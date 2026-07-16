INSERT INTO roles (id, name, permissions) VALUES
  ('admin', 'Administrador', '["*"]'),
  ('engineer', 'Ingeniero', '["columns.read", "commands.request", "recipes.read", "recipes.manage", "recipes.approve", "campaigns.read", "campaigns.manage", "alarms.read", "alarms.manage", "users.read", "audit.read", "system.read"]'),
  ('supervisor', 'Supervisor', '["columns.read", "commands.request", "recipes.read", "campaigns.read", "campaigns.manage", "alarms.read", "alarms.ack", "audit.read", "system.read"]'),
  ('operator', 'Operador', '["columns.read", "commands.request", "recipes.read", "campaigns.read", "alarms.read", "alarms.ack", "system.read"]'),
  ('maintenance', 'Mantenimiento', '["columns.read", "commands.request", "maintenance.manage", "devices.read", "system.read"]'),
  ('viewer', 'Visualizador', '["columns.read", "recipes.read", "campaigns.read", "alarms.read", "system.read"]')
ON CONFLICT (id) DO NOTHING;

INSERT INTO blocks (id, name, description)
SELECT n, 'Bloque ' || n, 'Bloque demo de 20 columnas'
FROM generate_series(1, 10) AS n
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipes (id, name, version, status, flow_setpoint_kg_h, temperature_setpoint_c, aeration_enabled, created_by, approved_by, approved_at)
VALUES ('REC-DEMO-001', 'Receta demo sulfato', 1, 'approved', 12, 25, true, 'admin', 'admin', now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO campaigns (id, name, status, recipe_id, column_ids, created_by, started_at)
VALUES ('CAM-DEMO-001', 'Campaña demo bloque 1', 'running', 'REC-DEMO-001', '[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]'::jsonb, 'admin', now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO columns (id, block_id, state, flow_setpoint_kg_h)
SELECT n, ((n - 1) / 20) + 1, 'Available', 0
FROM generate_series(1, 200) AS n
ON CONFLICT (id) DO NOTHING;

INSERT INTO alarms (id, column_id, severity, code, message)
VALUES ('ALM-DEMO-042', 42, 'critical', 'SCALE_OFFLINE', 'Balanza de entrada sin comunicacion')
ON CONFLICT (id) DO NOTHING;

INSERT INTO alarm_rules (id, name, variable, operator, threshold, hysteresis, delay_s, priority, action, target_scope, column_ids, enabled, version, created_by)
VALUES ('AR-DEMO-FLOW', 'Flujo bajo demo', 'flow_measured_kg_h', 'lt', 8, 0.5, 30, 'warning', 'notify', 'all', '[]'::jsonb, true, 1, 'admin')
ON CONFLICT (id) DO NOTHING;
