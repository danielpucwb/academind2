from __future__ import annotations

from uuid import uuid4

MINIMAL_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"


def _seed_course_discipline(client) -> tuple[str, str]:
    created = client.post("/api/cursos", json={"nome": "Catalogue Course"})
    assert created.status_code == 201
    cid = created.json()["id"]
    resp = client.post("/api/disciplinas", params={"curso_id": cid}, json={"nome": "Catalogue Disc"})
    assert resp.status_code == 201
    return cid, resp.json()["id"]


def test_api_artefacts_round_trip_list_upload_delete(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    empty = client.get(f"/api/disciplinas/{disc_id}/artefacts")
    assert empty.status_code == 200
    assert empty.json()["artefacts"] == []

    up = client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("notes.pdf", MINIMAL_PDF, "application/pdf"))],
    )
    assert up.status_code == 200, up.text
    aid = up.json()["created"][0]["id"]

    listed = client.get(f"/api/disciplinas/{disc_id}/artefacts")
    assert listed.status_code == 200
    arts = listed.json()["artefacts"]
    assert len(arts) == 1
    assert arts[0]["id"] == aid
    prefix = arts[0].get("sha256_prefix")
    assert isinstance(prefix, str) and len(prefix) == 12

    deleted = client.delete(f"/api/disciplinas/{disc_id}/artefacts/{aid}")
    assert deleted.status_code == 204

    again = client.get(f"/api/disciplinas/{disc_id}/artefacts")
    assert again.json()["artefacts"] == []


def test_api_artefacts_unknown_discipline_404(client) -> None:
    fake = uuid4()
    r = client.get(f"/api/disciplinas/{fake}/artefacts")
    assert r.status_code == 404


def test_originals_rows_empty_message(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    r = client.get(f"/ui/cursos/{cid}/disciplinas/{disc_id}/originals-rows")
    assert r.status_code == 200
    assert "Sem ficheiros catalogados nesta disciplina." in r.text


def test_originals_rows_lists_upload_after_api_upload(client) -> None:
    cid, disc_id = _seed_course_discipline(client)
    client.post(
        "/api/upload",
        data={"disciplina_id": disc_id},
        files=[("files", ("lista.pdf", MINIMAL_PDF, "application/pdf"))],
    )
    r = client.get(f"/ui/cursos/{cid}/disciplinas/{disc_id}/originals-rows")
    assert r.status_code == 200
    assert "lista.pdf" in r.text
    assert "Eliminar" in r.text
