# AI Revenue & Sales Operations Agent (PipelinePilot)

[![CI](https://github.com/JkayAy/revenue_and_sales_operating_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/JkayAy/revenue_and_sales_operating_agent/actions/workflows/ci.yml)

**Repository:** [github.com/JkayAy/revenue_and_sales_operating_agent](https://github.com/JkayAy/revenue_and_sales_operating_agent)

Production-style **sales operations agent** — ingest leads, qualify against ICP, enrich/research with citations, draft outreach, **human approval**, and **idempotent HubSpot CRM writes** (shadow mode by default).

---

## Why this project (for hiring managers)

| Concern | How this design addresses it |
|--------|------------------------------|
| “ChatGPT wrapper” | Multi-step loop: ingest → qualify → enrich → research → draft → CRM; playbook engine in code |
| Unsafe automation | No autonomous send in v1; approval queue; opt-out; idempotent CRM tools |
| CRM trust | Allowlisted HubSpot tools; stage rules; shadow / dry-run |
| Production habits | Postgres persistence, signed webhooks, rate limits, request tracing, golden eval in CI |
| Business outcome | KPIs: queue depth, drafts ready, approval rate |

---

## Status — v0.5 (portfolio complete)

| Milestone | Delivered |
|-----------|-----------|
| R0–R2 | Spec docs, playbook engine, orchestrator, eval harness, Next.js dashboard |
| R3 | Postgres persistence, approvals, audit |
| R4 | Live HubSpot client, OAuth routes, webhook signatures, optional LLM drafts |
| R5 | Interview guide, rate limiting, structured tracing (`X-Trace-Id`), HubSpot token refresh |

---

## Quick start

**Docker (recommended):**

```powershell
.\scripts\docker-up.ps1 -Build
curl http://localhost:8000/ready
```

**Local:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
python -m eval
sales-api
```

**Dashboard:** `cd apps/dashboard && npm install && npm run dev` (set `NEXT_PUBLIC_SALES_API=http://127.0.0.1:8000`).

See [docs/LAUNCH.md](./docs/LAUNCH.md) and [docs/HUBSPOT.md](./docs/HUBSPOT.md).

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Comprehensive roadmap](./docs/COMPREHENSIVE_ROADMAP.md) | Phases R0–R5 |
| [Interview guide](./docs/INTERVIEW_GUIDE.md) | 8-min demo script |
| [HubSpot setup](./docs/HUBSPOT.md) | OAuth, webhooks, live CRM |
| [PRD / TRD / MVP](./docs/PRD.md) | Requirements & stack |

Full index in previous sections of this repo under `docs/`.

---

## Hardening (v0.5)

- **Rate limit:** `POST /v1/leads/ingest` and `/v1/webhooks/hubspot` — `RATE_LIMIT_PER_MINUTE` (default 60)
- **Tracing:** Response header `X-Trace-Id`; structured logs on ingest complete
- **HubSpot OAuth:** Automatic refresh when DB-stored token expires (refresh token required)

---

## Author

**Ayodele Kolawole James** — MIT License. Add LinkedIn and Loom demo URL when ready.
