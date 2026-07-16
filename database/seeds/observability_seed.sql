INSERT INTO codesys_endpoints (controller_id, endpoint_url, role, is_active, healthy)
VALUES
  ('CODESYS-A', 'opc.tcp://codesys-a:4840', 'primary', true, true),
  ('CODESYS-B', 'opc.tcp://codesys-b:4840', 'secondary', false, true)
ON CONFLICT (controller_id) DO UPDATE
SET is_active = EXCLUDED.is_active,
    healthy = EXCLUDED.healthy,
    last_heartbeat = now();

INSERT INTO gateways (id, name, status, management_ip, ot_ip, real_io_enabled, last_seen_at)
VALUES ('GW-DEMO-01', 'Gateway demo', 'online', '192.168.10.10', '10.10.0.10', false, now())
ON CONFLICT (id) DO UPDATE
SET status = EXCLUDED.status,
    last_seen_at = now();

INSERT INTO gateway_metrics (ts, gateway_id, quality, devices_online, devices_total)
SELECT now() - (n || ' minutes')::interval, 'GW-DEMO-01', 0.96, 4, 4
FROM generate_series(0, 30, 5) AS n;

INSERT INTO opcua_metrics (ts, endpoint, latency_ms, reconnects, quality)
SELECT now() - (n || ' minutes')::interval, 'CODESYS-A', 8 + n * 0.1, 0, 1
FROM generate_series(0, 30, 5) AS n;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'flow_measured_kg_h', 12 + (c % 5) * 0.2, 0.97, 'simulator'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'flow_setpoint_kg_h', 12, 1, 'recipe'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'input_weight_kg', 1000 - n * 0.2 - c, 0.98, 'simulator'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'pump_output_pct', 35 + (c % 7), 0.98, 'simulator'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'temperature_pv_c', 25 + (c % 3) * 0.4, 0.98, 'simulator'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'temperature_setpoint_c', 25, 1, 'recipe'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO historical_series (series_time, column_id, variable, value, quality, source)
SELECT now() - (n || ' minutes')::interval, c, 'data_quality', 0.96, 1, 'simulator'
FROM generate_series(0, 30, 5) AS n
CROSS JOIN generate_series(1, 20) AS c;

INSERT INTO events (source, severity, code, gateway_id, device_id, protocol, message)
VALUES
  ('gateway', 'warning', 'simulated_warning', 'GW-DEMO-01', 'SIM-BAL-IN-001', 'simulated', 'Evento de diagnostico demo'),
  ('opcua-connector', 'info', 'heartbeat', null, null, 'opcua', 'Heartbeat OPC UA demo');
