from fastapi.testclient import TestClient
from sales_api.main import create_app


def test_health():
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ingest_and_approve_flow():
    client = TestClient(create_app())
    r = client.post(
        "/v1/leads/ingest",
        json={
            "email": "alex@acme.io",
            "first_name": "Alex",
            "company": "Acme Analytics",
            "employee_count": 120,
            "country": "US",
            "industry": "software",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "awaiting_approval"
    lead_id = data["lead_id"]

    detail = client.get(f"/v1/leads/{lead_id}")
    assert detail.status_code == 200
    assert detail.json()["run"]["draft"]["subject"]

    appr = client.post(f"/v1/leads/{lead_id}/approve", json={"editor_user_id": "rep-1"})
    assert appr.status_code == 200
    assert appr.json()["status"] == "approved"


def test_disqualified_lead():
    client = TestClient(create_app())
    r = client.post(
        "/v1/leads/ingest",
        json={
            "email": "bad@casino.io",
            "employee_count": 200,
            "country": "US",
            "industry": "gambling",
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "disqualified"
