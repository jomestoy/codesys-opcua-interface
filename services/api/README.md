# API service

API FastAPI de la plataforma principal.

Responsabilidades:

- autenticacion, usuarios, roles y permisos;
- validacion de comandos;
- auditoria;
- persistencia;
- publicacion de estados via WebSocket;
- integracion con `services/opcua-connector`.

Regla: la API no escribe salidas de campo; escribe solicitudes en el buzon OPC UA para que CODESYS valide y confirme.

## Estado Hito 4

Implementado en `services/api/app.py`:

- autenticacion con token HMAC local;
- usuarios, roles, permisos, cambio de password y foto de perfil;
- resumen ejecutivo;
- columnas y detalle;
- comandos via `PlatformService` + conector OPC UA simulado;
- recetas;
- campanas;
- alarmas;
- auditoria;
- WebSocket `/ws/summary`;
- `REAL_IO_ENABLED=false` por defecto.

## Ejecutar

```powershell
python -m services.api.run
```

URLs:

- API: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`
- credenciales demo runtime: `GET /auth/demo-credentials`

Si se definen `DEMO_ADMIN_PASSWORD` y `DEMO_OPERATOR_PASSWORD`, la demo usa esos valores. Si no, los genera en runtime y no guarda contrasenas en Git.
