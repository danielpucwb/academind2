from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4


def _seed_course_discipline(client) -> tuple[str, str]:
    created = client.post("/api/cursos", json={"nome": "Farmacologia"})
    assert created.status_code == 201
    cid = created.json()["id"]
    resp = client.post("/api/disciplinas", params={"curso_id": cid}, json={"nome": "Toxicos"})
    assert resp.status_code == 201
    return cid, resp.json()["id"]


MINIMAL_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"


def test_upload_pdf_writes_under_originais_documentos(client, tmp_path: Path) -> None:
    _, disc_id = _seed_course_discipline(client)
    r = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("notas.pdf", MINIMAL_PDF, "application/pdf"))],
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "correlation_id" in data
    UUID(str(data["correlation_id"]))  # raises if malformed
    assert len(data["created"]) == 1
    stored = data["created"][0]["stored_relative_path"]
    assert stored.startswith("originais/documentos/")

    # Verify bytes landed under temp project layout
    root = tmp_path
    storage = root / "storage" / "cursos"
    matches = list(storage.rglob("*.pdf"))
    assert len(matches) == 1
    assert matches[0].read_bytes() == MINIMAL_PDF


def test_duplicate_upload_returns_409(client) -> None:
    _, disc_id = _seed_course_discipline(client)
    spec = ("dup.pdf", MINIMAL_PDF, "application/pdf")
    files = [("files", spec)]
    first = client.post("/api/upload", data={"disciplina_id": disc_id}, files=files)
    assert first.status_code == 200

    dup = client.post("/api/upload", data={"disciplina_id": disc_id}, files=files)
    assert dup.status_code == 409
    payload = dup.json()
    detail = payload.get("detail") if isinstance(payload, dict) else None
    assert isinstance(detail, dict) and "duplicates" in detail


def test_rejected_extension_resolves_to_422(client) -> None:
    _, disc_id = _seed_course_discipline(client)
    r = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("evil.exe", b"MZ\xff", "application/octet-stream"))],
    )
    assert r.status_code == 422
    detail = r.json().get("detail", {})
    assert "rejected" in detail


def test_unknown_discipline_returns_404(client) -> None:
    fake = uuid4()
    r = client.post(
        "/api/upload",
        data={"disciplina_id": str(fake)},
        files=[("files", ("a.pdf", MINIMAL_PDF, "application/pdf"))],
    )
    assert r.status_code == 404
