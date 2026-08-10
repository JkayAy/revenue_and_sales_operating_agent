# HubSpot integration

Connect a **HubSpot private app** or **OAuth app** for live CRM notes and deal stage updates after rep approval.

> **Verification status:** Mock HubSpot (`MockHubSpotClient`) and webhook signature checks are covered by unit tests. `LiveHubSpotClient`, OAuth callback, token refresh, and real CRM writes have **not** been exercised against a live HubSpot account in this repository. Treat live setup as operator-tested only.

---

## 1. Private app (fastest for demo)

1. HubSpot → Settings → Integrations → Private Apps → Create  
2. Scopes: `crm.objects.contacts.read`, `crm.objects.contacts.write`, `crm.objects.deals.read`, `crm.objects.deals.write`, `crm.objects.notes.write`  
3. Copy access token → `.env`:

```env
MOCK_TOOLS=false
HUBSPOT_ACCESS_TOKEN=pat-...
HUBSPOT_WEBHOOK_SECRET=your-app-client-secret
```

4. Set `crm_writes_enabled=true` via admin flags (and disable shadow for real writes):

```http
POST /v1/admin/flags/crm_writes_enabled
{"enabled": true}
```

Keep **`shadow_mode=true`** until you are ready for live CRM mutations.

---

## 2. OAuth (production-style)

Set in `.env`:

```env
HUBSPOT_CLIENT_ID=
HUBSPOT_CLIENT_SECRET=
HUBSPOT_REDIRECT_URI=http://127.0.0.1:8001/v1/integrations/hubspot/callback
```

1. Open `GET /v1/integrations/hubspot/authorize` → HubSpot consent  
2. Callback stores tokens in `hubspot_connections` (Postgres)  
3. `GET /v1/integrations/hubspot/status` shows connection state  

---

## 3. Webhooks

Target URL: `POST https://<your-host>/v1/webhooks/hubspot`

HubSpot sends `X-HubSpot-Signature` = `SHA256(client_secret + raw_body)`.

If the payload only includes `objectId`, the API fetches contact properties via CRM when a token is configured.

---

## 4. Deal stages

`config/playbook.yaml` → `pipeline.on_approve_first_touch.deal_stage_id` must be the **internal** HubSpot stage ID (not the label). Find it in HubSpot deal pipeline settings.

---

## 5. LLM drafts (optional)

```env
LLM_DRAFT_ENABLED=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

When enabled (and flag `llm_draft_enabled`), outreach copy is generated via OpenAI; falls back to the template if the API fails.
