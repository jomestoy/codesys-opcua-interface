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
  approved_by?: string | null;
};

export type Campaign = {
  id: string;
  name: string;
  status: string;
  recipe_id: string;
  column_ids: number[];
  created_by: string;
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
};

export type AuditEvent = {
  id: number;
  username: string;
  action: string;
  target: string;
  detail: Record<string, unknown>;
  event_time: string;
};
