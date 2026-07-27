from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class OutreachDraft:
    subject: str
    body: str
    version: int = 1


@dataclass
class ToolRunRecord:
    tool_name: str
    input_json: dict[str, Any]
    output_json: dict[str, Any] | None
    status: str
    idempotency_key: str | None = None
    latency_ms: int | None = None


@dataclass
class LeadRun:
    id: str
    lead_id: str
    status: str = "queued"
    qualified: bool | None = None
    disqualify_reason: str | None = None
    enrichment: dict[str, Any] = field(default_factory=dict)
    research: dict[str, Any] = field(default_factory=dict)
    draft: OutreachDraft | None = None
    tool_runs: list[ToolRunRecord] = field(default_factory=list)
    shadow_mode: bool = True
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    error_code: str | None = None


@dataclass
class Lead:
    id: str
    email: str
    first_name: str | None = None
    company: str | None = None
    employee_count: int | None = None
    country: str | None = None
    industry: str | None = None
    hubspot_contact_id: str | None = None
    status: str = "new"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    runs: list[LeadRun] = field(default_factory=list)
