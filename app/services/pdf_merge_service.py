from __future__ import annotations

import asyncio
import os
import uuid as uuid_std
from dataclasses import dataclass
from pathlib import Path, PurePath, PurePosixPath
from uuid import UUID

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from sqlmodel import Session

from app.core import paths as path_helpers
from app.core.config import SettingsModel
from app.exceptions import NothingToMergeError, PdfMergeRejectedError
from app.models.catalogue import CatalogueArtefact
from app.repositories import catalogue as catalogue_repo
from app.services.hierarchy_resolver import resolve_discipline_paths
from app.services.processados_lock import MergeLock


@dataclass(slots=True, frozen=True)
class PdfDiag:
    code: str
    message_pt: str
    filename: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"code": self.code, "message_pt": self.message_pt, "filename": self.filename}


@dataclass(slots=True, frozen=True)
class PdfMergeOutcome:
    stored_relative_path: str
    page_count: int
    source_basenames: list[str]
    diagnostics: list[PdfDiag]

    def to_json(self) -> dict[str, object]:
        return {
            "stored_relative_path": self.stored_relative_path,
            "page_count": self.page_count,
            "source_basenames": list(self.source_basenames),
        }


def _is_catalogue_pdf(ar: CatalogueArtefact) -> bool:
    if ar.bucket != "documentos":
        return False
    parts = PurePosixPath(ar.stored_relative_path).parts
    if len(parts) < 3:
        return False
    return parts[:2] == ("originais", "documentos") and parts[-1].lower().endswith(".pdf")


def _sort_key(ar: CatalogueArtefact) -> tuple[str, str]:
    base = PurePath(ar.original_filename).name
    return (base.lower(), ar.original_filename)


class PdfMergeService:
    def __init__(
        self,
        session: Session,
        settings: SettingsModel,
        merge_lock: MergeLock | None = None,
    ) -> None:
        self._session = session
        self._settings = settings
        self._lock = merge_lock or MergeLock()

    def _gather_inputs(self, discipline_id: UUID) -> list[CatalogueArtefact]:
        rows = catalogue_repo.list_for_discipline(self._session, discipline_id)
        chosen = [r for r in rows if _is_catalogue_pdf(r)]
        chosen.sort(key=_sort_key)
        return chosen

    def _merge_locked(self, discipline_id: UUID, discipline_root: Path) -> PdfMergeOutcome:
        candidates = self._gather_inputs(discipline_id)
        if not candidates:
            raise NothingToMergeError("Não há PDFs em originais/documentos elegíveis para fundir.")

        diagnostics: list[PdfDiag] = []
        writer = PdfWriter()
        merged_sources: list[str] = []

        for art in candidates:
            basename = PurePath(art.original_filename).name
            disk_path = (discipline_root / art.stored_relative_path).resolve()
            path_helpers.assert_resolved_under_anchor(disk_path, discipline_root)
            try:
                reader = PdfReader(str(disk_path))
            except PdfReadError:
                diagnostics.append(
                    PdfDiag(
                        code="corrupt_pdf",
                        message_pt="Este PDF parece incompleto ou corrompido e não pode ser lido.",
                        filename=basename,
                    )
                )
                raise PdfMergeRejectedError(
                    "Não foi possível fundir os PDFs (ficheiros ilegíveis ou corrompidos).",
                    [d.as_dict() for d in diagnostics],
                ) from None

            if reader.is_encrypted:
                diagnostics.append(
                    PdfDiag(
                        code="encrypted_pdf",
                        message_pt="Este PDF está encriptado; remova a senha antes de fundir.",
                        filename=basename,
                    )
                )
                raise PdfMergeRejectedError(
                    "Não foi possível fundir os PDFs (existe pelo menos um PDF encriptado).",
                    [d.as_dict() for d in diagnostics],
                )

            n_pages = len(reader.pages)
            if n_pages == 0:
                diagnostics.append(
                    PdfDiag(
                        code="empty_pdf",
                        message_pt="Este PDF não contém páginas e foi ignorado.",
                        filename=basename,
                    )
                )
                continue

            try:
                writer.append(reader)
            except (PdfReadError, OSError, ValueError) as exc:
                diagnostics.append(
                    PdfDiag(
                        code="pdf_append_failed",
                        message_pt=f"Erro ao anexar páginas ({type(exc).__name__}). Verifique integridade.",
                        filename=basename,
                    )
                )
                raise PdfMergeRejectedError(
                    "Não foi possível fundir os PDFs (falhou ao concatenar páginas).",
                    [d.as_dict() for d in diagnostics],
                ) from exc

            merged_sources.append(basename)

        if len(writer.pages) == 0:
            diagnostics.append(
                PdfDiag(code="nothing_to_concat", message_pt="Nenhuma página restou para escrever após filtros.")
            )
            raise PdfMergeRejectedError(
                "Não foi possível produzir o PDF fundido porque não sobrou conteúdo válido.",
                [d.as_dict() for d in diagnostics],
            )

        out_dir = discipline_root / "processados" / "pdfs"
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp_out = out_dir / f"concatenado.pdf.tmp-{uuid_std.uuid4().hex}"
        final_out = out_dir / "concatenado.pdf"

        try:
            with tmp_out.open("wb") as tmp_f:
                writer.write(tmp_f)
            os.replace(tmp_out, final_out)
        finally:
            tmp_out.unlink(missing_ok=True)

        path_helpers.assert_resolved_under_anchor(final_out, discipline_root)
        rel_out = final_out.resolve().relative_to(discipline_root.resolve()).as_posix()

        return PdfMergeOutcome(
            stored_relative_path=rel_out,
            page_count=len(writer.pages),
            source_basenames=merged_sources,
            diagnostics=diagnostics,
        )

    async def merge_discipline_pdf(self, discipline_id: UUID) -> PdfMergeOutcome:
        _course, _discipline, discipline_root = resolve_discipline_paths(
            self._session,
            discipline_id,
            self._settings,
        )
        async with self._lock.for_discipline_id(discipline_id, discipline_root):
            return await asyncio.to_thread(self._merge_locked, discipline_id, discipline_root)
