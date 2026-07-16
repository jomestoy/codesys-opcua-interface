# Analisis de brechas

Fecha de auditoria: 2026-07-15.

## Que funciona realmente

- Generacion offline de perfil OPC UA en `codesys-opcua-interface`.
- Validacion offline basica de:
  - endpoint `opc.tcp://`;
  - `SignAndEncrypt`;
  - `REAL_IO_ENABLED=false`;
  - presencia de simbolos minimos.
- CLI del gateway con:
  - lectura de configuracion JSON;
  - validacion basica;
  - salida de estado;
  - diagnostico local;
  - comandos nominales de red y dispositivos.
- Tests unitarios actuales:
  - `codesys-opcua-interface`: 36 tests.
  - `column-gateway`: 7 tests.
- Estimador matematico offline de flujo por regresion lineal.
- PI lento offline.
- Modelo de comando con TTL, sequence e idempotencia.
- Simulador de redundancia primario/secundario.
- Conector OPC UA offline/simulado con seleccion de activo y bloqueo por doble activo.
- Driver simulado del gateway con lectura/escritura en memoria.
- Parser de referencia LP7516.
- API FastAPI offline con autenticacion, permisos, columnas, comandos, recetas, campanas, alarmas, usuarios y auditoria.
- Flujos offline/API de recetas, campanas y alarmas Hito 5.
- Dashboards Grafana provisionados como JSON de solo lectura.
- Flujos Node-RED provisionados para notificacion/reportes sin control directo.
- API y fuente frontend exponen estado de integraciones con `control_allowed=false`.

## Que funciona solo offline

- Perfil OPC UA.
- Validacion de configuracion del gateway.
- Diagnostico CLI.
- Documentacion conceptual.
- Matematica de control.
- Buzon de comandos.
- Redundancia simulada.
- Suscripciones simuladas.
- Wrapper `asyncua` preparado pero no conectado a runtime real.
- Structured Text fuente no compilado en CODESYS.
- Programa ST offline `PRG_ColumnControl` para 200 columnas.
- Programa ST offline `PRG_Simulation` para escenarios de demo sin I/O real.
- Generacion de PLCopen XML preliminar desde fuentes ST.
- Backend web funcional en memoria, sin PostgreSQL real.
- Frontend React/Vite/MUI como fuente no compilada en este ambiente.
- Recetas/campanas/alarmas funcionales en memoria y simulacion.
- Grafana y Node-RED provisionados sin arranque de contenedores validado.

## Que esta simulado

- Dos endpoints CODESYS, con uno activo y otro standby.
- 200 columnas para demo offline.
- Flujo gravimetrico por muestras sinteticas.
- Confirmacion de comandos por CODESYS simulado.
- Servidor/cliente OPC UA simulado a nivel de contrato Python, no socket OPC UA real.
- Driver de campo `simulated`.
- Lecturas de dispositivos simulados.

## Que son unicamente plantillas

- Nodos OPC UA `ns=<validado>;s=...`.
- Perfil CODESYS.
- Perfil de gateway.
- Protocolos de dispositivo declarados.
- Seguridad OPC UA declarada.
- Documentacion de arquitectura.

## Que falta para OPC UA real

- Instalar dependencia opcional `asyncua`.
- Validar cliente OPC UA asincronico con runtime real.
- Conexion real.
- Reconexion.
- Certificados.
- Trust list.
- `Basic256Sha256` con `SignAndEncrypt`.
- Suscripciones.
- Lectura y escritura controlada.
- Calidad OPC UA.
- Timestamp de origen y servidor.
- Buzon de comandos contra tipos OPC UA reales.
- Confirmacion de comandos contra runtime CODESYS real.
- Monitoreo real de endpoint primario/secundario.
- Failover CODESYS real.

## Que falta para la plataforma web

- Persistencia PostgreSQL real.
- SQLAlchemy/Alembic real.
- Migrar el store en memoria a repositorios persistentes.
- Compilar frontend con Node/npm y dependencias instaladas.
- Integracion Grafana por reverse proxy dentro de la UI.
- Integracion Node-RED restringida.
- Pruebas Playwright.
- Completar pantallas restantes: tendencias, comunicaciones, dispositivos, mapa I/O, mantenimiento, simulador, estado sistema, backup/restore.
- Persistir Hito 5 en PostgreSQL real.
- Hardening JWT/OIDC productivo.
- Validar Grafana contra PostgreSQL/Timescale real.
- Habilitar administracion Node-RED con autenticacion fuerte si se requiere editar flows en produccion.

## Que falta para CODESYS

- Compilar el codigo Structured Text en CODESYS Development System.
- Validar bloques funcionales `FB_Column`, maquina de estados, estimador gravimetrico y PI lento en runtime real.
- Validar estructuras `ST_*`.
- Validar GVLs y simbolos exportados.
- Validar modelo de 200 columnas en CODESYS.
- Validar si el XML preliminar generado es importable sin ajustes.
- Simulacion IEC en CODESYS real.
- Tareas documentadas y configuradas dentro del proyecto CODESYS real.
- Validacion en CODESYS Development System.
- Licenciamiento/runtime para prueba real.

## Que falta para el gateway

- Drivers reales validados con hardware.
- Servicio Linux real.
- Drivers:
  - Modbus TCP;
  - Modbus RTU;
  - RS232;
  - socket serial;
  - simulado.
- Buffer breve.
- Health real.
- Watchdog.
- Dual NIC.
- Reglas nftables.
- Empaquetado `.deb`.
- systemd.
- Logs y rotacion.
- Metricas.
- Diagnosticos funcionales.

Arquitectura modular, driver simulado, buffer, autoridad y systemd base ya existen; no estan validados en Linux industrial.

## Que requiere hardware

- Validacion de Modbus TCP con ADAM u otro equipo real.
- Validacion RS485/Modbus RTU.
- Validacion RS232 con balanzas.
- Parser final LP7516 u otro protocolo definitivo.
- Confirmacion de bombas LMI.
- Estado seguro electrico.
- E-Stop fisico.
- Ensayos de ruido, tara, recarga y cambio de recipiente.

## Que requiere licencias CODESYS

- CODESYS Development System para importar/validar PLCopen.
- Runtime CODESYS en servidor A.
- Runtime CODESYS en servidor B.
- Licencias de redundancia si se requiere failover real.
- Configuracion OPC UA Server.
- Simbolos exportados.

## Que no puede validarse en este ambiente

- Conexion real a CODESYS.
- Seguridad OPC UA con certificados reales.
- Red OT dual NIC.
- Drivers contra hardware fisico.
- Paquetes `.deb` instalados en Raspberry Pi/PC industrial.
- Servicio systemd ejecutandose en Linux.
- Failover real entre dos runtimes CODESYS.
- Pruebas FAT/SAT.
- Arranque real de contenedores Grafana/Node-RED en este ambiente.
- Dashboards Grafana con datos historicos PostgreSQL reales.
- Envio real de notificaciones Node-RED hacia correo/Teams.

## Riesgo principal

El riesgo tecnico mayor es confundir plantillas con funcionalidad real. A partir de esta auditoria, cada modulo debe declarar explicitamente si es `offline`, `simulado`, `conector real` o `requiere hardware`.
