# Instrucciones del repositorio

- Mantener `REAL_IO_ENABLED=false` por defecto.
- No declarar validado hardware real sin pruebas con CODESYS Runtime y dispositivos fisicos.
- La web/API solo solicita comandos; CODESYS valida y ejecuta.
- No almacenar secretos, certificados privados, IPs productivas ni mapas finales no aprobados.
- Grafana y Node-RED no controlan equipos.
- Ejecutar `python -m pytest -q` antes de declarar un hito completado.
