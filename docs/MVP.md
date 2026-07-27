# MVP Definition — Version 1.0

**Purpose:** Ship a **hire-ready pilot** that proves governed sales automation—not unconstrained outbound AI.

---

## 1. MVP thesis

Prove **sub-5-minute** ingest-to-draft for inbound HubSpot leads with **ICP gating**, **cited research posture**, **approval queue**, and **audited CRM side-effects** in shadow or controlled pilot mode.

---

## 2. In scope (P0)

| Area | Included |
|------|----------|
| Ingest | Manual API + HubSpot webhook stub |
| Qualify | Playbook engine (YAML) |
| Enrich / research | Mock providers + citation policy |
| Draft | Template + optional LLM env |
| UI | Dashboard queue + lead detail + approve/reject |
| CRM | Mock HubSpot client; real API when creds set |
| Eval | ≥ 15 golden playbook scenarios in CI |
| Ops | Docker Compose Postgres + API; flags |

---

## 3. Out of scope

| Item | Deferred |
|------|----------|
| Autonomous email send | v1.2+ after eval |
| Salesforce | R6 |
| Multi-tenant billing | v2.0 |
| LinkedIn actions | — |
| Quote / CPQ | — |

---

## 4. Quality bar

| Gate | Threshold |
|------|-----------|
| Playbook golden eval | ≥ 95% pass |
| Orchestrator mock eval | ≥ 80% pass |
| Manual pilot | 0 unapproved sends |
| CRM duplicate writes | 0 on retry (idempotency) |

---

## 5. Timeline (13 weeks)

See [COMPREHENSIVE_ROADMAP.md](./COMPREHENSIVE_ROADMAP.md) phases R0–R5.

**Current implementation target:** Complete **R1 + R2** foundation and agent core in repo.

---

## 6. Employer narrative

> “I bounded MVP to **HubSpot ingest → qualify → draft → human approval → idempotent CRM writes**, with **playbook rules in code** and **golden-lead evals in CI**—because speed-to-lead only matters if RevOps trusts the automation.”
