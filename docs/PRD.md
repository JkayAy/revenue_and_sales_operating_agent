# Product Requirements Document (PRD)

**Product:** PipelinePilot — AI Revenue & Sales Operations Agent  
**Version:** 1.0  
**Status:** Approved for MVP implementation  
**Owner:** [Your name]  

---

## 1. Overview

### 1.1 Problem statement

B2B sales teams lose pipeline to **slow follow-up** and **generic outreach**. Reps spend most of their day on CRM hygiene, manual research, and drafting emails instead of selling. Inbound leads often wait hours or days for a personalized first touch.

### 1.2 Product summary

A **sales operations agent** that ingests inbound leads (HubSpot-first), **qualifies** against an ICP playbook, **enriches** and **researches** accounts with cited sources, **drafts** personalized outreach, and **updates CRM** only after **human approval**—with full audit and eval coverage.

### 1.3 Goals

| Goal | Metric | Target (pilot) |
|------|--------|----------------|
| Speed-to-lead | Median ingest → draft ready | < 5 minutes |
| Qualification accuracy | Golden-lead ICP pass rate | ≥ 95% |
| Rep trust | Draft approved without major edit | ≥ 70% |
| Safety | Unapproved outbound sends | 0 |
| Governance | CRM writes in audit log | 100% |

### 1.4 Non-goals

- Replacing HubSpot/Salesforce as system of record  
- Autonomous email send without approval (MVP)  
- LinkedIn automation behind login walls  
- CPQ / quote PDF generation in v1  
- Multi-language sequences in v1  

---

## 2. Users & personas

### 2.1 SDR / AE (primary)

- **Needs:** Context, editable drafts, fast approve/reject, predictable CRM updates.  
- **Success:** First-touch draft in minutes; no surprise pipeline moves.

### 2.2 Sales manager

- **Needs:** Team queue, KPIs, playbook tuning, kill switch.  
- **Success:** Visibility into agent errors and approval rates.

### 2.3 RevOps / admin

- **Needs:** HubSpot mapping, stage rules, audit export, eval gates.  
- **Success:** CI blocks regressions; shadow mode for testing.

---

## 3. User stories (P0)

| ID | Story | Acceptance criteria |
|----|-------|---------------------|
| US-L1 | As RevOps, I connect HubSpot so leads flow in | OAuth or webhook secret configured; test event ingested |
| US-L2 | As the system, I qualify new leads against ICP | Qualified/disqualified with coded reason |
| US-L3 | As a rep, I see enrichment and sources on a lead | Firmographics + `sources[]` or explicit gap |
| US-L4 | As a rep, I review and approve a draft | Approve/reject/edit logged with actor |
| US-L5 | As RevOps, I control CRM writes | Shadow mode blocks writes; flag enables post-approval writes |
| US-L6 | As a manager, I view KPIs | Queue depth, median time-to-draft, approval rate |
| US-L7 | As security, I audit tool calls | Every HubSpot tool run stored with idempotency key |

---

## 4. Functional requirements

### 4.1 Ingest

- HubSpot webhook: `contact.creation` (and manual `POST /v1/leads/ingest`)  
- Dedupe by email per organization  
- Opt-out / blocklist check before processing  

### 4.2 Agent pipeline

1. Qualify (playbook engine)  
2. Enrich (provider or mock in dev)  
3. Research (search API or mock; min citation policy)  
4. Draft outreach (subject + body)  
5. Queue for approval  

### 4.3 CRM (post-approval)

- Add timeline note with draft summary  
- Update deal stage per playbook when approved  
- Idempotent writes per `lead_run_id`  

### 4.4 Admin

- Feature flags: `shadow_mode`, `crm_writes_enabled`, `kill_switch`  
- Metrics endpoint for dashboard  

---

## 5. Policies & compliance

- CAN-SPAM: MVP does not send mail; customer owns list consent  
- PII: redact email body in default trace export  
- Rate limits on ingest and search tools  

---

## 6. Success metrics & instrumentation

Events: `lead.ingested`, `lead.qualified`, `lead.draft_ready`, `lead.approved`, `lead.crm_synced`, `lead.failed`.

---

## 7. Dependencies

- HubSpot developer sandbox  
- Optional: search API key (Tavily/Serper) for live research  
- Optional: OpenAI/Anthropic for draft polish (deterministic template fallback in dev)  

---

## 8. Open questions

| Question | Default for MVP |
|----------|-----------------|
| Salesforce in v1? | No — HubSpot only |
| Who can approve? | Any authenticated rep; manager sees all |
| Auto-assign leads? | Round-robin v1.1 |
