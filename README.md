# AI Revenue & Sales Operations Agent (PipelinePilot)

[![CI](https://github.com/JkayAy/revenue_and_sales_operating_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/JkayAy/revenue_and_sales_operating_agent/actions/workflows/ci.yml)

**Repository:** [github.com/JkayAy/revenue_and_sales_operating_agent](https://github.com/JkayAy/revenue_and_sales_operating_agent)

Sales-ops agent prototype: ingest leads, qualify against ICP, mock enrich/research, template outreach draft, human approval queue, and **mock HubSpot CRM writes** (shadow/dry-run by default).

---

## What actually runs (audit, Aug 2026)

Claims below were checked by running tests, `python -m eval`, local API imports, Docker Compose, and code inspection. Nothing is marked verified unless it was exercised in this repo.

| Area | Evidence | Status |
|------|----------|--------|
| Spec / planning docs (`docs/PRD.md`, TRD, MVP) | Files present | **Verified** — documentation only |
| Playbook engine (ICP, citations, stage rules) | `packages/playbook_engine/tests`, `python -m eval` (9/9) | **Verified** |
| Orchestrator: qualify → enrich → research → draft | `orchestrator.py`, `test_core_loop_e2e.py`, `test_api.py` | **Verified** — enrich/research are **in-process mocks**, not external APIs |
| Golden eval harness | `python -m eval` — 9/9 scenarios | **Verified** |
| FastAPI ingest / approve / reject / list | `pytest` API tests | **Verified** (in-memory store by default) |
| Postgres persistence | `test_postgres_integration.py` (opt-in `INTEGRATION_DB=1`); Docker `/ready` with `database: connected` | **Verified** when Postgres is up |
| Approval audit records | `record_approval` in store/postgres | **Verified** in-memory; Postgres path covered by integration test |
| Next.js approval dashboard | `npm run build` succeeds | **Verified** — build only; no automated browser E2E against API |
| Mock HubSpot client + idempotency | `test_mock_client.py` | **Verified** — mock only |
| Shadow mode / dry-run CRM on approve | Default `shadow_mode=true`; `sync_crm_after_approval` passes `dry_run` | **Verified** in E2E test (no live CRM mutation) |
| Webhook signature verification | `test_webhook_signature.py`, `test_webhooks.py` | **Verified** — unit tests with test secrets |
| Rate limiting (`429` on ingest) | `test_hardening.py` | **Verified** |
| Request tracing (`X-Trace-Id`) | `test_hardening.py` | **Verified** |
| Live HubSpot client (`LiveHubSpotClient`) | Code in `packages/tools_hubspot/src/tools_hubspot/live.py` | **Not verified** — no test against a real HubSpot account |
| HubSpot OAuth (authorize / callback / token refresh) | Routes in `hubspot_auth.py`, `integrations.py` | **Not verified** — no live OAuth run in CI or tests |
| LLM draft generation (OpenAI) | `draft_writer.py`, disabled by default | **Not verified** — no tests with live API |
| HubSpot webhooks → ingest | Route exists; signature tests only | **Partial** — signature verified; full webhook→ingest path not E2E tested |

**Test commands run:** `pytest` (16 passed), `python -m eval` (9/9 passed).

---

## Core loop (local, mock data)

```
POST /v1/leads/ingest
  → ICP qualify (playbook engine)
  → mock enrich + mock research (fixed in-process data)
  → template draft (optional LLM if configured — untested here)
  → status: awaiting_approval

GET /v1/leads?status=awaiting_approval   # approval queue

POST /v1/leads/{id}/approve
  → MockHubSpotClient create_note + update_deal_stage (dry_run while shadow_mode=true)
  → status: approved
```

CRM writes use **MockHubSpotClient** when `MOCK_TOOLS=true` (default). Live writes require `MOCK_TOOLS=false`, a real token, `crm_writes_enabled=true`, and `shadow_mode=false` — that path has **not** been verified against HubSpot in this repo.

---

## Quick start

**Docker (Postgres + API on host port 8001):**

```powershell
.\scripts\docker-up.ps1 -Build
curl http://localhost:8001/ready
```

Default host port is **8001** to avoid common conflicts on 8000. Override with `SALES_API_HOST_PORT`.

**Local (in-memory store, no Docker):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
python -m eval
sales-api
# API: http://127.0.0.1:8000
```

**Dashboard:**

```powershell
cd apps/dashboard
npm install
$env:NEXT_PUBLIC_SALES_API="http://127.0.0.1:8000"   # or :8001 if using Docker API
npm run dev
```

See [docs/LAUNCH.md](./docs/LAUNCH.md) and [docs/HUBSPOT.md](./docs/HUBSPOT.md).

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Launch guide](./docs/LAUNCH.md) | Local and Docker setup |
| [HubSpot setup](./docs/HUBSPOT.md) | OAuth/webhooks — **code exists; live use not verified here** |
| [Interview guide](./docs/INTERVIEW_GUIDE.md) | Demo script aligned to verified behavior |
| [PRD / TRD / MVP](./docs/PRD.md) | Requirements & design |
| [Comprehensive roadmap](./docs/COMPREHENSIVE_ROADMAP.md) | **Planning** — future phases, not delivery claims |

---

## Hardening (implemented & tested)

- **Rate limit:** `POST /v1/leads/ingest` and `/v1/webhooks/hubspot` — `RATE_LIMIT_PER_MINUTE` (default 60)
- **Tracing:** Response header `X-Trace-Id`; structured logs on ingest complete
- **HubSpot OAuth refresh:** Implemented in code; **not verified** against live HubSpot token expiry

---

## Author

**Ayodele Kolawole James** — MIT License.
