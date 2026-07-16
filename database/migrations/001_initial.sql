CREATE TABLE IF NOT EXISTS roles (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  permissions JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role_id TEXT NOT NULL REFERENCES roles(id),
  active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS columns (
  id INTEGER PRIMARY KEY CHECK (id BETWEEN 1 AND 200),
  block_id INTEGER NOT NULL CHECK (block_id BETWEEN 1 AND 10),
  state TEXT NOT NULL,
  flow_setpoint_kg_h NUMERIC NOT NULL DEFAULT 0,
  flow_measured_kg_h NUMERIC NOT NULL DEFAULT 0,
  data_quality NUMERIC NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS commands (
  command_id TEXT PRIMARY KEY,
  column_id INTEGER NOT NULL REFERENCES columns(id),
  command_type TEXT NOT NULL,
  requested_value JSONB,
  requested_by TEXT NOT NULL,
  requested_at TIMESTAMPTZ NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  sequence BIGINT NOT NULL,
  status TEXT NOT NULL,
  result TEXT,
  applied_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS audit_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
  username TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  detail JSONB NOT NULL DEFAULT '{}'::jsonb
);
