from __future__ import annotations


def test_dashboard_renders(client) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "acadeMIND" in r.text


def test_health_json_keys(client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) >= {"status", "sqlite", "ffmpeg", "whisper_cuda"}
    assert isinstance(data["sqlite"], bool)
    assert isinstance(data["ffmpeg"], bool)
    assert data["status"] in ("ok", "degraded", "error")


def test_cursos_rest_flow(client) -> None:
    assert client.get("/api/cursos").json() == []

    creation = client.post("/api/cursos", json={"nome": "Medicina"})
    assert creation.status_code == 201
    body = creation.json()
    assert body["nome"] == "Medicina"
    cid = body["id"]

    listed = client.get("/api/cursos").json()
    assert len(listed) == 1

    discs = client.get("/api/disciplinas", params={"curso_id": cid}).json()
    assert discs == []

    d = client.post("/api/disciplinas", params={"curso_id": cid}, json={"nome": "Anatomia"})
    assert d.status_code == 201
    did = d.json()["id"]

    discs2 = client.get("/api/disciplinas", params={"curso_id": cid}).json()
    assert len(discs2) == 1

    dash = client.get(f"/cursos/{cid}")
    assert dash.status_code == 200

    det = client.get(f"/cursos/{cid}/disciplinas/{did}")
    assert det.status_code == 200
    assert "Originais" in det.text
    assert "Processados" in det.text
    assert "Processamento" in det.text
