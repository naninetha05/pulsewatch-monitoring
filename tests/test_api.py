from app.config import settings


def _create(client, name="api", url="https://example.com"):
    return client.post("/api/v1/monitors", json={"name": name, "target_url": url})


def test_health_and_ready(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_monitor_crud(client):
    r = _create(client)
    assert r.status_code == 201
    mid = r.json()["id"]
    assert client.get(f"/api/v1/monitors/{mid}").json()["name"] == "api"
    r = client.patch(f"/api/v1/monitors/{mid}", json={"interval_seconds": 30})
    assert r.json()["interval_seconds"] == 30
    assert len(client.get("/api/v1/monitors").json()) == 1
    assert client.delete(f"/api/v1/monitors/{mid}").status_code == 204
    assert client.get(f"/api/v1/monitors/{mid}").status_code == 404


def test_duplicate_name_rejected(client):
    _create(client)
    assert _create(client).status_code == 409


def test_validation(client):
    assert _create(client, url="not-a-url").status_code == 422
    r = client.post("/api/v1/monitors", json={"name": "x", "target_url": "https://a.io", "interval_seconds": 1})
    assert r.status_code == 422


def test_metrics_and_alerts(client):
    mid = _create(client).json()["id"]
    ok = client.post(f"/api/v1/monitors/{mid}/metrics", json={"latency_ms": 50, "status_code": 200})
    assert ok.status_code == 201 and ok.json()["up"] is True
    client.post(f"/api/v1/monitors/{mid}/metrics", json={"latency_ms": 5000, "status_code": 200})
    down = client.post(f"/api/v1/monitors/{mid}/metrics", json={"latency_ms": 10, "status_code": 503})
    assert down.json()["up"] is False
    assert len(client.get(f"/api/v1/monitors/{mid}/metrics").json()) == 3
    severities = sorted(a["severity"] for a in client.get("/api/v1/alerts").json())
    assert severities == ["critical", "warning"]
    body = client.get("/metrics").text
    assert "pulsewatch_monitors_total 1" in body
    assert "pulsewatch_open_alerts 2" in body


def test_metrics_unknown_monitor(client):
    assert client.post("/api/v1/monitors/999/metrics", json={"latency_ms": 1, "status_code": 200}).status_code == 404


def test_api_key_enforced(client, monkeypatch):
    monkeypatch.setattr(settings, "api_key", "s3cret")
    assert client.get("/api/v1/monitors").status_code == 401
    assert client.get("/api/v1/monitors", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/api/v1/monitors", headers={"X-API-Key": "s3cret"}).status_code == 200
    assert client.get("/health").status_code == 200
