from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from playbook_engine import PlaybookEngine
from tools_hubspot import MockHubSpotClient

from sales_api.draft_writer import generate_draft
from sales_api.store import (
    LeadRun,
    OutreachDraft,
    ToolRunRecord,
    get_flags,
    get_hubspot_client,
    monotonic_ms,
    record_tool_run,
)


@dataclass
class OrchestratorResult:
    qualified: bool
    status: str
    disqualify_reason: str | None = None
    enrichment: dict[str, Any] | None = None
    research: dict[str, Any] | None = None
    draft: OutreachDraft | None = None


class LeadOrchestrator:
    def __init__(self, engine: PlaybookEngine, hubspot: MockHubSpotClient | None = None) -> None:
        self.engine = engine
        self.hubspot = hubspot or get_hubspot_client()

    def _mock_enrich(self, company: str | None) -> dict[str, Any]:
        name = company or "Unknown Co"
        return {
            "company_name": name,
            "employee_count_est": "mid-market",
            "industry_guess": "B2B software",
            "provider": "mock_enrichment",
        }

    def _mock_research(self, company: str | None, first_name: str | None) -> dict[str, Any]:
        slug = (company or "company").lower().replace(" ", "")
        return {
            "persona": "VP Revenue Operations",
            "talking_points": [
                f"Recent growth in {company or 'your space'}",
                "Stack consolidation trend",
            ],
            "sources": [
                {"title": f"{company} about page", "url": f"https://{slug}.example/about"},
                {"title": "Industry report", "url": "https://example.com/report"},
            ],
        }

    def _build_draft(
        self,
        *,
        first_name: str | None,
        company: str | None,
        research: dict[str, Any],
        tone: str,
    ) -> OutreachDraft:
        name = first_name or "there"
        co = company or "your team"
        point = research.get("talking_points", ["your recent momentum"])[0]
        subject = f"Quick idea for {co}'s pipeline velocity"
        body = (
            f"Hi {name},\n\n"
            f"I noticed {point.lower()} — teams like {co} often struggle with slow "
            f"inbound follow-up while reps stay buried in CRM work.\n\n"
            f"We help RevOps automate qualify → research → draft with human approval "
            f"({tone} tone). Worth a 15-minute compare?\n\n"
            f"Best,\n[Your name]"
        )
        return OutreachDraft(subject=subject, body=body)

    def run(
        self,
        *,
        email: str,
        first_name: str | None,
        company: str | None,
        employee_count: int | None,
        country: str | None,
        industry: str | None,
        lead_run: LeadRun | None = None,
    ) -> OrchestratorResult:
        flags = get_flags()
        if flags.get("kill_switch"):
            return OrchestratorResult(
                qualified=False,
                status="failed",
                disqualify_reason="kill_switch",
            )

        icp = self.engine.evaluate_icp(
            employee_count=employee_count,
            country=country,
            industry=industry,
        )
        if not icp.allowed:
            return OrchestratorResult(
                qualified=False,
                status="disqualified",
                disqualify_reason=icp.message,
            )

        enrichment = self._mock_enrich(company)
        research = self._mock_research(company, first_name)
        sources = research.get("sources", [])
        cite = self.engine.evaluate_citations(sources_count=len(sources))
        if not cite.allowed:
            return OrchestratorResult(
                qualified=True,
                status="failed",
                disqualify_reason=cite.message,
                enrichment=enrichment,
                research=research,
            )

        template = self._build_draft(
            first_name=first_name,
            company=company,
            research=research,
            tone=self.engine.config.outreach.tone,
        )
        draft = generate_draft(
            first_name=first_name,
            company=company,
            research=research,
            tone=self.engine.config.outreach.tone,
            template_draft=template,
        )

        if lead_run is not None:
            t0 = time.perf_counter()
            record_tool_run(
                lead_run,
                ToolRunRecord(
                    tool_name="mock_enrich",
                    input_json={"company": company},
                    output_json=enrichment,
                    status="success",
                    latency_ms=monotonic_ms(t0),
                ),
            )
            record_tool_run(
                lead_run,
                ToolRunRecord(
                    tool_name="mock_research",
                    input_json={"company": company},
                    output_json=research,
                    status="success",
                    latency_ms=monotonic_ms(t0),
                ),
            )

        return OrchestratorResult(
            qualified=True,
            status="awaiting_approval",
            enrichment=enrichment,
            research=research,
            draft=draft,
        )

    def sync_crm_after_approval(
        self,
        *,
        lead_run_id: str,
        contact_id: str,
        draft: OutreachDraft,
        deal_id: str | None = None,
    ) -> list[ToolRunRecord]:
        flags = get_flags()
        shadow = flags.get("shadow_mode", True)
        crm_enabled = flags.get("crm_writes_enabled", False)
        dry_run = shadow or not crm_enabled
        stage_id = self.engine.config.pipeline.on_approve_first_touch_deal_stage_id
        records: list[ToolRunRecord] = []

        t0 = time.perf_counter()
        note_result = self.hubspot.create_note(
            contact_id=contact_id,
            body=f"Approved draft:\nSubject: {draft.subject}\n\n{draft.body}",
            idempotency_key=f"{lead_run_id}:note",
            dry_run=dry_run,
        )
        records.append(
            ToolRunRecord(
                tool_name="hubspot_create_note",
                input_json={"contact_id": contact_id, "dry_run": dry_run},
                output_json={
                    "ok": note_result.ok,
                    "external_id": note_result.external_id,
                    "detail": note_result.detail,
                },
                status="success" if note_result.ok else "error",
                idempotency_key=f"{lead_run_id}:note",
                latency_ms=monotonic_ms(t0),
            )
        )

        if deal_id:
            stage_decision = self.engine.evaluate_stage_change(approved=True, shadow_mode=shadow)
            if stage_decision.allowed or dry_run:
                stage_result = self.hubspot.update_deal_stage(
                    deal_id=deal_id,
                    stage_id=stage_id,
                    idempotency_key=f"{lead_run_id}:stage",
                    dry_run=dry_run,
                )
                records.append(
                    ToolRunRecord(
                        tool_name="hubspot_update_deal_stage",
                        input_json={"deal_id": deal_id, "stage_id": stage_id, "dry_run": dry_run},
                        output_json={
                            "ok": stage_result.ok,
                            "detail": stage_result.detail,
                        },
                        status="success" if stage_result.ok else "error",
                        idempotency_key=f"{lead_run_id}:stage",
                    )
                )
        return records
