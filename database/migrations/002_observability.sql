CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'info',
  code TEXT NOT NULL,
  gateway_id TEXT,
  device_id TEXT,
  protocol TEXT,
  message TEXT NOT NULL DEFAULT '',
  detail JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS codesys_endpoints (
  controller_id TEXT PRIMARY KEY,
  endpoint_url TEXT NOT NULL,
  role TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT false,
  healthy BOOLEAN NOT NULL DEFAULT true,
  last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS opcua_metrics (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  endpoint TEXT NOT NULL,
  latency_ms NUMERIC NOT NULL,
  reconnects INTEGER NOT NULL DEFAULT 0,
  quality NUMERIC NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS gateway_metrics (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  gateway_id TEXT NOT NULL,
  quality NUMERIC NOT NULL DEFAULT 1,
  devices_online INTEGER NOT NULL DEFAULT 0,
  devices_total INTEGER NOT NULL DEFAULT 0
);
