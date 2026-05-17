from __future__ import annotations

from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from typing import AsyncIterator

from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter

from app.exceptions import MergeLockBusyError
from app.services.processados_lock import MergeLock


def blank_pdf_bytes(page_width_pts: float) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=page_width_pts, height=792.0)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _seed_course_discipline(client: TestClient) -> tuple[str, str]:
    created = client.post("/api/cursos", json={"nome": "Farmacologia"})
    assert created.status_code == 201
    cid = created.json()["id"]
    resp = client.post("/api/disciplinas", params={"curso_id": cid}, json={"nome": "Toxicos"})
    assert resp.status_code == 201
    return cid, resp.json()["id"]


def _find_under_storage(tmp_path: Path, pattern: str) -> Path:
    matches = sorted((tmp_path / "storage").rglob(pattern))
    assert len(matches) >= 1, f"nothing matched {pattern!r} under {tmp_path}"
    return matches[0]


def test_merge_api_orders_pdf_pages_by_basename(client: TestClient, tmp_path: Path) -> None:
    _, disc_id = _seed_course_discipline(client)
    zebra = blank_pdf_bytes(333.3)
    alfa = blank_pdf_bytes(111.1)
    uploads = [
        ("files", ("zebra-sort.pdf", zebra, "application/pdf")),
        ("files", ("alfa-sort.pdf", alfa, "application/pdf")),
    ]
    ingest = client.post("/api/upload", data={"disciplina_id": disc_id}, files=uploads)
    assert ingest.status_code == 200, ingest.text

    merge = client.post(f"/api/disciplinas/{disc_id}/merge-pdfs")
    assert merge.status_code == 200, merge.text
    payload = merge.json()
    assert payload["ok"] is True
    assert payload["merged"]["stored_relative_path"] == "processados/pdfs/concatenado.pdf"
    assert payload["merged"]["page_count"] == 2
    assert payload["merged"]["source_basenames"][0].lower().startswith("alfa")

    merged_path = _find_under_storage(tmp_path, "concatenado.pdf")
    reader = PdfReader(str(merged_path))
    w0 = reader.pages[0].mediabox.width
    w1 = reader.pages[1].mediabox.width
    assert abs(float(w0) - 111.1) < 0.1
    assert abs(float(w1) - 333.3) < 0.1


def test_merge_no_pdf_returns_422(client: TestClient) -> None:
    _, disc_id = _seed_course_discipline(client)
    merge = client.post(f"/api/disciplinas/{disc_id}/merge-pdfs")
    assert merge.status_code == 422
    payload = merge.json()
    assert payload["ok"] is False
    assert isinstance(payload["diagnostics"], list)


def test_merge_truncated_original_surfaces_diagnostic(client: TestClient, tmp_path: Path) -> None:
    _, disc_id = _seed_course_discipline(client)
    uploads = [
        ("files", ("good.pdf", blank_pdf_bytes(200.0), "application/pdf")),
        ("files", ("broken.pdf", blank_pdf_bytes(400.0), "application/pdf")),
    ]
    ingest = client.post("/api/upload", data={"disciplina_id": disc_id}, files=uploads)
    assert ingest.status_code == 200, ingest.text

    broken_pdf = _find_under_storage(tmp_path, "broken*.pdf")
    broken_pdf.write_bytes(broken_pdf.read_bytes()[:60])

    merge = client.post(f"/api/disciplinas/{disc_id}/merge-pdfs")
    assert merge.status_code == 422
    detail = merge.json()
    assert detail["ok"] is False
    diag = detail["diagnostics"]
    assert any(d.get("code") == "corrupt_pdf" for d in diag)


class BusyPdfMergeLock(MergeLock):
    @asynccontextmanager
    async def for_discipline_id(self, *_a: object, **_k: object) -> AsyncIterator[None]:
        raise MergeLockBusyError("Operação ocupada (teste de bloqueio).")
        yield  # pragma: no cover


def test_merge_lock_busy_returns_409(client: TestClient) -> None:
    _, disc_id = _seed_course_discipline(client)
    ingest = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("solo.pdf", blank_pdf_bytes(55.5), "application/pdf"))],
    )
    assert ingest.status_code == 200

    client.app.state.pdf_merge_lock = BusyPdfMergeLock()
    merge = client.post(f"/api/disciplinas/{disc_id}/merge-pdfs")
    assert merge.status_code == 409
