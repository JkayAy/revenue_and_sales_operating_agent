from fastapi.testclient import TestClient
from sales_api.config import settings
from sales_api.main import create_app


def test_rate_limit_returns_429(monkeypatch):
    import sales_api.rate_limit as rl

    rl._hits.clear()
    monkeypatch.setattr(settings, "rate_limit_per_minute", 2)
    client = TestClient(create_app())
    body = {
        "email": "a@test.io",
        "employee_count": 100,
        "country": "US",
        "industry": "software",
    }
    assert client.post("/v1/leads/ingest", json=body).status_code == 200
    body["email"] = "b@test.io"
    assert client.post("/v1/leads/ingest", json=body).status_code == 200
    body["email"] = "c@test.io"
    r = client.post("/v1/leads/ingest", json=body)
    assert r.status_code == 429


def test_trace_id_header():
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("X-Trace-Id")
