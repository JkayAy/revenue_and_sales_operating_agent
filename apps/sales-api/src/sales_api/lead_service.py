from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from playbook_engine import PlaybookEngine

from sales_api.observability import log_event
from sales_api.orchestrator import LeadOrchestrator
from sales_api.store import (
    Lead,
    LeadRun,
    bump_metric,
    find_lead_by_email,
    get_flags,
    get_lead,
    is_opt_out,
    new_id,
    record_approval,
    save_lead,
)

def process_ingest(
    engine: PlaybookEngine,
    orch: LeadOrchestrator,
    payload: dict[str, Any],
) -> tuple[Lead, LeadRun]:
    email = str(payload["email"]).strip().lower()
    if is_opt_out(email):
        lead = find_lead_by_email(email) or Lead(id=new_id(), email=email, status="blocked")
        lead.status = "blocked"
        save_lead(lead)
        raise ValueError("opt_out")

    existing = find_lead_by_email(email)
    if existing:
        lead = existing
    else:
        lead = Lead(
            id=new_id(),
            email=email,
            first_name=payload.get("first_name"),
            company=payload.get("company"),
            employee_count=payload.get("employee_count"),
            country=payload.get("country"),
            industry=payload.get("industry"),
            hubspot_contact_id=payload.get("hubspot_contact_id"),
        )

    lead.status = "processing"
    run = LeadRun(id=new_id(), lead_id=lead.id, shadow_mode=get_flags().get("shadow_mode", True))
    lead.runs.insert(0, run)
    save_lead(lead)
    bump_metric("ingest_count")

    result = orch.run(
        email=email,
        first_name=lead.first_name,
        company=lead.company,
        employee_count=lead.employee_count,
        country=lead.country,
        industry=lead.industry,
        lead_run=run,
    )

    run.qualified = result.qualified
    run.disqualify_reason = result.disqualify_reason
    run.enrichment = result.enrichment or {}
    run.research = result.research or {}
    run.draft = result.draft
    run.status = result.status
    run.completed_at = datetime.now(UTC)
    lead.status = result.status

    if result.status == "awaiting_approval":
        bump_metric("draft_ready_count")

    save_lead(lead)
    log_event(
        "lead.ingest_complete",
        lead_id=lead.id,
        run_id=run.id,
        status=lead.status,
        email=email,
    )
    return lead, run


def approve_lead(
    engine: PlaybookEngine,
    orch: LeadOrchestrator,
    lead_id: str,
    *,
    actor_user_id: str,
    edited_subject: str | None = None,
    edited_body: str | None = None,
) -> Lead:
    lead = get_lead(lead_id)
    if not lead or not lead.runs:
        raise KeyError("lead_not_found")
    run = lead.runs[0]
    if run.status != "awaiting_approval" or not run.draft:
        raise ValueError("not_awaiting_approval")

    draft = run.draft
    if edited_subject:
        draft.subject = edited_subject
    if edited_body:
        draft.body = edited_body

    contact_id = lead.hubspot_contact_id or f"mock-{lead.id[:8]}"
    crm_records = orch.sync_crm_after_approval(
        lead_run_id=run.id,
        contact_id=contact_id,
        draft=draft,
        deal_id=payload_deal_id(lead),
    )
    run.tool_runs.extend(crm_records)
    run.status = "approved"
    lead.status = "approved"
    record_approval(run.id, "approved", actor_user_id)
    bump_metric("approval_count")
    save_lead(lead)
    return lead


def reject_lead(lead_id: str, *, actor_user_id: str, reason: str) -> Lead:
    lead = get_lead(lead_id)
    if not lead or not lead.runs:
        raise KeyError("lead_not_found")
    run = lead.runs[0]
    run.status = "rejected"
    run.disqualify_reason = reason
    lead.status = "rejected"
    record_approval(run.id, "rejected", actor_user_id, reason)
    bump_metric("reject_count")
    save_lead(lead)
    return lead


def payload_deal_id(lead: Lead) -> str | None:
    return f"deal-{lead.id[:8]}"
