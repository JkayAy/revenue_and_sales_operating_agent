import os

import pytest
from fastapi.testclient import TestClient

from sales_api.config import settings
from sales_api.main import create_app


@pytest.mark.skipif(not os.environ.get("INTEGRATION_DB"), reason="set INTEGRATION_DB=1")
def test_postgres_ingest_persists():
    assert settings.database_url, "DATABASE_URL required for integration test"
    client = TestClient(create_app())
    email = f"pgtest+{os.getpid()}@acme.io"
    r = client.post(
        "/v1/leads/ingest",
        json={
            "email": email,
            "first_name": "Pg",
            "company": "Acme",
            "employee_count": 100,
            "country": "US",
            "industry": "software",
        },
    )
    assert r.status_code == 200
    lead_id = r.json()["lead_id"]

    r2 = client.get(f"/v1/leads/{lead_id}")
    assert r2.status_code == 200
    assert r2.json()["run"]["draft"]["subject"]

    metrics = client.get("/v1/admin/metrics").json()
    assert metrics.get("storage") == "postgres"
    assert metrics["total_leads"] >= 1
