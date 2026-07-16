# Plataforma web — Hitos 4 y 5

Estado: prototipo funcional offline con API FastAPI y fuente React/Vite. No es aun despliegue productivo.

## Backend

Archivos:

- `codesys_opcua_interface/platform_store.py`: dominio en memoria, usuarios, permisos, columnas, recetas, campanas, alarmas, auditoria y servicio de comandos.
- `services/api/app.py`: API FastAPI.
- `services/api/run.py`: entrypoint Uvicorn.

Endpoints principales:

- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/change-password`
- `GET /users`
- `POST /users`
- `PATCH /users/{username}/profile`
- `GET /system/summary`
- `GET /columns`
- `GET /columns/{column_id}`
- `POST /commands`
- `GET /recipes`
- `POST /recipes`
- `GET /recipes/compare`
- `PATCH /recipes/{recipe_id}`
- `POST /recipes/{recipe_id}/clone`
- `POST /recipes/{recipe_id}/approve`
- `POST /recipes/{recipe_id}/reject`
- `POST /recipes/{recipe_id}/obsolete`
- `POST /recipes/{recipe_id}/assign`
- `GET /campaigns`
- `POST /campaigns`
- `GET /campaigns/compare`
- `GET /campaigns/{campaign_id}/export`
- `POST /campaigns/{campaign_id}/schedule`
- `POST /campaigns/{campaign_id}/start`
- `POST /campaigns/{campaign_id}/pause`
- `POST /campaigns/{campaign_id}/finish`
- `POST /campaigns/{campaign_id}/cancel`
- `GET /alarms`
- `POST /alarms/{alarm_id}/ack`
- `POST /alarms/{alarm_id}/clear`
- `GET /alarms/export`
- `GET /alarm-rules`
- `POST /alarm-rules`
- `PATCH /alarm-rules/{rule_id}`
- `POST /alarm-rules/evaluate`
- `GET /alarm-history`
- `GET /audit`
- `WS /ws/summary`

## Frontend

Archivos:

- `apps/web/src/App.tsx`
- `apps/web/src/api.ts`
- `apps/web/src/types.ts`
- `apps/web/src/theme.ts`

Pantallas implementadas:

- login;
- resumen;
- vista planta por bloque;
- detalle de columna;
- recetas;
- campanas;
- alarmas y reglas de alarma;
- usuarios;
- auditoria.

## Base de datos

`database/migrations/001_initial.sql` fue ampliada con tablas para:

- roles;
- usuarios;
- bloques;
- columnas;
- recetas;
- campanas;
- comandos;
- alarmas;
- auditoria;
- gateways;
- dispositivos;
- mapas I/O;
- series historicas;
- mantenimiento;
- reportes;
- configuraciones.
- reglas e historial de alarmas.

La API Hito 4 usa store en memoria para demo y pruebas. PostgreSQL + SQLAlchemy/Alembic real queda pendiente para el siguiente tramo de plataforma.

## Validacion

```text
python -m pytest -q
36 passed
python -m compileall codesys_opcua_interface services tests
OK
```

No se compilo frontend porque no hay `node_modules` instalado en el ambiente y Node/npm no estan en PATH del sistema. Se localizaron Node/pnpm embebidos de Codex, pero no hay cache local de React/Vite/MUI. La validacion de UI de este hito es estatica mediante tests de fuente.

## Limitaciones

- Sin PostgreSQL real conectado.
- Sin SQLAlchemy/Alembic ejecutado.
- Sin build frontend verificado.
- Sin Playwright.
- Sin reverse proxy integrado para servir web + API en una URL.
- Sin Grafana embebido aun en la UI.
- Sin historicos persistentes reales.
