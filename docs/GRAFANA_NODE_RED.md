# Hito 7 - Grafana y Node-RED

Estado: implementado como integracion de demo/provisioning, sin autoridad de control.

## Principio de diseno

Grafana y Node-RED son servicios auxiliares. No escriben variables de salida, no controlan bombas, no escriben a dispositivos de campo y no sustituyen la autoridad CODESYS.

El flujo de control se mantiene asi:

1. operador solicita accion en la web;
2. API valida permisos, rango y auditoria;
3. conector OPC UA escribe la solicitud en el buzon;
4. CODESYS valida interlocks y estado;
5. CODESYS acepta, rechaza y confirma.

Grafana y Node-RED quedan fuera de ese camino.

## Grafana

Archivos:

- `grafana/provisioning/datasources/platform-postgres.yaml`
- `grafana/provisioning/dashboards/dashboards.yaml`
- `grafana/dashboards/column-overview.json`
- `grafana/dashboards/column-trends.json`
- `grafana/dashboards/communications-diagnostics.json`

Dashboards provisionados:

- `column-overview`: resumen operacional de columnas, flujo, calidad y alarmas.
- `column-trends`: peso, flujo, bomba y temperatura por columna.
- `communications-diagnostics`: estado OPC UA, gateways, latencia y eventos de comunicacion.

Restricciones:

- dashboards `editable=false`;
- datasource `editable=false`;
- datasource de PostgreSQL pensado como usuario de solo lectura;
- no hay panels ni acciones que generen comandos;
- no se almacenan secretos de base de datos en Git.

Limitacion:

- los dashboards estan listos para PostgreSQL real, pero en el ambiente actual la plataforma sigue usando store en memoria. Por eso Grafana queda provisionado, no validado contra series historicas reales.

## Node-RED

Archivos:

- `node-red/flows/notifications.json`
- `node-red/settings/settings.js`

Flujos provisionados:

- receptor HTTP de alarmas para preparar notificaciones;
- preparador de reporte diario;
- salida debug para demo;
- comentario de politica operacional.

Restricciones:

- no contiene endpoints de comandos;
- no contiene escrituras Modbus;
- no contiene escritura a CODESYS;
- editor admin deshabilitado por defecto en `docker-compose.demo.yml`;
- la ruta `/node-red-admin/` queda cerrada por el reverse proxy de demo.

Para habilitar administracion en un entorno controlado se debe cambiar la politica de despliegue, configurar autenticacion fuerte y registrar auditoria externa. No debe habilitarse con credenciales embebidas en Git.

## Reverse proxy

Archivo:

- `reverse-proxy/nginx.conf`

Rutas:

- `/` frontend web;
- `/api/` API FastAPI;
- `/ws/` WebSocket API;
- `/grafana/` Grafana;
- `/node-red/` runtime HTTP Node-RED;
- `/node-red-admin/` bloqueado con `403` por defecto.

## API y UI

Endpoints:

- `GET /integrations`
- `GET /integrations/grafana/dashboards`
- `GET /integrations/node-red/flows`

La UI agrega la pestana `Integraciones` para ver estado, dashboards y flows declarados. Los flags `control_allowed=false` se exponen explicitamente.

## Validacion

Pruebas agregadas:

- dashboards provisionados y solo lectura;
- flows sin palabras clave de control;
- proxy con rutas esperadas y editor cerrado;
- API de integraciones sin autoridad de control.

No validado aun:

- arranque real de contenedores Grafana/Node-RED en este ambiente;
- conexion Grafana a PostgreSQL real;
- envio real de correo/Teams desde Node-RED;
- SSO/LDAP/OIDC para administracion de Node-RED.
