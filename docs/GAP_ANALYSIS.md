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
  - `codesys-opcua-interface`: 10 tests.
  - `column-gateway`: 7 tests.
- Estimador matematico offline de flujo por regresion lineal.
- PI lento offline.
- Modelo de comando con TTL, sequence e idempotencia.
- Simulador de redundancia primario/secundario.
- Driver simulado del gateway con lectura/escritura en memoria.
- Parser de referencia LP7516.

## Que funciona solo offline

- Perfil OPC UA.
- Validacion de configuracion del gateway.
- Diagnostico CLI.
- Documentacion conceptual.
- Matematica de control.
- Buzon de comandos.
- Redundancia simulada.
- Structured Text fuente no compilado en CODESYS.

## Que esta simulado

- Dos endpoints CODESYS, con uno activo y otro standby.
- 200 columnas para demo offline.
- Flujo gravimetrico por muestras sinteticas.
- Confirmacion de comandos por CODESYS simulado.
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
- Dependencia `asyncua` validada.
- Conexion real.
- Reconexion.
- Resolucion de namespace por URI.
- Certificados.
- Trust list.
- `Basic256Sha256` con `SignAndEncrypt`.
- Suscripciones.
- Lectura y escritura controlada.
- Calidad OPC UA.
- Timestamp de origen y servidor.
- Buzon de comandos.
- Confirmacion de comandos.
- TTL, sequence ID e idempotencia.
- Monitoreo de endpoint primario/secundario.
- Failover simulado.

## Que falta para la plataforma web

- Migrar la aplicacion completa React/FastAPI existente al repositorio plataforma o integrarla como subarbol.
- Persistencia PostgreSQL.
- SQLAlchemy/Alembic.
- WebSocket.
- React Query.
- Material UI.
- Integracion Grafana por reverse proxy.
- Integracion Node-RED restringida.
- Pruebas Playwright.
- Pantallas obligatorias conectadas a API real.

## Que falta para CODESYS

- Codigo Structured Text.
- Bloques funcionales `FB_Column`, maquina de estados, estimador gravimetrico y PI lento.
- Estructuras `ST_*`.
- GVLs.
- Modelo de 200 columnas.
- Proyecto PLCopen XML importable.
- Simulacion IEC.
- Tareas documentadas.
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

## Riesgo principal

El riesgo tecnico mayor es confundir plantillas con funcionalidad real. A partir de esta auditoria, cada modulo debe declarar explicitamente si es `offline`, `simulado`, `conector real` o `requiere hardware`.
