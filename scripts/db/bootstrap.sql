-- Bootstrap schema for local development.
-- Safe to re-apply thanks to IF NOT EXISTS guards.

CREATE TABLE IF NOT EXISTS ng_meta (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ng_agents (
  agent_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
  heartbeat_interval_s INTEGER NOT NULL DEFAULT 10,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ng_events (
  event_id TEXT PRIMARY KEY,
  trace_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  capability TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  budget_ms INTEGER NOT NULL DEFAULT 3000,
  timeout_ms INTEGER NOT NULL DEFAULT 1500,
  attempt INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ng_incidents (
  incident_id TEXT PRIMARY KEY,
  trace_id TEXT,
  severity TEXT NOT NULL DEFAULT 'error',
  message TEXT NOT NULL,
  context JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'open'
);

CREATE INDEX IF NOT EXISTS idx_ng_events_trace_id ON ng_events (trace_id);
CREATE INDEX IF NOT EXISTS idx_ng_incidents_trace_id ON ng_incidents (trace_id);
