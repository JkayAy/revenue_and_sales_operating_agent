# Interview Guide — PipelinePilot

**Elevator pitch (30s):**  
PipelinePilot is a **governed sales ops agent**: HubSpot lead in → ICP qualify → enrich/research → draft email → **human approval** → idempotent CRM writes. Playbook rules live in code; golden evals run in CI.

---

## Screen-share order (8 min)

1. **Architecture** — README diagram + `docs/BLUEPRINT.md`  
2. **Docker** — `curl /ready` (Postgres connected)  
3. **Ingest** — Dashboard “Sample lead” or `POST /v1/leads/ingest`  
4. **Approval** — Open lead → sources + draft → Approve (shadow dry-run in tool_runs)  
5. **Metrics** — `/v1/admin/metrics` + dashboard `/metrics`  
6. **Engineering** — `python -m eval`, playbook YAML, webhook signature test  

---

## Talking points

| Topic | What to say |
|-------|-------------|
| Safety | No auto-send in MVP; shadow + approval queue |
| CRM | Allowlisted HubSpot tools; idempotency keys per run |
| Quality | Golden ICP + orchestrator scenarios in CI |
| Scale path | Postgres tenancy, OAuth tokens, optional LLM drafts |

---

## Likely questions

**Why not auto-send?** Reputation and compliance; prove approval UX and eval gates first.  

**How is this not ChatGPT?** Typed pipeline, playbook engine, audit log, CRM side-effects behind flags.  

**Agentforce comparison?** Same *pattern* (CRM + agent), narrower scope with explicit human-in-the-loop story.  

---

## Links to show

- `docs/HUBSPOT.md` — OAuth + webhooks  
- `docs/EVALUATION_AND_SAFETY.md` — golden sets  
- GitHub Actions CI — pytest + eval  
