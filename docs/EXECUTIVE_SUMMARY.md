# Executive Summary — Revenue & Sales Operations Agent

**Author:** [Your name]  
**Role target:** AI Engineer / Applied ML / LLM Platform  
**Last updated:** July 2026  

---

## Problem

Sales teams lose revenue to **slow lead follow-up** and **low-quality outreach**. Reps spend most of their time on CRM updates and research instead of conversations.

---

## Solution (this project)

**PipelinePilot** — an agent that:

1. Ingests inbound leads from **HubSpot**  
2. **Qualifies** against ICP rules in code  
3. **Enriches** and **researches** with source citations  
4. **Drafts** personalized first-touch email  
5. Requires **human approval** before CRM commits  
6. Logs **100%** of tool calls and runs **golden-lead evals** in CI  

---

## Differentiators

| Capability | Detail |
|------------|--------|
| Playbook engine | ICP + stage rules before LLM |
| Human-in-the-loop | No autonomous send in MVP |
| Tool layer | Idempotent HubSpot writes |
| Observability | Per-lead run timeline |
| Eval | Playbook + orchestrator golden sets |

---

## Reading order

1. [Blueprint](./BLUEPRINT.md)  
2. [PRD](./PRD.md)  
3. [TRD](./TRD.md)  
4. [MVP](./MVP.md)  
5. [Comprehensive roadmap](./COMPREHENSIVE_ROADMAP.md)  
