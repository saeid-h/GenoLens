from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_samples_list():
    res = client.get("/api/samples")
    assert res.status_code == 200
    body = res.json()
    assert "samples" in body


def test_overview_when_samples_exist():
    samples = client.get("/api/samples").json()["samples"]
    if not samples:
        return
    sid = samples[0]["id"]
    res = client.get(f"/api/samples/{sid}/overview")
    assert res.status_code == 200
    assert "count" in res.json()


def test_reference_status():
    res = client.get("/api/reference/status")
    assert res.status_code == 200
    body = res.json()
    assert "prs" in body
    assert "aadr" in body
