from __future__ import annotations

MINIMAL_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
HTMX = {"HX-Request": "true"}


def _seed_course_discipline(client) -> tuple[str, str]:
    created = client.post("/api/cursos", json={"nome": "HTMX Upload Course"})
    assert created.status_code == 201
    cid = created.json()["id"]
    resp = client.post("/api/disciplinas", params={"curso_id": cid}, json={"nome": "HTMX Disc"})
    assert resp.status_code == 201
    return cid, resp.json()["id"]


def test_htmx_upload_success_oob_feedback_and_list_swap(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    r = client.post(
        f"/ui/cursos/{cid}/disciplinas/{disc_id}/upload-htmx",
        data={"curso_id": cid},
        files=[("files", ("panel.pdf", MINIMAL_PDF, "application/pdf"))],
        headers=HTMX,
    )
    assert r.status_code == 200, r.text
    body = r.text
    assert "hx-swap-oob" in body
    assert "upload-feedback-slot" in body
    assert "originals-list-root" in body
    assert "Ingestão concluída" in body
    assert "panel.pdf" in body


def test_htmx_upload_duplicate_oob(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    spec = ("dup.pdf", MINIMAL_PDF, "application/pdf")
    first = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", spec)],
    )
    assert first.status_code == 200
    dup = client.post(
        f"/ui/cursos/{cid}/disciplinas/{disc_id}/upload-htmx",
        data={"curso_id": cid},
        files=[("files", spec)],
        headers=HTMX,
    )
    assert dup.status_code == 200, dup.text
    assert "hx-swap-oob" in dup.text
    assert "dup.pdf" in dup.text


def test_htmx_artefact_excluir_returns_updated_partial(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    up = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("remove-me.pdf", MINIMAL_PDF, "application/pdf"))],
    )
    assert up.status_code == 200
    aid = up.json()["created"][0]["id"]

    cleared = client.post(
        f"/ui/cursos/{cid}/disciplinas/{disc_id}/artefact-excluir",
        data={"curso_id": cid, "artefact_id": aid},
    )
    assert cleared.status_code == 200
    assert "Sem ficheiros catalogados nesta disciplina." in cleared.text
