# Plan de implementacion

## Hito 1: auditoria y arquitectura

Estado: completado localmente en modo offline/simulacion.

Entregables:

- `docs/CURRENT_STATE.md`
- `docs/GAP_ANALYSIS.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/DECISIONS.md`
- estructura base de plataforma principal;
- estructura base de gateway.

Validacion:

- `codesys-opcua-interface`: 10 tests passing.
- `column-gateway`: 7 tests passing.
- demo offline 200 columnas ejecutada.

## Hito 2: OPC UA real

Entregables:

- servicio `services/opcua-connector`: base creada;
- modelo de comandos: implementado offline;
- cliente asincronico con `asyncua`: wrapper preparado, requiere dependencia y runtime;
- simulador de endpoint primario/secundario: implementado;
- tests unitarios de modelo de comandos y failover simulado: implementados.

Pendiente:

- probar contra CODESYS real;
- certificados;
- trust list;
- suscripciones reales;
- escritura OPC UA real al buzon.

## Hito 3: CODESYS

Entregables:

- `codesys-control/src/*.st`;
- estructuras `ST_*`;
- GVLs;
- `ARRAY[1..200] OF FB_Column`;
- estimador gravimetrico con regresion lineal;
- PI lento con anti-windup;
- PLCopen XML inicial cuando sea posible;
- documentacion de tareas.

## Hito 4: plataforma web

Entregables:

- integrar/portar frontend y FastAPI;
- modelos de datos;
- API de comandos via buzon OPC UA;
- WebSocket;
- usuarios, roles, permisos, auditoria.

## Hito 5: recetas, campanas y alarmas

Entregables:

- versionamiento;
- aprobacion;
- asignacion;
- ejecucion simulada;
- alarmas configurables con limites autorizados;
- auditoria.

## Hito 6: gateway

Entregables:

- drivers desacoplados;
- driver simulado funcional;
- interfaces Modbus/RS232 preparadas;
- health/watchdog;
- buffer;
- dual NIC;
- safe state.

## Hito 7: Grafana y Node-RED

Entregables:

- dashboards iniciales;
- provisioning;
- flows de notificacion sin control directo;
- reverse proxy.

## Hito 8: empaquetado

Entregables:

- Docker demo;
- systemd;
- scripts de instalacion;
- paquetes `.deb` cuando el entorno Linux este disponible;
- tarballs portables.

## Hito 9: pruebas

Entregables:

- unitarias;
- integracion;
- UI;
- carga 200 columnas;
- failover;
- seguridad.

## Regla de avance

Despues de cada hito:

1. ejecutar pruebas disponibles;
2. corregir fallas;
3. actualizar documentacion;
4. crear commit descriptivo;
5. declarar explicitamente que funciona real, simulado u offline.
