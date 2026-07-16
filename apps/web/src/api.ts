import type { Alarm, AlarmRule, AuditEvent, Campaign, Column, Recipe, Summary, User } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export type Session = {
  access_token: string;
  user: User;
};

async function request<T>(path: string, token?: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  demoCredentials: () => request<Record<string, string>>("/auth/demo-credentials"),
  login: (username: string, password: string) =>
    request<Session>("/auth/login", undefined, { method: "POST", body: JSON.stringify({ username, password }) }),
  me: (token: string) => request<User>("/auth/me", token),
  changePassword: (token: string, username: string | null, newPassword: string) =>
    request<{ status: string }>("/auth/change-password", token, {
      method: "POST",
      body: JSON.stringify({ username, new_password: newPassword })
    }),
  summary: (token: string) => request<Summary>("/system/summary", token),
  columns: (token: string, blockId?: number) =>
    request<Column[]>(blockId ? `/columns?block_id=${blockId}` : "/columns", token),
  column: (token: string, id: number) => request<Column>(`/columns/${id}`, token),
  command: (token: string, columnId: number, commandType: string, requestedValue?: number | string | boolean) =>
    request<Record<string, unknown>>("/commands", token, {
      method: "POST",
      body: JSON.stringify({ column_id: columnId, command_type: commandType, requested_value: requestedValue })
    }),
  recipes: (token: string) => request<Recipe[]>("/recipes", token),
  createRecipe: (token: string, payload: Partial<Recipe>) =>
    request<Recipe>("/recipes", token, { method: "POST", body: JSON.stringify(payload) }),
  updateRecipe: (token: string, id: string, payload: Partial<Recipe>) =>
    request<Recipe>(`/recipes/${id}`, token, { method: "PATCH", body: JSON.stringify(payload) }),
  cloneRecipe: (token: string, id: string, payload: { name?: string; change_note?: string }) =>
    request<Recipe>(`/recipes/${id}/clone`, token, { method: "POST", body: JSON.stringify(payload) }),
  approveRecipe: (token: string, id: string) => request<Recipe>(`/recipes/${id}/approve`, token, { method: "POST" }),
  rejectRecipe: (token: string, id: string, reason: string) =>
    request<Recipe>(`/recipes/${id}/reject`, token, { method: "POST", body: JSON.stringify({ reason }) }),
  obsoleteRecipe: (token: string, id: string) => request<Recipe>(`/recipes/${id}/obsolete`, token, { method: "POST" }),
  assignRecipe: (token: string, id: string, columnIds: number[]) =>
    request<{ recipe_id: string; column_ids: number[] }>(`/recipes/${id}/assign`, token, {
      method: "POST",
      body: JSON.stringify({ column_ids: columnIds })
    }),
  compareRecipes: (token: string, leftId: string, rightId: string) =>
    request<Record<string, unknown>>(`/recipes/compare?left_id=${leftId}&right_id=${rightId}`, token),
  campaigns: (token: string) => request<Campaign[]>("/campaigns", token),
  createCampaign: (token: string, payload: { name: string; recipe_id: string; column_ids: number[] }) =>
    request<Campaign>("/campaigns", token, { method: "POST", body: JSON.stringify(payload) }),
  scheduleCampaign: (token: string, id: string, scheduledStart: string | null) =>
    request<Campaign>(`/campaigns/${id}/schedule`, token, {
      method: "POST",
      body: JSON.stringify({ scheduled_start: scheduledStart })
    }),
  startCampaign: (token: string, id: string) => request<Campaign>(`/campaigns/${id}/start`, token, { method: "POST" }),
  pauseCampaign: (token: string, id: string) => request<Campaign>(`/campaigns/${id}/pause`, token, { method: "POST" }),
  finishCampaign: (token: string, id: string) => request<Campaign>(`/campaigns/${id}/finish`, token, { method: "POST" }),
  cancelCampaign: (token: string, id: string, reason: string) =>
    request<Campaign>(`/campaigns/${id}/cancel`, token, { method: "POST", body: JSON.stringify({ reason }) }),
  exportCampaign: (token: string, id: string) => request<Record<string, unknown>>(`/campaigns/${id}/export`, token),
  alarms: (token: string) => request<Alarm[]>("/alarms", token),
  ackAlarm: (token: string, id: string, comment = "") =>
    request<Alarm>(`/alarms/${id}/ack`, token, { method: "POST", body: JSON.stringify({ comment }) }),
  clearAlarm: (token: string, id: string, comment = "") =>
    request<Alarm>(`/alarms/${id}/clear`, token, { method: "POST", body: JSON.stringify({ comment }) }),
  alarmRules: (token: string) => request<AlarmRule[]>("/alarm-rules", token),
  createAlarmRule: (token: string, payload: Partial<AlarmRule>) =>
    request<AlarmRule>("/alarm-rules", token, { method: "POST", body: JSON.stringify(payload) }),
  evaluateAlarmRules: (token: string) => request<Alarm[]>("/alarm-rules/evaluate", token, { method: "POST" }),
  exportAlarms: (token: string) => request<Record<string, unknown>>("/alarms/export", token),
  audit: (token: string) => request<AuditEvent[]>("/audit", token),
  users: (token: string) => request<User[]>("/users", token),
  createUser: (token: string, payload: { username: string; display_name: string; role_id: string; temporary_password: string }) =>
    request<User>("/users", token, { method: "POST", body: JSON.stringify(payload) }),
  updateProfile: (token: string, username: string, payload: { display_name?: string; profile_photo_url?: string }) =>
    request<User>(`/users/${username}/profile`, token, { method: "PATCH", body: JSON.stringify(payload) })
};
