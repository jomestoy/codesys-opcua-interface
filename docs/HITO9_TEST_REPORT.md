# Hito 9 - Informe de pruebas

Estado: completado localmente en modo offline/simulacion.

## Plataforma

Validado:

- `python -m pytest -q`: 48 tests passing.
- `python -m compileall -q codesys_opcua_interface services tests scripts`: OK.
- `scripts/load_test.py`: carga simulada de 200 columnas, comandos OPC UA simulados y failover CODESYS A/B.
- `scripts/security_audit.py`: sin secretos detectados y `REAL_IO_ENABLED=false`.
- fuente Playwright creada en `apps/web/tests/e2e.spec.ts`.

Ultimo load test ejecutado:

- columnas: 200;
- comandos: 50;
- fallas: 0;
- failover simulado: `CODESYS-A` a `CODESYS-B`;
- modo: `offline_simulation`;
- I/O real: deshabilitado.

## Gateway

Validado:

- `python -m pytest -q`: 18 tests passing.
- `python -m compileall -q column_gateway tests scripts`: OK.
- `scripts/smoke_test.py`: version, config validate, status, diagnose, network check y devices test.
- `scripts/security_audit.py`: sin secretos detectados y `real_io_enabled=false`.

## No validado aun

- Playwright ejecutado contra navegador real.
- Docker Compose completo levantado.
- Grafana renderizando dashboards contra PostgreSQL real.
- Node-RED enviando correo/Teams real.
- CODESYS Runtime real.
- OPC UA con certificados reales.
- Instalacion `.deb` con `dpkg`.
- Servicio `systemd` en Linux.
- Hardware Modbus TCP/RTU/RS232.
- FAT/SAT de planta.
