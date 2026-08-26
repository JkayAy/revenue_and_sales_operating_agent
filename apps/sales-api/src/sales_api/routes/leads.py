from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from sales_api.lead_service import approve_lead, process_ingest, reject_lead
from sales_api.store import get_lead, list_leads

router = APIRouter(prefix="/leads", tags=["leads"])


class IngestBody(BaseModel):
    email: EmailStr
    first_name: str | None = None
    company: str | None = None
    employee_count: int | None = Field(default=None, ge=0)
    country: str | None = None
    industry: str | None = None
    hubspot_contact_id: str | None = None


class ApproveBody(BaseModel):
    editor_user_id: str = "demo-rep"
    edited_subject: str | None = None
    edited_body: str | None = None


class RejectBody(BaseModel):
    actor_user_id: str = "demo-rep"
    reason: str


def _serialize_lead(lead: Any, *, detail: bool = False) -> dict[str, Any]:
    run = lead.runs[0] if lead.runs else None
    base = {
        "lead_id": lead.id,
        "email": lead.email,
        "first_name": lead.first_name,
        "company": lead.company,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
    }
    if run:
        base["run_id"] = run.id
        base["qualified"] = run.qualified
    if detail and run:
        base["run"] = {
            "id": run.id,
            "status": run.status,
            "qualified": run.qualified,
            "disqualify_reason": run.disqualify_reason,
            "enrichment": run.enrichment,
            "research": run.research,
            "draft": (
                {"subject": run.draft.subject, "body": run.draft.body, "version": run.draft.version}
                if run.draft
                else None
            ),
            "tool_runs": [
                {
                    "tool_name": t.tool_name,
                    "status": t.status,
                    "idempotency_key": t.idempotency_key,
                }
                for t in run.tool_runs
            ],
            "shadow_mode": run.shadow_mode,
        }
    return base


@router.post("/ingest")
def ingest(body: IngestBody, request: Request) -> dict[str, Any]:
    if request.app.state.flags.get("kill_switch"):
        raise HTTPException(status_code=503, detail="kill_switch enabled")
    try:
        lead, run = process_ingest(
            request.app.state.playbook_engine,
            request.app.state.orchestrator,
            body.model_dump(),
        )
    except ValueError as e:
        if str(e) == "opt_out":
            raise HTTPException(status_code=403, detail="opt_out") from e
        raise
    return {
        "lead_id": lead.id,
        "run_id": run.id,
        "status": lead.status,
        "qualified": run.qualified,
    }


@router.get("")
def leads_list(status: str | None = None) -> dict[str, Any]:
        items = [_serialize_lead(lead) for lead in list_leads(status=status)]
    return {"leads": items}


@router.get("/{lead_id}")
def lead_detail(lead_id: str) -> dict[str, Any]:
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="not_found")
    return _serialize_lead(lead, detail=True)


@router.post("/{lead_id}/approve")
def approve(lead_id: str, body: ApproveBody, request: Request) -> dict[str, Any]:
    try:
        lead = approve_lead(
            request.app.state.playbook_engine,
            request.app.state.orchestrator,
            lead_id,
            actor_user_id=body.editor_user_id,
            edited_subject=body.edited_subject,
            edited_body=body.edited_body,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail="not_found") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _serialize_lead(lead, detail=True)


@router.post("/{lead_id}/reject")
def reject(lead_id: str, body: RejectBody, request: Request) -> dict[str, Any]:
    try:
        lead = reject_lead(
            lead_id,
            actor_user_id=body.actor_user_id,
            reason=body.reason,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail="not_found") from e
    return _serialize_lead(lead, detail=True)
