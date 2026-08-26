"""End-to-end: ingest → qualify → enrich → research → draft → queue → approve."""

from fastapi.testclient import TestClient
from sales_api.main import create_app

INGEST = {
    "email": "core-loop@acme.io",
    "first_name": "Core",
    "company": "Acme Analytics",
    "employee_count": 120,
    "country": "US",
    "industry": "software",
}


def test_core_loop_ingest_qualify_enrich_draft_approve():
    client = TestClient(create_app())

    ingest = client.post("/v1/leads/ingest", json=INGEST)
    assert ingest.status_code == 200
    body = ingest.json()
    assert body["status"] == "awaiting_approval"
    assert body["qualified"] is True
    lead_id = body["lead_id"]

    queue = client.get("/v1/leads", params={"status": "awaiting_approval"})
    assert queue.status_code == 200
    assert lead_id in {item["lead_id"] for item in queue.json()["leads"]}

    detail = client.get(f"/v1/leads/{lead_id}").json()
    run = detail["run"]
    assert run["qualified"] is True
    assert run["enrichment"]["provider"] == "mock_enrichment"
    assert len(run["research"]["sources"]) >= 1
    assert run["draft"]["subject"]
    assert run["draft"]["body"]
    assert run["shadow_mode"] is True

    tool_names = {t["tool_name"] for t in run["tool_runs"]}
    assert {"mock_enrich", "mock_research"} <= tool_names

    approve = client.post(
        f"/v1/leads/{lead_id}/approve",
        json={"editor_user_id": "rep-e2e"},
    )
    assert approve.status_code == 200
    approved = approve.json()
    assert approved["status"] == "approved"

    crm_tools = {t["tool_name"] for t in approved["run"]["tool_runs"]}
    assert "hubspot_create_note" in crm_tools
    assert "hubspot_update_deal_stage" in crm_tools

    metrics = client.get("/v1/admin/metrics").json()
    assert metrics["draft_ready_count"] >= 1
    assert metrics["approval_count"] >= 1
