-- PipelinePilot core schema (see docs/DATABASE_SCHEMA.md)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email CITEXT UNIQUE NOT NULL,
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS organization_members (
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'rep',
  PRIMARY KEY (org_id, user_id)
);

CREATE TABLE IF NOT EXISTS hubspot_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
  portal_id TEXT,
  access_token_enc TEXT,
  refresh_token_enc TEXT,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email CITEXT NOT NULL,
  first_name TEXT,
  company TEXT,
  employee_count INT,
  country TEXT,
  industry TEXT,
  hubspot_contact_id TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (org_id, email)
);

CREATE INDEX IF NOT EXISTS idx_leads_org_status ON leads (org_id, status, created_at DESC);

CREATE TABLE IF NOT EXISTS lead_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'queued',
  qualified BOOLEAN,
  disqualify_reason TEXT,
  enrichment_json JSONB NOT NULL DEFAULT '{}',
  research_json JSONB NOT NULL DEFAULT '{}',
  error_code TEXT,
  shadow_mode BOOLEAN NOT NULL DEFAULT true,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_lead_runs_lead ON lead_runs (lead_id, started_at DESC);

CREATE TABLE IF NOT EXISTS outreach_drafts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_run_id UUID NOT NULL REFERENCES lead_runs(id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_run_id UUID NOT NULL REFERENCES lead_runs(id) ON DELETE CASCADE,
  decision TEXT NOT NULL,
  actor_user_id TEXT NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tool_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_run_id UUID NOT NULL REFERENCES lead_runs(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL,
  input_json JSONB NOT NULL,
  output_json JSONB,
  status TEXT NOT NULL,
  idempotency_key TEXT UNIQUE,
  latency_ms INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS opt_outs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email CITEXT,
  domain TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feature_flags (
  key TEXT PRIMARY KEY,
  enabled BOOLEAN NOT NULL DEFAULT false,
  payload JSONB NOT NULL DEFAULT '{}',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO feature_flags (key, enabled) VALUES
  ('shadow_mode', true),
  ('crm_writes_enabled', false),
  ('kill_switch', false)
ON CONFLICT (key) DO NOTHING;

INSERT INTO organizations (id, name) VALUES
  ('00000000-0000-0000-0000-000000000001', 'Demo Org')
ON CONFLICT (id) DO NOTHING;
