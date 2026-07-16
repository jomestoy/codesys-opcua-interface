export type Role = {
  id: string;
  name: string;
  permissions: string[];
};

export type User = {
  id: string;
  username: string;
  display_name: string;
  role: Role;
  active: boolean;
  password_change_required: boolean;
  profile_photo_url: string;
};

export type Summary = {
  columns_total: number;
  running: number;
  paused: number;
  alarm: number;
  offline: number;
  available: number;
  active_campaigns: number;
  flow_total_kg_h: number;
  data_quality: number;
  real_io_enabled: boolean;
  codesys: {
    primary: { controller_id: string; role: string; active: boolean; healthy: boolean };
    secondary: { controller_id: string; role: string; active: boolean; healthy: boolean };
  };
  gateways: Array<{ gateway_id: string; online: boolean; quality: number }>;
  critical_alarms: number;
};

export type Column = {
  id: number;
  block_id: number;
  state: string;
  flow_setpoint_kg_h: number;
  flow_measured_kg_h: number;
  pump_output_pct: number;
  input_weight_kg: number;
  output_weight_kg: number;
  temperature_pv_c: number;
  data_quality: number;
  recipe_id?: string | null;
  campaign_id?: string | null;
  gateway_id: string;
  codesys_controller: string;
};

export type Recipe = {
  id: string;
  name: string;
  version: number;
  status: string;
  flow_setpoint_kg_h: number;
  temperature_setpoint_c: number;
  aeration_enabled: boolean;
  created_by: string;
  base_recipe_id?: string | null;
  change_note: string;
  approved_by?: string | null;
  approved_at?: string | null;
  rejected_by?: string | null;
  rejected_reason: string;
  obsoleted_by?: string | null;
};

export type Campaign = {
  id: string;
  name: string;
  status: string;
  recipe_id: string;
  column_ids: number[];
  created_by: string;
  scheduled_start?: string | null;
  started_at?: string | null;
  paused_at?: string | null;
  finished_at?: string | null;
  cancelled_at?: string | null;
  notes: string;
};

export type Alarm = {
  id: string;
  column_id: number;
  severity: string;
  code: string;
  message: string;
  active: boolean;
  acknowledged_by?: string | null;
  acknowledged_at?: string | null;
  comment: string;
  source: string;
};

export type AlarmRule = {
  id: string;
  name: string;
  variable: string;
  operator: string;
  threshold: number;
  hysteresis: number;
  delay_s: number;
  priority: string;
  action: string;
  target_scope: string;
  column_ids: number[];
  enabled: boolean;
  version: number;
  created_by: string;
};

export type AuditEvent = {
  id: number;
  username: string;
  action: string;
  target: string;
  detail: Record<string, unknown>;
  event_time: string;
};

export type GrafanaDashboard = {
  uid: string;
  title: string;
  path: string;
  editable: boolean;
  tags: string[];
  panels: number;
};

export type NodeRedFlow = {
  id: string;
  label: string;
  path: string;
  disabled: boolean;
  contains_control_keywords: boolean;
};

export type IntegrationStatus = {
  grafana: {
    enabled: boolean;
    base_path: string;
    dashboards: GrafanaDashboard[];
    control_allowed: boolean;
  };
  node_red: {
    enabled: boolean;
    runtime_base_path: string;
    admin_base_path: string;
    flows: NodeRedFlow[];
    control_allowed: boolean;
  };
};
