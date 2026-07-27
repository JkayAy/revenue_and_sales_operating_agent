# Technical Requirements Document (TRD)

**System:** PipelinePilot — Sales Agent API  
**Version:** 1.0  
**Companion:** [PRD](./PRD.md), [Blueprint](./BLUEPRINT.md)  

---

## 1. System context

```text
[Next.js dashboard] --HTTPS--> [Sales Agent API] --> [PostgreSQL]
[HubSpot webhooks]  --------->       |
                                     +--> [Playbook engine]
                                     +--> [HubSpot tools]
                                     +--> [Search / enrich providers]
```

---

## 2. Technology stack

| Layer | Choice |
|-------|--------|
| Dashboard | Next.js 14+ (React) |
| Agent API | FastAPI (Python 3.11+) |
| Database | PostgreSQL 16 (+ pgvector optional v1.1) |
| Queue | In-process async (MVP); Redis job queue v1.1 |
| LLM | OpenAI/Anthropic optional; template drafts in mock mode |
| Observability | Structured logs; OpenTelemetry hooks (R4) |
| CI | GitHub Actions — ruff, pytest, `python -m eval` |

---

## 3. Repository structure

```text
/
├── apps/
│   ├── sales-api/       # FastAPI orchestrator + routes
│   └── dashboard/       # Rep queue UI
├── packages/
│   ├── playbook_engine/
│   ├── tools_hubspot/
│   └── eval/
├── config/playbook.yaml
├── infra/migrations/
├── docs/
└── scripts/
```

---

## 4. API specification

### 4.1 Leads

#### `POST /v1/leads/ingest`

```json
{
  "email": "alex@acme.io",
  "first_name": "Alex",
  "company": "Acme Analytics",
  "employee_count": 120,
  "country": "US",
  "industry": "software",
  "hubspot_contact_id": "optional"
}
```

Response: `{ "lead_id", "run_id", "status" }`

#### `GET /v1/leads?status=draft_pending`

List leads with latest run summary.

#### `GET /v1/leads/{lead_id}`

Full detail: enrichment, research, draft, tool_runs, timeline.

#### `POST /v1/leads/{lead_id}/approve`

Body: `{ "editor_user_id": "demo-rep", "edited_subject": null, "edited_body": null }`

#### `POST /v1/leads/{lead_id}/reject`

Body: `{ "reason": "wrong persona" }`

### 4.2 Webhooks

#### `POST /v1/webhooks/hubspot`

HubSpot subscription payload (v1: simplified JSON); validates optional `X-HubSpot-Signature`.

### 4.3 Admin

- `GET /v1/admin/metrics` — KPI aggregates  
- `GET /v1/admin/flags` / `POST /v1/admin/flags` — feature flags (header `X-Admin-Key` if set)  

### 4.4 Health

- `GET /health`, `GET /ready`  

---

## 5. Authentication (phased)

| Phase | Mechanism |
|-------|-----------|
| MVP demo | Open API + optional `ADMIN_API_KEY` |
| R4 | Magic link / Clerk JWT; org-scoped routes |

HubSpot: OAuth refresh tokens in `hubspot_connections` (encrypted column in prod story).

---

## 6. Agent orchestration

State machine on `lead_runs.status`:

`queued` → `qualifying` → `enriching` → `researching` → `drafting` → `awaiting_approval` → `approved` | `rejected` | `failed`

Shadow mode: run through `drafting`, skip HubSpot writes even on approve.

---

## 7. Tool contract

| Tool | Idempotency key pattern |
|------|-------------------------|
| `hubspot_create_note` | `{lead_run_id}:note` |
| `hubspot_update_deal_stage` | `{lead_run_id}:stage` |
| `hubspot_upsert_contact` | `{org_id}:{email}` |

---

## 8. Environment variables

See `.env.example`: `DATABASE_URL`, `ADMIN_API_KEY`, `HUBSPOT_CLIENT_SECRET`, `PLAYBOOK_CONFIG_PATH`, `CORS_ORIGINS`, `MOCK_TOOLS=true`.

---

## 9. Security

- Webhook signature verification when secret configured  
- Rate limit ingest: 60/min/IP (in-memory MVP)  
- No secrets in logs  

---

## 10. Testing

- Unit: playbook_engine, tools_hubspot mock  
- API: httpx AsyncClient against FastAPI  
- Golden: `python -m eval` in CI  
