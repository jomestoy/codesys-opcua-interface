# Informe de pruebas

Fecha: 2026-07-15.

## codesys-opcua-interface

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
48 passed
```

Cobertura funcional validada:

- perfil seguro offline;
- rechazo de modo OPC UA inseguro;
- regresion lineal para flujo gravimetrico;
- congelacion del estimador por timestamp no monotonico;
- PI lento con rate limit y freeze;
- TTL e idempotencia de comandos;
- rechazo de setpoint fuera de rango;
- failover simulado activo/standby;
- NodeId con namespace resuelto.
- mapa de simbolos OPC UA sin namespace index fijo;
- endpoint activo primario/secundario;
- bloqueo por doble activo;
- failover simulado;
- escritura solo al activo;
- suscripcion simulada;
- presencia de todos los `FB_*` y `ST_*` requeridos para CODESYS;
- soporte fuente de `ARRAY[1..200] OF FB_Column`;
- `REAL_IO_ENABLED=false` por defecto en `GVL_System.RealIoEnabled`;
- enrutamiento del buzon OPC UA por `PRG_ColumnControl`;
- bloqueo de simulacion cuando `RealIoEnabled=TRUE`;
- generacion parseable de PLCopen XML preliminar;
- dominio web/API con usuarios, permisos y 200 columnas;
- login y token HMAC local;
- flujo API de comandos hacia CODESYS simulado;
- recetas y campanas funcionales;
- creacion de usuarios y foto de perfil;
- fuente frontend con stack React/Vite/MUI/React Query y rutas API requeridas;
- recetas Hito 5: clonar, rechazar, editar, aprobar, comparar, asignar y obsoletar;
- campanas Hito 5: programar, iniciar, pausar, finalizar, cancelar, comparar y exportar;
- alarmas Hito 5: reglas configurables, evaluacion, historial, reconocimiento, limpieza y exportacion.
- integraciones Hito 7: Grafana/Node-RED sin autoridad de control;
- empaquetado Hito 8: Docker Compose demo, backup/restore seguro y queries Grafana alineadas al esquema.
- Hito 9: load test simulado, security audit y fuente Playwright.

## column-gateway

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
18 passed
```

Cobertura funcional validada:

- configuracion simulada valida;
- bloqueo de escritura real con `REAL_IO_ENABLED=false`;
- driver simulado lectura/escritura en memoria;
- buffer FIFO;
- servicio gateway con dispositivo simulado;
- parser de referencia LP7516.
- paquetes Hito 8: tarballs y `.deb` estructurales amd64/arm64;
- CLI `version` y `update` con validacion de argumentos.
- Hito 9: smoke test CLI y security audit gateway.

## No validado en este ambiente

- CODESYS real;
- importacion/compilacion del XML PLCopen preliminar en CODESYS Development System;
- OPC UA real con certificados;
- PostgreSQL/SQLAlchemy/Alembic real;
- build frontend con dependencias Node instaladas;
- Playwright;
- hardware Modbus/RS232;
- systemd;
- paquetes Debian instalados;
- red dual NIC/nftables;
- Grafana/Node-RED ejecutandose.
- Docker Compose demo completo ejecutandose.
- Instalacion real de paquetes `.deb`.
