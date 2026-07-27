# User Flows

Every primary journey includes **success**, **failure**, and **recovery** paths.

---

## 1. RevOps: Connect HubSpot (pilot)

1. Open **Settings → Integrations**  
2. Click **Connect HubSpot** (OAuth) or paste **webhook URL** in HubSpot private app  
3. Send test webhook → UI shows **Connected** with last event timestamp  
4. **Failure:** Invalid signature → error code `webhook_signature_invalid` + doc link  
5. **Recovery:** Re-copy secret; retry test  

---

## 2. System: New lead → draft ready

1. HubSpot `contact.creation` or `POST /v1/leads/ingest`  
2. Lead card status **Processing** (stepper: qualify → enrich → research → draft)  
3. **Qualified:** status **Awaiting approval** with draft preview  
4. **Disqualified:** status **Closed — ICP** with reason; no draft  
5. **Failure:** Run status **Failed** with `error_code` + **Retry run** button  
6. **Opt-out:** status **Blocked**; no processing  

---

## 3. Rep: Review queue

1. **Queue** default filter: `awaiting_approval`  
2. Open lead → tabs: **Summary**, **Sources**, **Draft**, **Activity**  
3. **Edit draft** inline → saves new version (audit)  
4. **Approve** → if `crm_writes_enabled` and not shadow: CRM sync spinner → **Synced** or actionable error  
5. **Reject** → requires reason → removed from rep queue; counted in metrics  
6. **Empty queue:** CTA **Import sample CSV** or link to HubSpot setup  

---

## 4. Manager: KPIs

1. **Dashboard → Metrics**  
2. Tiles: median time-to-draft, approval rate, disqualify rate, failures  
3. **Kill switch** disables new runs (existing drafts remain)  

---

## 5. Shadow mode demo (employer screen-share)

1. Enable **shadow_mode** flag  
2. Ingest sample lead → full pipeline visible  
3. Approve → UI shows **Would sync to HubSpot** (dry-run payload)  
4. No external CRM mutation  

---

## 6. CSV import (fallback ingest)

1. **Leads → Import**  
2. Upload CSV (email, company, employee_count, country)  
3. Batch ingest with progress bar  
4. Row-level errors downloadable as CSV  

*(CSV UI v1.1; API ingest available in v0.2.)*
