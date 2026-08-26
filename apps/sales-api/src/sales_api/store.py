from __future__ import annotations

import time
import uuid as uuid_lib
from typing import Any

from tools_hubspot import LiveHubSpotClient, MockHubSpotClient

from sales_api import postgres_store as pg
from sales_api.config import settings
from sales_api.database import db_enabled, persist_flag
from sales_api.hubspot_auth import get_effective_access_token
from sales_api.models import Lead, LeadRun, OutreachDraft, ToolRunRecord

# Re-export for callers
__all__ = [
    "Lead",
    "LeadRun",
    "OutreachDraft",
    "ToolRunRecord",
    "new_id",
    "get_flags",
    "set_flag",
    "is_opt_out",
    "add_opt_out",
    "get_hubspot_client",
    "find_lead_by_email",
    "save_lead",
    "get_lead",
    "list_leads",
    "record_tool_run",
    "record_approval",
    "bump_metric",
    "get_metrics",
    "monotonic_ms",
    "sync_flags_from_db",
]

_leads: dict[str, Lead] = {}
_email_index: dict[str, str] = {}
_flags: dict[str, bool] = {
    "shadow_mode": True,
    "crm_writes_enabled": False,
    "kill_switch": False,
}
_opt_out_emails: set[str] = set()
_hubspot = MockHubSpotClient()
_metrics: dict[str, float] = {
    "ingest_count": 0,
    "draft_ready_count": 0,
    "approval_count": 0,
    "reject_count": 0,
}


def new_id() -> str:
    return str(uuid_lib.uuid4())


def get_flags() -> dict[str, bool]:
    return dict(_flags)


def set_flag(key: str, enabled: bool) -> None:
    _flags[key] = enabled
    if db_enabled():
        persist_flag(key, enabled)


def is_opt_out(email: str) -> bool:
    if db_enabled():
        return pg.pg_is_opt_out(email)
    return email.lower() in _opt_out_emails


def add_opt_out(email: str) -> None:
    _opt_out_emails.add(email.lower())


def get_hubspot_client() -> MockHubSpotClient | LiveHubSpotClient:
    if settings.mock_tools:
        return _hubspot
    token = get_effective_access_token()
    if token:
        return LiveHubSpotClient(token)
    return _hubspot


def find_lead_by_email(email: str) -> Lead | None:
    if db_enabled():
        return pg.pg_find_lead_by_email(email)
    lid = _email_index.get(email.lower())
    return _leads.get(lid) if lid else None


def save_lead(lead: Lead) -> None:
    if db_enabled():
        pg.pg_save_lead(lead)
        return
    _leads[lead.id] = lead
    _email_index[lead.email.lower()] = lead.id


def get_lead(lead_id: str) -> Lead | None:
    if db_enabled():
        return pg.pg_get_lead(lead_id)
    return _leads.get(lead_id)


def list_leads(status: str | None = None) -> list[Lead]:
    if db_enabled():
        return pg.pg_list_leads(status=status)
    items = list(_leads.values())
    items.sort(key=lambda x: x.created_at, reverse=True)
    if status:
            items = [lead for lead in items if lead.status == status]
    return items


def record_tool_run(run: LeadRun, record: ToolRunRecord) -> None:
    run.tool_runs.append(record)


def record_approval(
    lead_run_id: str,
    decision: str,
    actor_user_id: str,
    reason: str | None = None,
) -> None:
    if db_enabled():
        pg.pg_insert_approval(lead_run_id, decision, actor_user_id, reason)


def bump_metric(name: str, delta: float = 1) -> None:
    if db_enabled():
        return
    _metrics[name] = _metrics.get(name, 0) + delta


def get_metrics() -> dict[str, Any]:
    if db_enabled():
        return pg.pg_get_metrics()
    drafts = [lead for lead in _leads.values() if lead.status == "awaiting_approval"]  
    return {
        **_metrics,
        "queue_depth": len(drafts),
        "total_leads": len(_leads),
        "storage": "memory",
    }


def monotonic_ms(start: float) -> int:
    return max(0, int((time.perf_counter() - start) * 1000))


def sync_flags_from_db(db_flags: dict[str, bool]) -> None:
    for key, enabled in db_flags.items():
        _flags[key] = enabled
