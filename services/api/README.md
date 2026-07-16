# API service

API FastAPI objetivo de la plataforma principal.

Responsabilidades:

- autenticacion, usuarios, roles y permisos;
- validacion de comandos;
- auditoria;
- persistencia;
- publicacion de estados via WebSocket;
- integracion con `services/opcua-connector`.

Regla: la API no escribe salidas de campo; escribe solicitudes en el buzon OPC UA para que CODESYS valide y confirme.
