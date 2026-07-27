# Database Schema

**Engine:** PostgreSQL 16  
**Extensions:** `pgcrypto`, `citext`  

---

## 1. ER overview

```text
organizations 1──N organization_members ──N users
organizations 1──N hubspot_connections
organizations 1──N playbooks
organizations 1──N leads 1──N lead_runs
lead_runs 1──N tool_runs
lead_runs 1──1 outreach_drafts (latest version)
lead_runs 1──N approvals
organizations 1──N opt_outs
organizations 1──N audit_events
organizations 1──N feature_flags
```

---

## 2. Tables

### `organizations`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `name` | TEXT | |
| `created_at` | TIMESTAMPTZ | |

### `users`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `email` | CITEXT UNIQUE | |
| `display_name` | TEXT | |
| `created_at` | TIMESTAMPTZ | |

### `organization_members`

| Column | Type | Notes |
|--------|------|-------|
| `org_id` | UUID FK | |
| `user_id` | UUID FK | |
| `role` | TEXT | `rep`, `manager`, `admin`, `viewer` |
| PRIMARY KEY | (org_id, user_id) | |

### `hubspot_connections`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `org_id` | UUID FK UNIQUE | One portal per org MVP |
| `portal_id` | TEXT | |
| `access_token_enc` | TEXT | Encrypt at app layer |
| `refresh_token_enc` | TEXT | |
| `expires_at` | TIMESTAMPTZ | |
| `created_at` | TIMESTAMPTZ | |

### `playbooks`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `org_id` | UUID FK | |
| `version` | INT | |
| `config_yaml` | TEXT | Or JSONB snapshot |
| `active` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

### `leads`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `org_id` | UUID FK | |
| `email` | CITEXT | |
| `first_name` | TEXT | |
| `company` | TEXT | |
| `employee_count` | INT NULL | |
| `country` | TEXT | |
| `industry` | TEXT | |
| `hubspot_contact_id` | TEXT NULL | |
| `status` | TEXT | `new`, `processing`, `awaiting_approval`, … |
| `created_at` | TIMESTAMPTZ | |
| UNIQUE | (org_id, email) | |

### `lead_runs`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `lead_id` | UUID FK | |
| `status` | TEXT | Pipeline state |
| `qualified` | BOOLEAN NULL | |
| `disqualify_reason` | TEXT NULL | |
| `enrichment_json` | JSONB | |
| `research_json` | JSONB | |
| `error_code` | TEXT NULL | |
| `shadow_mode` | BOOLEAN | |
| `started_at` | TIMESTAMPTZ | |
| `completed_at` | TIMESTAMPTZ NULL | |

### `outreach_drafts`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `lead_run_id` | UUID FK | |
| `version` | INT | |
| `subject` | TEXT | |
| `body` | TEXT | |
| `created_at` | TIMESTAMPTZ | |

### `approvals`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `lead_run_id` | UUID FK | |
| `decision` | TEXT | `approved`, `rejected` |
| `actor_user_id` | TEXT | MVP string id |
| `reason` | TEXT NULL | |
| `created_at` | TIMESTAMPTZ | |

### `tool_runs`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `lead_run_id` | UUID FK | |
| `tool_name` | TEXT | |
| `input_json` | JSONB | |
| `output_json` | JSONB | |
| `status` | TEXT | |
| `idempotency_key` | TEXT UNIQUE | |
| `latency_ms` | INT | |
| `created_at` | TIMESTAMPTZ | |

### `opt_outs`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `org_id` | UUID FK | |
| `email` | CITEXT NULL | |
| `domain` | TEXT NULL | |
| `created_at` | TIMESTAMPTZ | |

### `audit_events`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `org_id` | UUID FK | |
| `actor` | TEXT | |
| `action` | TEXT | |
| `payload` | JSONB | |
| `created_at` | TIMESTAMPTZ | |

### `feature_flags`

| Column | Type | Notes |
|--------|------|-------|
| `key` | TEXT PK | |
| `enabled` | BOOLEAN | |
| `payload` | JSONB | |
| `updated_at` | TIMESTAMPTZ | |

---

## 3. RBAC

See [PRD](./PRD.md) permissions matrix; enforce in API middleware from R4.

---

## 4. Retention (pilot)

- Conversational drafts: 90 days  
- Audit events: 1 year  
- PII export on request (GDPR story)  

---

## 5. Migration

Applied via `infra/migrations/001_initial.sql` on Docker Compose up.
