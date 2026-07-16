# CODESYS OPC UA Platform

Plataforma operacional para control de columnas con CODESYS como autoridad final, comunicacion OPC UA segura y gateway Linux separado para campo.

Estado actual: prototipo offline integrado hasta Hito 8.

## Principios de seguridad

- `REAL_IO_ENABLED=false` por defecto.
- La web no escribe equipos de campo.
- La API solicita comandos a CODESYS mediante buzon OPC UA.
- CODESYS acepta, rechaza y confirma comandos.
- Grafana y Node-RED no controlan equipos.
- E-Stop y protecciones criticas deben ser fisicas e independientes.

## Componentes implementados

- Perfil y validacion OPC UA.
- Conector OPC UA con primario/secundario simulado.
- Modelo de comandos con TTL, sequence e idempotencia.
- Fuente CODESYS Structured Text para 200 columnas.
- PLCopen XML preliminar.
- API FastAPI offline.
- Usuarios, roles y permisos.
- Recetas, campanas, alarmas y auditoria con flujos Hito 5.
- Frontend React/Vite/MUI como fuente.
- Migracion SQL inicial ampliada.
- Grafana provisionado con dashboards de solo lectura.
- Node-RED provisionado para notificaciones/reportes, sin control directo.
- Reverse proxy demo con rutas para API, Web, Grafana y Node-RED.
- Docker Compose demo con Web, API, PostgreSQL, Grafana, Node-RED y reverse proxy.
- Backup/restore seguro de configuracion demo.
- Empaquetado gateway delegado al repositorio `column-gateway`.

## Ejecutar pruebas

```powershell
python -m pytest -q
python -m compileall codesys_opcua_interface services tests
```

Resultado ultimo validado:

```text
45 passed
```

## Ejecutar API demo

```powershell
python -m services.api.run
```

Luego abrir:

- API: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`
- credenciales demo: `http://localhost:8000/auth/demo-credentials`

## Ejecutar stack demo Docker

```powershell
make demo
```

Servicios principales:

- Reverse proxy: `http://localhost:8080`
- API: `http://localhost:8000`
- Web Vite: `http://localhost:5173`
- Grafana: `http://localhost:3000`
- Node-RED runtime: `http://localhost:1880/node-red`

La base PostgreSQL usa `POSTGRES_HOST_AUTH_METHOD=trust` solo en demo local. No usar esa politica en produccion.

## Backup/restore demo

```powershell
make backup
python scripts/restore_demo.py backups\<archivo>.tar.gz
python scripts/restore_demo.py backups\<archivo>.tar.gz --apply
```

Sin `--apply`, restore solo valida el paquete.

## Ejecutar frontend

```powershell
cd apps/web
npm install
npm run dev
```

En el entorno local de Codex no se compilo el frontend porque no habia dependencias Node instaladas. La fuente queda preparada para Vite.

## Limitaciones conocidas

- No validado en CODESYS Development System.
- No validado contra runtime CODESYS real.
- No hay PostgreSQL real conectado todavia.
- No hay SQLAlchemy/Alembic operativo todavia.
- No hay hardware Modbus/RS232 validado.
- No hay build frontend verificado en este ambiente.
- No hay Playwright todavia.

Ver detalles en:

- `docs/CURRENT_STATE.md`
- `docs/GAP_ANALYSIS.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/WEB_PLATFORM.md`
- `docs/GRAFANA_NODE_RED.md`
- `codesys-control/docs/CODESYS_CONTROL.md`
