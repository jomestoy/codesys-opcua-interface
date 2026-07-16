# Seguridad

- `REAL_IO_ENABLED=false` por defecto.
- No commitear certificados, usuarios técnicos, endpoints reales ni mapas finales.
- Usar OPC UA `SignAndEncrypt`.
- Gestionar trust lists y certificados fuera del repositorio.
- Separar red de gestión y red OT.
- Mantener interlocks críticos en CODESYS/control físico.
- Toda escritura futura debe tener TTL, idempotencia, confirmación y auditoría.

Este proyecto no es un sistema de seguridad certificado.
