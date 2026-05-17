from __future__ import annotations

import hashlib
import os
import uuid as uuid_std
from dataclasses import dataclass
from pathlib import Path, PurePath
from uuid import UUID

from fastapi import UploadFile
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.config import SettingsModel
from app.core.paths import assert_resolved_under_anchor, ensure_discipline_paths
from app.exceptions import DuplicateArtefactError, InvalidUploadExtensionError, NotFoundError, PayloadTooLargeError
from app.models.catalogue import CatalogueArtefact
from app.repositories import catalogue as catalogue_repo
from app.repositories import hierarchy as hier_repos


_EXT_TO_BUCKET: dict[str, str] = {
    "pdf": "documentos",
    "txt": "documentos",
    "docx": "documentos",
    "html": "web",
    "mhtml": "web",
    "mp4": "videos",
    "mp3": "audios",
    "wav": "audios",
    "m4a": "audios",
}


@dataclass(slots=True)
class PerFileReject:
    filename: str
    code: str
    message: str


def _normalized_extension(upload_name: str | None, allowed: set[str]) -> str:
    stem_name = PurePath(upload_name or "upload").name
    suf = PurePath(stem_name).suffix
    ext = suf.lower().lstrip(".")
    if not ext or ext not in allowed:
        raise InvalidUploadExtensionError(f"extension not permitted: '{ext}'")
    return ext


def _bucket(ext: str) -> str:
    b = _EXT_TO_BUCKET.get(ext)
    if b is None:
        raise InvalidUploadExtensionError(f"extension not classified: '{ext}'")
    return b


class IngestionService:
    def __init__(self, session: Session, settings: SettingsModel) -> None:
        self.session = session
        self._settings = settings

    async def ingest_upload(self, discipline_id: UUID, upload: UploadFile) -> CatalogueArtefact:
        allowed_ext = set(self._settings.allowed_extensions)
        display_name = PurePath(upload.filename or "upload").name
        display_name = display_name[:512]

        ext = _normalized_extension(upload.filename, allowed_ext)
        bucket_segment = _bucket(ext)

        discipline = hier_repos.get_discipline(self.session, discipline_id)
        if discipline is None:
            raise NotFoundError("Discipline not found")
        course = hier_repos.get_course(self.session, discipline.curso_id)
        if course is None:
            raise NotFoundError("Course not found")

        discipline_root = ensure_discipline_paths(course.slug, discipline.slug, self._settings.storage_root_abs)
        target_dir = discipline_root / "originais" / bucket_segment
        target_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = Path(target_dir) / f".ingest-{uuid_std.uuid4().hex}.part"
        stem = slugify(PurePath(display_name).stem, max_length=80) or "ficheiro"

        hasher = hashlib.sha256()
        total = 0
        chunk = self._settings.upload_chunk_bytes
        limit = self._settings.max_upload_bytes

        try:
            with tmp_path.open("xb") as out:
                while True:
                    block = await upload.read(chunk)
                    if not block:
                        break
                    total += len(block)
                    if total > limit:
                        raise PayloadTooLargeError("ficheiro excede max_upload_bytes")
                    hasher.update(block)
                    out.write(block)

            digest = hasher.hexdigest().lower()

            if catalogue_repo.exists_sha256(self.session, discipline_id, digest):
                raise DuplicateArtefactError("Ficheiro idêntico já existe nesta disciplina.")

            final_path = Path(target_dir) / f"{stem}-{digest[:16]}.{ext}"
            os.replace(str(tmp_path), str(final_path))

            assert_resolved_under_anchor(final_path, discipline_root)
            stored_rel = final_path.resolve().relative_to(discipline_root.resolve()).as_posix()

            row = CatalogueArtefact(
                discipline_id=discipline_id,
                sha256=digest,
                original_filename=display_name,
                stored_relative_path=stored_rel,
                bucket=bucket_segment,
                mime_type=(upload.content_type or "").split(";")[0].strip()[:256] or None,
                byte_size=total,
            )
            try:
                self.session.add(row)
                self.session.commit()
                self.session.refresh(row)
                return row
            except IntegrityError:
                self.session.rollback()
                final_path.unlink(missing_ok=True)
                raise DuplicateArtefactError("Ficheiro idêntico já existe nesta disciplina.") from None
        finally:
            tmp_path.unlink(missing_ok=True)


def artefact_public(artefact: CatalogueArtefact) -> dict[str, object]:
    """JSON-safe artefact envelope (never absolute filesystem paths)."""
    return {
        "id": str(artefact.id),
        "discipline_id": str(artefact.discipline_id),
        "sha256": artefact.sha256,
        "bucket": artefact.bucket,
        "stored_relative_path": artefact.stored_relative_path,
        "byte_size": artefact.byte_size,
        "original_filename": artefact.original_filename,
        "mime_type": artefact.mime_type,
    }


def reject_from_exc(filename: str, exc: BaseException) -> PerFileReject:
    if isinstance(exc, DuplicateArtefactError):
        return PerFileReject(filename, "duplicate", str(exc))
    if isinstance(exc, InvalidUploadExtensionError):
        return PerFileReject(filename, "validation", str(exc))
    if isinstance(exc, PayloadTooLargeError):
        return PerFileReject(filename, "too_large", str(exc))
    if isinstance(exc, NotFoundError):
        return PerFileReject(filename, "not_found", str(exc))
    return PerFileReject(filename, "error", str(exc))
