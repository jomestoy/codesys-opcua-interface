# Conector OPC UA CODESYS

Fecha de actualizacion: 2026-07-16.

Estado Hito 2: implementado y probado en modo offline/simulacion.

## Alcance implementado

- Mapa de simbolos OPC UA sin indices de namespace codificados.
- Resolucion de `NodeId` a partir de namespace index resuelto por URI.
- Wrapper `AsyncuaCodesysClient` con dependencia opcional `asyncua`.
- Lectura individual.
- Lectura multiple.
- Escritura controlada.
- Suscripcion a cambios de datos.
- Modelo de calidad/timestamps mediante `OpcuaDataValue`.
- Simulador de endpoints CODESYS primario/secundario.
- Seleccion del unico endpoint activo.
- Bloqueo si hay doble activo.
- Buzon de comandos OPC UA.
- Confirmacion de comando desde CODESYS simulado.

## Flujo de comando implementado

1. API o servicio crea `ColumnCommand`.
2. `CommandMailbox` valida rango, tipo, TTL e idempotencia.
3. `CodesysOpcuaConnector` evalua endpoints primario/secundario.
4. Si existe exactamente un activo, escribe `GVL_OPCUA.CommandMailbox`.
5. CODESYS simulado publica `GVL_OPCUA.CommandConfirmation`.
6. El conector actualiza estado local como `Applied`, `Rejected` o `Failed`.

## Simbolos principales

- `GVL_System.ControllerId`
- `GVL_System.ControllerRole`
- `GVL_System.IsActive`
- `GVL_System.RedundancyHealthy`
- `GVL_System.Heartbeat`
- `GVL_System.ApplicationVersion`
- `GVL_System.ControlAuthority`
- `GVL_OPCUA.CommandMailbox`
- `GVL_OPCUA.CommandConfirmation`
- `GVL_Columns.Columns[001].Status.FlowMeasuredKgH`

## Validado por tests

- seleccion de endpoint activo;
- escritura solo al activo;
- rechazo ante doble activo;
- failover al secundario si primario esta offline;
- suscripcion simulada;
- `NodeId` con namespace resuelto;
- cliente inyectable para pruebas sin `asyncua`.

## Pendiente para OPC UA real

- Instalar `asyncua`.
- Configurar certificados cliente.
- Configurar trust list en CODESYS.
- Validar `Basic256Sha256` + `SignAndEncrypt` contra runtime real.
- Probar suscripciones reales.
- Probar escritura real del buzon, no de salidas.
- Confirmar tipos OPC UA para `ST_ColumnCommand`.
- Validar latencia, reconexion y timeouts.

## Restriccion

No se declara validado CODESYS real ni redundancia real. Este hito valida contrato, seleccion de activo y flujo de comando contra simuladores/fakes.
