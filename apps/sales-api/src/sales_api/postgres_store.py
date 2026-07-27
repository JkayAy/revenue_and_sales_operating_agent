from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg.types.json import Json

from sales_api.config import settings
from sales_api.database import pg_dsn
from sales_api.models import Lead, LeadRun, OutreachDraft, ToolRunRecord


def _org_id() -> str:
    return settings.default_org_id


def _row_to_lead(row: tuple, runs: list[LeadRun]) -> Lead:
    return Lead(
        id=str(row[0]),
        email=row[1],
        first_name=row[2],
        company=row[3],
        employee_count=row[4],
        country=row[5],
        industry=row[6],
        hubspot_contact_id=row[7],
        status=row[8],
        created_at=row[9],
        runs=runs,
    )


def _fetch_runs_for_lead(conn: Any, lead_id: str, limit: int = 5) -> list[LeadRun]:
    runs: list[LeadRun] = []
    run_rows = conn.execute(
        """
        SELECT id, lead_id, status, qualified, disqualify_reason,
               enrichment_json, research_json, error_code, shadow_mode,
               started_at, completed_at
        FROM lead_runs
        WHERE lead_id = %s
        ORDER BY started_at DESC
        LIMIT %s
        """,
        (lead_id, limit),
    ).fetchall()
    for rr in run_rows:
        run_id = str(rr[0])
        draft_row = conn.execute(
            """
            SELECT subject, body, version FROM outreach_drafts
            WHERE lead_run_id = %s
            ORDER BY version DESC
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
        draft = None
        if draft_row:
            draft = OutreachDraft(
                subject=draft_row[0],
                body=draft_row[1],
                version=int(draft_row[2]),
            )
        tool_rows = conn.execute(
            """
            SELECT tool_name, input_json, output_json, status, idempotency_key, latency_ms
            FROM tool_runs
            WHERE lead_run_id = %s
            ORDER BY created_at
            """,
            (run_id,),
        ).fetchall()
        tools = [
            ToolRunRecord(
                tool_name=tr[0],
                input_json=tr[1] if isinstance(tr[1], dict) else json.loads(tr[1] or "{}"),
                output_json=tr[2] if tr[2] is None or isinstance(tr[2], dict) else json.loads(tr[2]),
                status=tr[3],
                idempotency_key=tr[4],
                latency_ms=tr[5],
            )
            for tr in tool_rows
        ]
        runs.append(
            LeadRun(
                id=run_id,
                lead_id=str(rr[1]),
                status=rr[2],
                qualified=rr[3],
                disqualify_reason=rr[4],
                enrichment=rr[5] if isinstance(rr[5], dict) else json.loads(rr[5] or "{}"),
                research=rr[6] if isinstance(rr[6], dict) else json.loads(rr[6] or "{}"),
                error_code=rr[7],
                shadow_mode=bool(rr[8]),
                started_at=rr[9],
                completed_at=rr[10],
                draft=draft,
                tool_runs=tools,
            )
        )
    return runs


def pg_find_lead_by_email(email: str) -> Lead | None:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT id, email, first_name, company, employee_count, country, industry,
                   hubspot_contact_id, status, created_at
            FROM leads
            WHERE org_id = %s AND email = %s
            """,
            (_org_id(), email.lower()),
        ).fetchone()
        if not row:
            return None
        runs = _fetch_runs_for_lead(conn, str(row[0]))
        return _row_to_lead(row, runs)


def pg_get_lead(lead_id: str) -> Lead | None:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT id, email, first_name, company, employee_count, country, industry,
                   hubspot_contact_id, status, created_at
            FROM leads WHERE id = %s AND org_id = %s
            """,
            (lead_id, _org_id()),
        ).fetchone()
        if not row:
            return None
        runs = _fetch_runs_for_lead(conn, lead_id)
        return _row_to_lead(row, runs)


def pg_list_leads(status: str | None = None) -> list[Lead]:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        if status:
            rows = conn.execute(
                """
                SELECT id, email, first_name, company, employee_count, country, industry,
                       hubspot_contact_id, status, created_at
                FROM leads
                WHERE org_id = %s AND status = %s
                ORDER BY created_at DESC
                """,
                (_org_id(), status),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, email, first_name, company, employee_count, country, industry,
                       hubspot_contact_id, status, created_at
                FROM leads
                WHERE org_id = %s
                ORDER BY created_at DESC
                """,
                (_org_id(),),
            ).fetchall()
        out: list[Lead] = []
        for row in rows:
            lid = str(row[0])
            runs = _fetch_runs_for_lead(conn, lid, limit=1)
            out.append(_row_to_lead(row, runs))
        return out


def pg_save_lead(lead: Lead) -> None:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        conn.execute(
            """
            INSERT INTO leads (
              id, org_id, email, first_name, company, employee_count,
              country, industry, hubspot_contact_id, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (org_id, email) DO UPDATE SET
              first_name = EXCLUDED.first_name,
              company = EXCLUDED.company,
              employee_count = EXCLUDED.employee_count,
              country = EXCLUDED.country,
              industry = EXCLUDED.industry,
              hubspot_contact_id = COALESCE(EXCLUDED.hubspot_contact_id, leads.hubspot_contact_id),
              status = EXCLUDED.status
            """,
            (
                lead.id,
                _org_id(),
                lead.email.lower(),
                lead.first_name,
                lead.company,
                lead.employee_count,
                lead.country,
                lead.industry,
                lead.hubspot_contact_id,
                lead.status,
                lead.created_at,
            ),
        )
        for run in lead.runs:
            conn.execute(
                """
                INSERT INTO lead_runs (
                  id, lead_id, status, qualified, disqualify_reason,
                  enrichment_json, research_json, error_code, shadow_mode,
                  started_at, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  status = EXCLUDED.status,
                  qualified = EXCLUDED.qualified,
                  disqualify_reason = EXCLUDED.disqualify_reason,
                  enrichment_json = EXCLUDED.enrichment_json,
                  research_json = EXCLUDED.research_json,
                  error_code = EXCLUDED.error_code,
                  completed_at = EXCLUDED.completed_at
                """,
                (
                    run.id,
                    lead.id,
                    run.status,
                    run.qualified,
                    run.disqualify_reason,
                    Json(run.enrichment),
                    Json(run.research),
                    run.error_code,
                    run.shadow_mode,
                    run.started_at,
                    run.completed_at,
                ),
            )
            if run.draft:
                conn.execute(
                    """
                    INSERT INTO outreach_drafts (lead_run_id, version, subject, body)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (lead_run_id, version) DO UPDATE SET
                      subject = EXCLUDED.subject,
                      body = EXCLUDED.body
                    """,
                    (run.id, run.draft.version, run.draft.subject, run.draft.body),
                )
            for tool in run.tool_runs:
                if not tool.idempotency_key:
                    conn.execute(
                        """
                        INSERT INTO tool_runs (
                          lead_run_id, tool_name, input_json, output_json,
                          status, idempotency_key, latency_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            run.id,
                            tool.tool_name,
                            Json(tool.input_json),
                            Json(tool.output_json) if tool.output_json is not None else None,
                            tool.status,
                            None,
                            tool.latency_ms,
                        ),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO tool_runs (
                          lead_run_id, tool_name, input_json, output_json,
                          status, idempotency_key, latency_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (idempotency_key) DO NOTHING
                        """,
                        (
                            run.id,
                            tool.tool_name,
                            Json(tool.input_json),
                            Json(tool.output_json) if tool.output_json is not None else None,
                            tool.status,
                            tool.idempotency_key,
                            tool.latency_ms,
                        ),
                    )
        conn.commit()


def pg_insert_approval(
    lead_run_id: str,
    decision: str,
    actor_user_id: str,
    reason: str | None = None,
) -> None:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        conn.execute(
            """
            INSERT INTO approvals (lead_run_id, decision, actor_user_id, reason)
            VALUES (%s, %s, %s, %s)
            """,
            (lead_run_id, decision, actor_user_id, reason),
        )
        conn.execute(
            """
            INSERT INTO audit_events (org_id, actor, action, payload)
            VALUES (%s, %s, %s, %s)
            """,
            (
                UUID(_org_id()),
                actor_user_id,
                f"lead.{decision}",
                Json({"lead_run_id": lead_run_id, "reason": reason}),
            ),
        )
        conn.commit()


def pg_is_opt_out(email: str) -> bool:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT 1 FROM opt_outs
            WHERE org_id = %s AND (email = %s OR domain = %s)
            LIMIT 1
            """,
            (_org_id(), email.lower(), email.split("@")[-1].lower()),
        ).fetchone()
        return row is not None


def pg_get_metrics() -> dict[str, Any]:
    dsn = pg_dsn()
    assert dsn
    with psycopg_connect(dsn) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE org_id = %s",
            (_org_id(),),
        ).fetchone()[0]
        queue = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE org_id = %s AND status = 'awaiting_approval'",
            (_org_id(),),
        ).fetchone()[0]
        drafts = conn.execute(
            """
            SELECT COUNT(*) FROM lead_runs lr
            JOIN leads l ON l.id = lr.lead_id
            WHERE l.org_id = %s AND lr.status = 'awaiting_approval'
            """,
            (_org_id(),),
        ).fetchone()[0]
        approved = conn.execute(
            """
            SELECT COUNT(*) FROM approvals a
            JOIN lead_runs lr ON lr.id = a.lead_run_id
            JOIN leads l ON l.id = lr.lead_id
            WHERE l.org_id = %s AND a.decision = 'approved'
            """,
            (_org_id(),),
        ).fetchone()[0]
        rejected = conn.execute(
            """
            SELECT COUNT(*) FROM approvals a
            JOIN lead_runs lr ON lr.id = a.lead_run_id
            JOIN leads l ON l.id = lr.lead_id
            WHERE l.org_id = %s AND a.decision = 'rejected'
            """,
            (_org_id(),),
        ).fetchone()[0]
        ingests = conn.execute(
            """
            SELECT COUNT(*) FROM lead_runs lr
            JOIN leads l ON l.id = lr.lead_id
            WHERE l.org_id = %s
            """,
            (_org_id(),),
        ).fetchone()[0]
        return {
            "total_leads": int(total),
            "queue_depth": int(queue),
            "draft_ready_count": int(drafts),
            "approval_count": int(approved),
            "reject_count": int(rejected),
            "ingest_count": int(ingests),
            "storage": "postgres",
        }


def pg_audit(action: str, actor: str, payload: dict[str, Any]) -> None:
    dsn = pg_dsn()
    if not dsn:
        return
    with psycopg_connect(dsn) as conn:
        conn.execute(
            """
            INSERT INTO audit_events (org_id, actor, action, payload)
            VALUES (%s, %s, %s, %s)
            """,
            (UUID(_org_id()), actor, action, Json(payload)),
        )
        conn.commit()


def psycopg_connect(dsn: str):
    import psycopg

    return psycopg.connect(dsn, connect_timeout=5)
