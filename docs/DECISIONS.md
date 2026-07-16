# Decisiones de arquitectura

## ADR-001: CODESYS es la autoridad final de control

Decision: la aplicacion web y el gateway no ejecutan la logica final de control.

Motivo: evita control paralelo, reduce riesgo operacional y concentra interlocks, estados seguros y PI en IEC 61131-3.

## ADR-002: gateway sin PI propio

Decision: el gateway no implementa un segundo controlador PI que compita con CODESYS.

Motivo: el gateway normaliza comunicaciones, calidad y timestamps; CODESYS calcula control gravimetrico y manda salidas.

## ADR-003: comandos por buzon OPC UA

Decision: la web solicita acciones mediante API; la API escribe un comando en un buzon OPC UA; CODESYS valida y confirma.

Motivo: no se escriben salidas directas desde frontend ni API.

## ADR-004: REAL_IO_ENABLED=false por defecto

Decision: cualquier modulo nuevo debe arrancar con I/O real deshabilitado.

Motivo: seguridad durante desarrollo, demo y pruebas offline.

## ADR-005: namespace OPC UA por URI

Decision: no se codifican indices de namespace OPC UA.

Motivo: los indices cambian entre runtimes; la conexion debe resolverlos por URI.

## ADR-006: redundancia preparada, no validada

Decision: se implementa simulacion de endpoint primario/secundario y estado de redundancia, pero no se declara validada la redundancia CODESYS real.

Motivo: requiere dos runtimes, licencias y pruebas OT reales.

## ADR-007: Grafana y Node-RED no controlan equipos

Decision: Grafana se limita a visualizacion; Node-RED a notificaciones, reportes e integraciones.

Motivo: evita caminos alternativos de control no auditados.
