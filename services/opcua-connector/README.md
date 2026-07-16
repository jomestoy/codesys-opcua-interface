# OPC UA connector

Conector entre API/plataforma y CODESYS OPC UA.

La implementacion Python reusable esta en:

- `codesys_opcua_interface.opcua_client`
- `codesys_opcua_interface.opcua_connector`
- `codesys_opcua_interface.opcua_nodes`
- `codesys_opcua_interface.opcua_simulator`
- `codesys_opcua_interface.command_model`

Estado:

- simulacion redundante primaria/secundaria: implementada;
- modelo de comandos con TTL, sequence e idempotencia: implementado offline;
- cliente asyncua real: wrapper preparado, requiere dependencia opcional y CODESYS real;
- seleccion de endpoint activo: implementada en simulacion/fake;
- bloqueo por doble activo: implementado;
- suscripciones: contrato implementado y probado con simulador.
