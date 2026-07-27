# Implementation Backlog

| Milestone | Status |
|-----------|--------|
| **R0 — Spec** | Done |
| **R1 — Foundation** | Done |
| **R2 — Agent core** | Done |
| **R3 — Approval + CRM + Postgres** | Done |
| **R4 — HubSpot + webhooks + LLM** | Done |
| **R5 — Portfolio + hardening** | Done |

## v0.5 hardening

- Rate limiting on ingest/webhook (`rate_limit.py`)
- Request tracing + structured logs (`observability.py`)
- HubSpot OAuth refresh token flow
- CI: pytest + `python -m eval`

## Post-portfolio (optional)

- OpenTelemetry exporter when `OTEL_ENABLED=true`
- Real enrichment/search providers
- Salesforce (R6)
- Multi-tenant auth (Clerk/JWT)
