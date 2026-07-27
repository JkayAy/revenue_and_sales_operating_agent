CREATE UNIQUE INDEX IF NOT EXISTS idx_outreach_drafts_run_version
  ON outreach_drafts (lead_run_id, version);
