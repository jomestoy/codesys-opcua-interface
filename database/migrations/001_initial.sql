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
  display_name TEXT NOT NULL DEFAULT '',
  profile_photo_url TEXT NOT NULL DEFAULT '',
  password_change_required BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS blocks (
  id INTEGER PRIMARY KEY CHECK (id BETWEEN 1 AND 10),
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS columns (
  id INTEGER PRIMARY KEY CHECK (id BETWEEN 1 AND 200),
  block_id INTEGER NOT NULL REFERENCES blocks(id),
  state TEXT NOT NULL,
  flow_setpoint_kg_h NUMERIC NOT NULL DEFAULT 0,
  flow_measured_kg_h NUMERIC NOT NULL DEFAULT 0,
  pump_output_pct NUMERIC NOT NULL DEFAULT 0,
  input_weight_kg NUMERIC NOT NULL DEFAULT 0,
  output_weight_kg NUMERIC NOT NULL DEFAULT 0,
  temperature_pv_c NUMERIC NOT NULL DEFAULT 0,
  data_quality NUMERIC NOT NULL DEFAULT 0,
  recipe_id TEXT,
  campaign_id TEXT,
  gateway_id TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recipes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version INTEGER NOT NULL,
  status TEXT NOT NULL,
  flow_setpoint_kg_h NUMERIC NOT NULL,
  temperature_setpoint_c NUMERIC NOT NULL,
  aeration_enabled BOOLEAN NOT NULL DEFAULT true,
  created_by TEXT NOT NULL,
  base_recipe_id TEXT,
  change_note TEXT NOT NULL DEFAULT '',
  approved_by TEXT,
  approved_at TIMESTAMPTZ,
  rejected_by TEXT,
  rejected_reason TEXT NOT NULL DEFAULT '',
  obsoleted_by TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (name, version)
);

CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  recipe_id TEXT NOT NULL REFERENCES recipes(id),
  column_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_by TEXT NOT NULL,
  scheduled_start TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  notes TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
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

CREATE TABLE IF NOT EXISTS alarms (
  id TEXT PRIMARY KEY,
  column_id INTEGER NOT NULL REFERENCES columns(id),
  severity TEXT NOT NULL,
  code TEXT NOT NULL,
  message TEXT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT true,
  acknowledged_by TEXT,
  acknowledged_at TIMESTAMPTZ,
  comment TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT 'application',
  cleared_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alarm_rules (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  variable TEXT NOT NULL,
  operator TEXT NOT NULL,
  threshold NUMERIC NOT NULL,
  hysteresis NUMERIC NOT NULL DEFAULT 0,
  delay_s INTEGER NOT NULL DEFAULT 0,
  priority TEXT NOT NULL,
  action TEXT NOT NULL,
  target_scope TEXT NOT NULL,
  column_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  enabled BOOLEAN NOT NULL DEFAULT true,
  version INTEGER NOT NULL DEFAULT 1,
  created_by TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alarm_history (
  id BIGSERIAL PRIMARY KEY,
  alarm_id TEXT NOT NULL REFERENCES alarms(id),
  username TEXT NOT NULL,
  action TEXT NOT NULL,
  comment TEXT NOT NULL DEFAULT '',
  event_time TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
  username TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  detail JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS gateways (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  management_ip TEXT,
  ot_ip TEXT,
  real_io_enabled BOOLEAN NOT NULL DEFAULT false,
  last_seen_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  gateway_id TEXT NOT NULL REFERENCES gateways(id),
  name TEXT NOT NULL,
  protocol TEXT NOT NULL,
  endpoint JSONB NOT NULL DEFAULT '{}'::jsonb,
  safe_state JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS io_maps (
  id TEXT PRIMARY KEY,
  column_id INTEGER REFERENCES columns(id),
  logical_variable TEXT NOT NULL,
  device_id TEXT NOT NULL REFERENCES devices(id),
  address JSONB NOT NULL DEFAULT '{}'::jsonb,
  scale JSONB NOT NULL DEFAULT '{}'::jsonb,
  unit TEXT NOT NULL DEFAULT '',
  enabled BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS historical_series (
  id BIGSERIAL PRIMARY KEY,
  series_time TIMESTAMPTZ NOT NULL,
  column_id INTEGER REFERENCES columns(id),
  variable TEXT NOT NULL,
  value NUMERIC NOT NULL,
  quality NUMERIC NOT NULL DEFAULT 1,
  source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_events (
  id BIGSERIAL PRIMARY KEY,
  column_id INTEGER REFERENCES columns(id),
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  description TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  report_type TEXT NOT NULL,
  parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS configurations (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_by TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
