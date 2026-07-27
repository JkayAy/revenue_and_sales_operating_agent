INSERT INTO feature_flags (key, enabled) VALUES
  ('llm_draft_enabled', false)
ON CONFLICT (key) DO NOTHING;
