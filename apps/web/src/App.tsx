import { useState, type ReactNode } from "react";
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Grid,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Toolbar,
  Typography
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Session } from "./api";
import type { Alarm, AlarmRule, Campaign, Column, Recipe, Summary, User } from "./types";

const sessionKey = "codesys-platform-session";

export default function App() {
  const [session, setSession] = useState<Session | null>(() => {
    const raw = localStorage.getItem(sessionKey);
    return raw ? (JSON.parse(raw) as Session) : null;
  });

  if (!session) {
    return <LoginPage onLogin={(next) => {
      localStorage.setItem(sessionKey, JSON.stringify(next));
      setSession(next);
    }} />;
  }

  return <Shell session={session} onLogout={() => {
    localStorage.removeItem(sessionKey);
    setSession(null);
  }} />;
}

function LoginPage({ onLogin }: { onLogin: (session: Session) => void }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const login = useMutation({
    mutationFn: () => api.login(username, password),
    onSuccess: onLogin,
    onError: (err) => setError(err instanceof Error ? err.message : "Error de login")
  });
  const demo = useMutation({
    mutationFn: api.demoCredentials,
    onSuccess: (credentials) => {
      setUsername("admin");
      setPassword(credentials.admin ?? "");
    }
  });

  return (
    <Box className="login-page">
      <Card className="login-card">
        <CardContent>
          <Stack spacing={3}>
            <Box>
              <Typography variant="overline" color="secondary">Bureau Veritas</Typography>
              <Typography variant="h5">Plataforma CODESYS OPC UA</Typography>
              <Typography color="text.secondary">Acceso limitado por credenciales y permisos.</Typography>
            </Box>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField label="Usuario" value={username} onChange={(event) => setUsername(event.target.value)} fullWidth />
            <TextField
              label="Contraseña"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              fullWidth
            />
            <Stack direction="row" spacing={1}>
              <Button variant="contained" onClick={() => login.mutate()} disabled={login.isPending}>Ingresar</Button>
              <Button variant="outlined" onClick={() => demo.mutate()} disabled={demo.isPending}>Usar demo</Button>
            </Stack>
            <Alert severity="info">
              En demo, las credenciales temporales se generan en runtime. No hay contraseñas reales guardadas en Git.
            </Alert>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}

function Shell({ session, onLogout }: { session: Session; onLogout: () => void }) {
  const [tab, setTab] = useState(0);
  const token = session.access_token;

  return (
    <Box>
      <AppBar position="sticky" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>BV Column Control</Typography>
          <Chip color="secondary" label={session.user.role.name} sx={{ mr: 2 }} />
          <Avatar src={session.user.profile_photo_url} sx={{ mr: 1 }}>{session.user.display_name[0]}</Avatar>
          <Typography sx={{ mr: 2 }}>{session.user.display_name}</Typography>
          <Button color="inherit" onClick={onLogout}>Salir</Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Tabs value={tab} onChange={(_, value) => setTab(value)} variant="scrollable" scrollButtons="auto">
          <Tab label="Resumen" />
          <Tab label="Planta" />
          <Tab label="Recetas" />
          <Tab label="Campañas" />
          <Tab label="Alarmas" />
          <Tab label="Usuarios" />
          <Tab label="Auditoría" />
        </Tabs>
        <TabPanel value={tab} index={0}><SummaryView token={token} /></TabPanel>
        <TabPanel value={tab} index={1}><PlantView token={token} /></TabPanel>
        <TabPanel value={tab} index={2}><RecipesView token={token} /></TabPanel>
        <TabPanel value={tab} index={3}><CampaignsView token={token} /></TabPanel>
        <TabPanel value={tab} index={4}><AlarmsView token={token} /></TabPanel>
        <TabPanel value={tab} index={5}><UsersView token={token} currentUser={session.user} /></TabPanel>
        <TabPanel value={tab} index={6}><AuditView token={token} /></TabPanel>
      </Container>
    </Box>
  );
}

function SummaryView({ token }: { token: string }) {
  const { data, isLoading, error } = useQuery({ queryKey: ["summary", token], queryFn: () => api.summary(token) });
  if (isLoading) return <LinearProgress />;
  if (error || !data) return <Alert severity="error">No se pudo cargar el resumen.</Alert>;
  return (
    <Stack spacing={3}>
      <Grid container spacing={2}>
        <Metric title="Columnas" value={data.columns_total} />
        <Metric title="Ejecutando" value={data.running} color="success" />
        <Metric title="Alarmas" value={data.alarm} color="error" />
        <Metric title="Flujo total kg/h" value={data.flow_total_kg_h.toFixed(1)} />
        <Metric title="Calidad datos" value={`${Math.round(data.data_quality * 100)}%`} />
        <Metric title="Campañas activas" value={data.active_campaigns} />
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <StatusCard title="CODESYS primario" data={data.codesys.primary} />
        </Grid>
        <Grid item xs={12} md={6}>
          <StatusCard title="CODESYS secundario" data={data.codesys.secondary} />
        </Grid>
      </Grid>
      <Alert severity={data.real_io_enabled ? "warning" : "info"}>
        REAL_IO_ENABLED={String(data.real_io_enabled)}. En demo debe permanecer en false.
      </Alert>
    </Stack>
  );
}

function PlantView({ token }: { token: string }) {
  const [blockId, setBlockId] = useState(1);
  const [selectedId, setSelectedId] = useState(1);
  const queryClient = useQueryClient();
  const columns = useQuery({ queryKey: ["columns", token, blockId], queryFn: () => api.columns(token, blockId) });
  const selected = useQuery({ queryKey: ["column", token, selectedId], queryFn: () => api.column(token, selectedId), enabled: !!selectedId });
  const command = useMutation({
    mutationFn: ({ type, value }: { type: string; value?: number }) => api.command(token, selectedId, type, value),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["columns"] });
      queryClient.invalidateQueries({ queryKey: ["column"] });
      queryClient.invalidateQueries({ queryKey: ["summary"] });
    }
  });
  const [setpoint, setSetpoint] = useState("12");

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} lg={8}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Vista general de planta</Typography>
            <TextField select size="small" label="Bloque" value={blockId} onChange={(event) => setBlockId(Number(event.target.value))}>
              {Array.from({ length: 10 }, (_, index) => index + 1).map((id) => <MenuItem key={id} value={id}>Bloque {id}</MenuItem>)}
            </TextField>
          </Stack>
          {columns.isLoading ? <LinearProgress /> : (
            <Box className="column-grid">
              {(columns.data ?? []).map((column) => (
                <Button
                  key={column.id}
                  variant={column.id === selectedId ? "contained" : "outlined"}
                  color={stateColor(column.state)}
                  onClick={() => setSelectedId(column.id)}
                >
                  C{column.id.toString().padStart(3, "0")}
                  <small>{column.state}</small>
                </Button>
              ))}
            </Box>
          )}
        </Paper>
      </Grid>
      <Grid item xs={12} lg={4}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Detalle columna {selectedId}</Typography>
          {selected.isLoading || !selected.data ? <LinearProgress /> : <ColumnDetail column={selected.data} />}
          <Divider sx={{ my: 2 }} />
          <Stack spacing={1}>
            <Stack direction="row" spacing={1}>
              <Button variant="contained" onClick={() => command.mutate({ type: "start" })}>Iniciar</Button>
              <Button variant="outlined" onClick={() => command.mutate({ type: "pause" })}>Pausar</Button>
              <Button color="warning" variant="outlined" onClick={() => command.mutate({ type: "stop" })}>Detener</Button>
            </Stack>
            <Stack direction="row" spacing={1}>
              <TextField size="small" label="SP flujo kg/h" value={setpoint} onChange={(event) => setSetpoint(event.target.value)} />
              <Button onClick={() => command.mutate({ type: "set_flow", value: Number(setpoint) })}>Aplicar SP</Button>
            </Stack>
            {command.data && <Alert severity="success">Comando: {String(command.data.Status)} · {String(command.data.Result)}</Alert>}
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );
}

function RecipesView({ token }: { token: string }) {
  const queryClient = useQueryClient();
  const recipes = useQuery({ queryKey: ["recipes", token], queryFn: () => api.recipes(token) });
  const [name, setName] = useState("Nueva receta");
  const [flow, setFlow] = useState("12");
  const [assignColumns, setAssignColumns] = useState("1,2,3");
  const [comparison, setComparison] = useState<Record<string, unknown> | null>(null);
  const create = useMutation({
    mutationFn: () => api.createRecipe(token, { name, flow_setpoint_kg_h: Number(flow), temperature_setpoint_c: 25, aeration_enabled: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] })
  });
  const clone = useMutation({
    mutationFn: (id: string) => api.cloneRecipe(token, id, { change_note: "clonada desde UI" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] })
  });
  const approve = useMutation({
    mutationFn: (id: string) => api.approveRecipe(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] })
  });
  const reject = useMutation({
    mutationFn: (id: string) => api.rejectRecipe(token, id, "rechazada desde UI para revision"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] })
  });
  const obsolete = useMutation({
    mutationFn: (id: string) => api.obsoleteRecipe(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] })
  });
  const assign = useMutation({
    mutationFn: (id: string) => api.assignRecipe(token, id, parseCsvNumbers(assignColumns)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["columns"] })
  });
  const compareFirstTwo = async () => {
    const items = recipes.data ?? [];
    if (items.length >= 2) setComparison(await api.compareRecipes(token, items[0].id, items[1].id));
  };
  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Crear receta</Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ mt: 1 }}>
          <TextField label="Nombre" value={name} onChange={(event) => setName(event.target.value)} />
          <TextField label="Flujo kg/h" value={flow} onChange={(event) => setFlow(event.target.value)} />
          <TextField label="Columnas asignación" value={assignColumns} onChange={(event) => setAssignColumns(event.target.value)} />
          <Button variant="contained" onClick={() => create.mutate()}>Crear borrador</Button>
          <Button variant="outlined" onClick={compareFirstTwo}>Comparar 2 primeras</Button>
        </Stack>
      </Paper>
      {comparison && <Alert severity="info">Comparación: {JSON.stringify(comparison["differences"])}</Alert>}
      <DataTable
        rows={recipes.data ?? []}
        columns={["id", "name", "version", "status", "flow_setpoint_kg_h", "approved_by", "rejected_reason"]}
        renderActions={(recipe: Recipe) => (
          <Stack direction="row" spacing={1}>
            <Button onClick={() => clone.mutate(recipe.id)}>Clonar</Button>
            {recipe.status !== "approved" && <Button onClick={() => approve.mutate(recipe.id)}>Aprobar</Button>}
            {recipe.status !== "rejected" && recipe.status !== "obsolete" && <Button onClick={() => reject.mutate(recipe.id)}>Rechazar</Button>}
            {recipe.status === "approved" && <Button color="warning" onClick={() => obsolete.mutate(recipe.id)}>Obsoletar</Button>}
            {recipe.status === "approved" && <Button onClick={() => assign.mutate(recipe.id)}>Asignar</Button>}
          </Stack>
        )}
      />
    </Stack>
  );
}

function CampaignsView({ token }: { token: string }) {
  const queryClient = useQueryClient();
  const campaigns = useQuery({ queryKey: ["campaigns", token], queryFn: () => api.campaigns(token) });
  const recipes = useQuery({ queryKey: ["recipes", token], queryFn: () => api.recipes(token) });
  const [name, setName] = useState("Nueva campaña");
  const [recipeId, setRecipeId] = useState("REC-DEMO-001");
  const [columns, setColumns] = useState("1,2,3");
  const [scheduledStart, setScheduledStart] = useState("2026-07-20T08:00:00Z");
  const [campaignExport, setCampaignExport] = useState<Record<string, unknown> | null>(null);
  const create = useMutation({
    mutationFn: () => api.createCampaign(token, {
      name,
      recipe_id: recipeId,
      column_ids: parseCsvNumbers(columns)
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const schedule = useMutation({
    mutationFn: (id: string) => api.scheduleCampaign(token, id, scheduledStart),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const start = useMutation({
    mutationFn: (id: string) => api.startCampaign(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const pause = useMutation({
    mutationFn: (id: string) => api.pauseCampaign(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const finish = useMutation({
    mutationFn: (id: string) => api.finishCampaign(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const cancel = useMutation({
    mutationFn: (id: string) => api.cancelCampaign(token, id, "cancelada desde UI"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
  const exportCampaign = async (id: string) => setCampaignExport(await api.exportCampaign(token, id));
  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Crear campaña</Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ mt: 1 }}>
          <TextField label="Nombre" value={name} onChange={(event) => setName(event.target.value)} />
          <TextField select label="Receta" value={recipeId} onChange={(event) => setRecipeId(event.target.value)} sx={{ minWidth: 220 }}>
            {(recipes.data ?? []).filter((recipe) => recipe.status === "approved").map((recipe) => (
              <MenuItem key={recipe.id} value={recipe.id}>{recipe.name}</MenuItem>
            ))}
          </TextField>
          <TextField label="Columnas CSV" value={columns} onChange={(event) => setColumns(event.target.value)} />
          <TextField label="Programación ISO" value={scheduledStart} onChange={(event) => setScheduledStart(event.target.value)} />
          <Button variant="contained" onClick={() => create.mutate()}>Crear</Button>
        </Stack>
      </Paper>
      {campaignExport && <Alert severity="info">Export campaña: {JSON.stringify(campaignExport["summary"])}</Alert>}
      <DataTable
        rows={campaigns.data ?? []}
        columns={["id", "name", "status", "recipe_id", "column_ids", "scheduled_start"]}
        renderActions={(campaign: Campaign) => (
          <Stack direction="row" spacing={1}>
            <Button onClick={() => schedule.mutate(campaign.id)}>Programar</Button>
            {campaign.status !== "running" && <Button onClick={() => start.mutate(campaign.id)}>Iniciar</Button>}
            {campaign.status === "running" && <Button onClick={() => pause.mutate(campaign.id)}>Pausar</Button>}
            {campaign.status !== "finished" && <Button onClick={() => finish.mutate(campaign.id)}>Finalizar</Button>}
            {campaign.status !== "cancelled" && <Button color="warning" onClick={() => cancel.mutate(campaign.id)}>Cancelar</Button>}
            <Button onClick={() => exportCampaign(campaign.id)}>Exportar</Button>
          </Stack>
        )}
      />
    </Stack>
  );
}

function AlarmsView({ token }: { token: string }) {
  const queryClient = useQueryClient();
  const alarms = useQuery({ queryKey: ["alarms", token], queryFn: () => api.alarms(token) });
  const rules = useQuery({ queryKey: ["alarm-rules", token], queryFn: () => api.alarmRules(token) });
  const [ruleName, setRuleName] = useState("Calidad baja");
  const [threshold, setThreshold] = useState("0.5");
  const [targetColumns, setTargetColumns] = useState("42");
  const ack = useMutation({
    mutationFn: (id: string) => api.ackAlarm(token, id, "Reconocida desde UI"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alarms"] })
  });
  const clear = useMutation({
    mutationFn: (id: string) => api.clearAlarm(token, id, "Limpieza desde UI"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alarms"] })
  });
  const createRule = useMutation({
    mutationFn: () => api.createAlarmRule(token, {
      name: ruleName,
      variable: "data_quality",
      operator: "lt",
      threshold: Number(threshold),
      priority: "critical",
      action: "notify",
      target_scope: "columns",
      column_ids: parseCsvNumbers(targetColumns),
      enabled: true
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alarm-rules"] })
  });
  const evaluate = useMutation({
    mutationFn: () => api.evaluateAlarmRules(token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alarms"] });
      queryClient.invalidateQueries({ queryKey: ["alarm-rules"] });
    }
  });
  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Configuración de alarmas</Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ mt: 1 }}>
          <TextField label="Nombre regla" value={ruleName} onChange={(event) => setRuleName(event.target.value)} />
          <TextField label="Umbral calidad" value={threshold} onChange={(event) => setThreshold(event.target.value)} />
          <TextField label="Columnas CSV" value={targetColumns} onChange={(event) => setTargetColumns(event.target.value)} />
          <Button variant="contained" onClick={() => createRule.mutate()}>Crear regla</Button>
          <Button variant="outlined" onClick={() => evaluate.mutate()}>Evaluar reglas</Button>
        </Stack>
      </Paper>
      <DataTable rows={rules.data ?? []} columns={["id", "name", "variable", "operator", "threshold", "priority", "target_scope", "version", "enabled"]} />
      <DataTable
        rows={alarms.data ?? []}
        columns={["id", "column_id", "severity", "code", "message", "active", "acknowledged_by", "comment"]}
        renderActions={(alarm: Alarm) => (
          <Stack direction="row" spacing={1}>
            {alarm.active && !alarm.acknowledged_by && <Button onClick={() => ack.mutate(alarm.id)}>Reconocer</Button>}
            {alarm.active && <Button color="warning" onClick={() => clear.mutate(alarm.id)}>Limpiar</Button>}
          </Stack>
        )}
      />
    </Stack>
  );
}

function UsersView({ token, currentUser }: { token: string; currentUser: User }) {
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: ["users", token], queryFn: () => api.users(token) });
  const [username, setUsername] = useState("nuevo.usuario");
  const [displayName, setDisplayName] = useState("Nuevo Usuario");
  const [roleId, setRoleId] = useState("viewer");
  const [password, setPassword] = useState("Temporal!2026");
  const [photo, setPhoto] = useState(currentUser.profile_photo_url ?? "");
  const create = useMutation({
    mutationFn: () => api.createUser(token, { username, display_name: displayName, role_id: roleId, temporary_password: password }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] })
  });
  const updateProfile = useMutation({
    mutationFn: () => api.updateProfile(token, currentUser.username, { profile_photo_url: photo }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] })
  });
  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Perfil</Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ mt: 1 }}>
          <TextField label="URL foto perfil" value={photo} onChange={(event) => setPhoto(event.target.value)} fullWidth />
          <Button variant="outlined" onClick={() => updateProfile.mutate()}>Guardar foto</Button>
        </Stack>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Crear usuario</Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ mt: 1 }}>
          <TextField label="Usuario" value={username} onChange={(event) => setUsername(event.target.value)} />
          <TextField label="Nombre" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
          <TextField select label="Rol" value={roleId} onChange={(event) => setRoleId(event.target.value)} sx={{ minWidth: 180 }}>
            {["admin", "engineer", "supervisor", "operator", "maintenance", "viewer"].map((role) => <MenuItem key={role} value={role}>{role}</MenuItem>)}
          </TextField>
          <TextField label="Contraseña temporal" value={password} onChange={(event) => setPassword(event.target.value)} />
          <Button variant="contained" onClick={() => create.mutate()}>Crear</Button>
        </Stack>
      </Paper>
      <DataTable rows={users.data ?? []} columns={["username", "display_name", "active", "password_change_required"]} />
    </Stack>
  );
}

function AuditView({ token }: { token: string }) {
  const audit = useQuery({ queryKey: ["audit", token], queryFn: () => api.audit(token) });
  return <DataTable rows={audit.data ?? []} columns={["id", "event_time", "username", "action", "target"]} />;
}

function ColumnDetail({ column }: { column: Column }) {
  return (
    <Stack spacing={1} sx={{ mt: 2 }}>
      <Chip label={column.state} color={stateColor(column.state)} />
      <Typography>Receta: {column.recipe_id ?? "sin asignar"}</Typography>
      <Typography>Campaña: {column.campaign_id ?? "sin asignar"}</Typography>
      <Typography>Peso entrada: {column.input_weight_kg.toFixed(2)} kg</Typography>
      <Typography>Peso salida: {column.output_weight_kg.toFixed(2)} kg</Typography>
      <Typography>Flujo PV/SP: {column.flow_measured_kg_h.toFixed(2)} / {column.flow_setpoint_kg_h.toFixed(2)} kg/h</Typography>
      <Typography>Bomba: {column.pump_output_pct.toFixed(1)}%</Typography>
      <Typography>Temperatura: {column.temperature_pv_c.toFixed(1)} °C</Typography>
      <Typography>Gateway: {column.gateway_id}</Typography>
      <Typography>CODESYS: {column.codesys_controller}</Typography>
      <LinearProgress variant="determinate" value={column.data_quality * 100} />
    </Stack>
  );
}

function Metric({ title, value, color = "primary" }: { title: string; value: number | string; color?: "primary" | "success" | "error" }) {
  return (
    <Grid item xs={12} sm={6} md={4} lg={2}>
      <Card>
        <CardContent>
          <Typography color="text.secondary">{title}</Typography>
          <Typography variant="h5" color={`${color}.main`}>{value}</Typography>
        </CardContent>
      </Card>
    </Grid>
  );
}

function StatusCard({ title, data }: { title: string; data: Summary["codesys"]["primary"] }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        <Typography>{data.controller_id} · {data.role}</Typography>
        <Chip label={data.active ? "Activo" : "Standby"} color={data.active ? "success" : "default"} sx={{ mr: 1 }} />
        <Chip label={data.healthy ? "Salud OK" : "Degradado"} color={data.healthy ? "success" : "error"} />
      </CardContent>
    </Card>
  );
}

function DataTable<T>({
  rows,
  columns,
  renderActions
}: {
  rows: T[];
  columns: string[];
  renderActions?: (row: T) => ReactNode;
}) {
  return (
    <Paper sx={{ overflowX: "auto" }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            {columns.map((column) => <TableCell key={column}>{column}</TableCell>)}
            {renderActions && <TableCell>Acciones</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row, index) => (
            <TableRow key={String((row as Record<string, unknown>).id ?? (row as Record<string, unknown>).username ?? index)}>
              {columns.map((column) => <TableCell key={column}>{formatCell((row as Record<string, unknown>)[column])}</TableCell>)}
              {renderActions && <TableCell>{renderActions(row)}</TableCell>}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
}

function TabPanel({ value, index, children }: { value: number; index: number; children: ReactNode }) {
  return <Box hidden={value !== index} sx={{ py: 3 }}>{value === index && children}</Box>;
}

function stateColor(state: string): "success" | "warning" | "error" | "info" | "primary" {
  if (state === "Running") return "success";
  if (state === "Paused") return "warning";
  if (state === "Alarm") return "error";
  if (state === "Offline") return "info";
  return "primary";
}

function formatCell(value: unknown): string {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "boolean") return value ? "sí" : "no";
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function parseCsvNumbers(value: string): number[] {
  return value.split(",").map((item) => Number(item.trim())).filter(Boolean);
}
