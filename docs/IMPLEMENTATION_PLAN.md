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
- tests unitarios de modelo de comandos y failover simulado: implementados;
- mapa de simbolos OPC UA: implementado;
- seleccion de endpoint activo: implementada;
- bloqueo de doble activo: implementado;
- suscripcion simulada: implementada.

Validacion:

- `codesys-opcua-interface`: 17 tests passing.

Pendiente:

- probar contra CODESYS real;
- certificados;
- trust list;
- suscripciones reales;
- escritura OPC UA real al buzon;
- confirmacion real de `ST_ColumnCommand`.

## Hito 3: CODESYS

Estado: completado localmente como fuente ST y validacion estatica offline. Pendiente validacion en CODESYS Development System.

Entregables:

- `codesys-control/src/*.st`;
- estructuras `ST_*`;
- GVLs;
- `ARRAY[1..200] OF FB_Column`;
- estimador gravimetrico con regresion lineal;
- PI lento con anti-windup;
- `PRG_ColumnControl` para 200 columnas;
- `PRG_Simulation` para demo offline sin I/O real;
- PLCopen XML preliminar generado en `codesys-control/plcopen/codesys-control.plcopen.xml`;
- validador offline `codesys_opcua_interface/codesys_project.py`;
- documentacion de tareas.

Validacion:

- `codesys-opcua-interface`: 22 tests passing.

Pendiente:

- importar/compilar en CODESYS Development System;
- configurar tareas reales;
- publicar simbolos OPC UA desde CODESYS real;
- probar `FB_Column` y `PRG_ColumnControl` contra un runtime CODESYS;
- validar performance de 200 columnas en hardware de control.

## Hito 4: plataforma web

Estado: completado localmente como prototipo offline API + fuente frontend. Pendiente persistencia PostgreSQL real y build frontend.

Entregables:

- API FastAPI en `services/api/app.py`;
- dominio demo en `codesys_opcua_interface/platform_store.py`;
- modelos de datos principales en migracion SQL;
- API de comandos via conector OPC UA simulado;
- WebSocket `/ws/summary`;
- usuarios, roles, permisos, auditoria;
- frontend React/TypeScript/Vite/Material UI en `apps/web`;
- pantallas base conectadas a API: login, resumen, planta, recetas, campanas, alarmas, usuarios y auditoria.

Validacion:

- `codesys-opcua-interface`: 32 tests passing.
- `compileall`: OK.

Pendiente:

- instalar dependencias Node y compilar frontend;
- reemplazar store en memoria por PostgreSQL + SQLAlchemy/Alembic;
- configurar OIDC/JWT productivo;
- Playwright;
- servir frontend y API con reverse proxy;
- historicos persistentes reales.

## Hito 5: recetas, campanas y alarmas

Estado: completado localmente como flujo funcional offline/API + fuente frontend. Pendiente persistencia real y pruebas UI automatizadas.

Entregables:

- versionamiento;
- aprobacion;
- rechazo;
- obsolescencia;
- clonacion;
- comparacion;
- asignacion;
- ciclo de campana: programar, iniciar, pausar, finalizar, cancelar;
- exportacion y comparacion de campanas;
- alarmas configurables con limites autorizados, alcance all/columns/block y version;
- historial de alarmas;
- reconocimiento, comentario, limpieza y exportacion;
- auditoria.

Validacion:

- `codesys-opcua-interface`: 36 tests passing.
- `compileall`: OK.

Pendiente:

- persistir estos flujos en PostgreSQL real;
- integrar historicos reales de proceso;
- Playwright para flujo completo UI;
- control critico de alarmas en CODESYS real.

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

Estado: completado localmente como provisioning y fuente de integracion sin autoridad de control.

Entregables:

- dashboards Grafana de resumen, tendencias y comunicaciones;
- provisioning de datasource PostgreSQL readonly;
- provisioning de dashboards no editables;
- flows Node-RED de notificacion y reportes;
- editor Node-RED cerrado por defecto en demo;
- reverse proxy con rutas `/grafana/`, `/node-red/` y `/node-red-admin/`;
- API `/integrations`;
- pestana UI `Integraciones`.

Validacion:

- `codesys-opcua-interface`: 41 tests passing.
- `compileall`: OK.

Pendiente:

- ejecutar contenedores con Docker en entorno con imagenes disponibles;
- conectar Grafana a PostgreSQL real;
- configurar SSO/LDAP/OIDC o politica equivalente para administracion Node-RED;
- conectar Node-RED a correo/Teams reales sin secretos en Git.

## Hito 8: empaquetado

Estado: completado localmente como empaquetado demo/plataforma y generacion offline de paquetes gateway. Pendiente validacion Linux real.

Entregables:

- Docker Compose demo para Web, API, PostgreSQL, Grafana, Node-RED y reverse proxy;
- migracion/seed de observabilidad para dashboards;
- backup y restore seguro de configuracion demo;
- `make package-gateway` delegado al repositorio `column-gateway`;
- en `column-gateway`: tarballs portables amd64/arm64;
- en `column-gateway`: paquetes `.deb` estructurales amd64/arm64;
- en `column-gateway`: scripts install/update/uninstall/rollback/diagnose;
- en `column-gateway`: unidad systemd incluida.

Validacion:

- `codesys-opcua-interface`: 45 tests passing.
- `column-gateway`: 16 tests passing.
- `column-gateway/dist/column-gateway_0.8.0_{amd64,arm64}.{tar.gz,deb}` generado localmente.

Pendiente:

- ejecutar Docker Compose con imagenes reales;
- instalar `.deb` en Linux con `dpkg`;
- validar `systemd`;
- validar rollback en Linux;
- generar paquetes firmados en CI;
- crear usuario PostgreSQL readonly real para Grafana en produccion.

## Hito 9: pruebas

Estado: completado localmente en modo offline/simulacion. Pendiente ejecucion contra runtime, Docker, navegador y hardware reales.

Entregables:

- unitarias existentes ampliadas;
- integracion API/OPC UA simulado;
- fuente Playwright para UI;
- carga simulada de 200 columnas;
- failover simulado CODESYS A/B;
- auditoria de seguridad offline;
- smoke/security gateway.

Validacion:

- `codesys-opcua-interface`: 48 tests passing.
- `column-gateway`: 18 tests passing.
- load test plataforma: 200 columnas, 50 comandos, 0 fallas, failover A/B.
- security audit plataforma: passed.
- smoke test gateway: passed.
- security audit gateway: passed.

Pendiente:

- Playwright contra navegador real;
- Docker Compose real;
- OPC UA real con certificados;
- CODESYS real;
- paquetes `.deb` instalados con `dpkg`;
- hardware Modbus/RS232;
- prueba de carga prolongada;
- FAT/SAT.

## Regla de avance

Despues de cada hito:

1. ejecutar pruebas disponibles;
2. corregir fallas;
3. actualizar documentacion;
4. crear commit descriptivo;
5. declarar explicitamente que funciona real, simulado u offline.
