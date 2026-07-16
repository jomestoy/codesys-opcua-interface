INSERT INTO roles (id, name, permissions) VALUES
  ('admin', 'Administrador', '["*"]'),
  ('operator', 'Operador', '["columns.read", "commands.request"]')
ON CONFLICT (id) DO NOTHING;

INSERT INTO columns (id, block_id, state, flow_setpoint_kg_h)
SELECT n, ((n - 1) / 20) + 1, 'Available', 0
FROM generate_series(1, 200) AS n
ON CONFLICT (id) DO NOTHING;
