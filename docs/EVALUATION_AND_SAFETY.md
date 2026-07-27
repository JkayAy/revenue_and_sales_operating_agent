# Evaluation & Safety

---

## 1. Golden datasets

| Category | Location | Purpose |
|----------|----------|---------|
| Playbook / ICP | `packages/eval/scenarios/playbook/` | Qualify/disqualify, stage rules |
| Orchestrator | `packages/eval/scenarios/orchestrator/` | End-to-end mock pipeline |
| Safety | `packages/eval/scenarios/safety/` | Opt-out, blocked domain, injection in company name |

**CI gate:** `python -m eval` must pass thresholds in [MVP](./MVP.md).

---

## 2. Regression policy

- No merge if playbook pass rate drops below 95%  
- Add scenario for every production bug fix  

---

## 3. Red team (manual + scripted)

- Prompt injection via `company` / `first_name` fields  
- Attempt to force CRM stage skip without approval  
- Duplicate webhook delivery (idempotency)  

---

## 4. Guardrails

- Opt-out table checked first  
- Minimum citation count before draft (playbook)  
- `kill_switch` halts processing  

---

## 5. Shadow mode

Full pipeline without HubSpot mutations; dry-run payloads in API response for demos.
