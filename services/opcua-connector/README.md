# OPC UA connector

Conector entre API/plataforma y CODESYS OPC UA.

La implementacion Python reusable esta en `codesys_opcua_interface/opcua_client.py`, `command_model.py` y `redundancy.py`.

Estado:

- simulacion redundante primaria/secundaria: implementada;
- modelo de comandos con TTL, sequence e idempotencia: implementado offline;
- cliente asyncua real: wrapper preparado, requiere dependencia opcional y CODESYS real.
