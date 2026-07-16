# Plataforma web — Hito 4

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
- `POST /recipes/{recipe_id}/approve`
- `GET /campaigns`
- `POST /campaigns`
- `POST /campaigns/{campaign_id}/start`
- `GET /alarms`
- `POST /alarms/{alarm_id}/ack`
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
- alarmas;
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

La API Hito 4 usa store en memoria para demo y pruebas. PostgreSQL + SQLAlchemy/Alembic real queda pendiente para el siguiente tramo de plataforma.

## Validacion

```text
python -m pytest -q
32 passed
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
