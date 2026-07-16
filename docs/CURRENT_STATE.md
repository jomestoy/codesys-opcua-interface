# Estado actual del proyecto

Fecha de auditoria: 2026-07-15.

## Repositorios auditados

- `jomestoy/codesys-opcua-interface`
- `jomestoy/column-gateway`

La copia local auditada esta en `github-projects/`.

## codesys-opcua-interface

Estado real: plantilla offline de perfil OPC UA.

Archivos relevantes:

- `codesys_opcua_interface/profile.py`: genera un perfil JSON con endpoint, namespace, politica de seguridad, modo de seguridad y plantillas de nodos.
- `config/codesys-profile.example.json`: ejemplo de perfil.
- `docs/ARCHITECTURE.md`: arquitectura conceptual.
- `docs/SECURITY.md`: notas de seguridad.
- `tests/test_profile.py`: pruebas unitarias basicas del perfil offline.

Funciones existentes:

- `build_profile()`: construye un diccionario de perfil OPC UA a partir de variables de entorno.
- `validate_profile(profile)`: valida reglas basicas del perfil.
- `main()`: CLI minima con comandos `export` y `validate`.

Pruebas ejecutadas:

```text
2 passed in 0.02s
```

## column-gateway

Estado real: CLI de validacion de configuracion y diagnostico local. No contiene drivers reales.

Archivos relevantes:

- `column_gateway/cli.py`: CLI con comandos `status`, `config validate`, `diagnose`, `devices test`, `network check` y comandos de servicio informativos.
- `config/gateway.example.json`: ejemplo de configuracion.
- `docs/ARCHITECTURE.md`: arquitectura conceptual.
- `docs/SECURITY.md`: notas de seguridad.
- `tests/test_gateway.py`: pruebas unitarias de validacion de configuracion.

Funciones existentes:

- `read_config(path)`: lee JSON de configuracion o entrega configuracion segura por defecto.
- `validate_config(config)`: valida `gateway_id`, `real_io_enabled`, tipo de dispositivo y endpoint CODESYS.
- `main()`: CLI minima.

Pruebas ejecutadas:

```text
2 passed in 0.03s
```

## Conclusion

Ambos repositorios son bases correctas para evolucionar, pero aun no contienen una plataforma productiva ni un prototipo integrado. Lo existente valida criterios de seguridad por defecto y evita declarar I/O real habilitado. Esa propiedad debe conservarse.

## Avance implementado tras auditoria

### Plataforma / CODESYS OPC UA

Se agregaron:

- modelo offline de buzon de comandos con TTL, sequence ID e idempotencia;
- simulador deterministico de dos endpoints CODESYS, con primario activo y secundario standby;
- failover simulado donde solo el activo acepta comandos;
- estimador gravimetrico offline por regresion lineal;
- PI lento offline con banda muerta, rate limit y congelacion;
- wrapper OPC UA real con `asyncua` opcional y resolucion de namespace por URI;
- estructura base de plataforma principal;
- migracion SQL inicial;
- seed de 200 columnas;
- dashboard Grafana inicial de solo lectura;
- flow Node-RED inicial sin control;
- reverse proxy inicial;
- codigo Structured Text base para CODESYS.

Pruebas ejecutadas:

```text
10 passed
```

Demo ejecutada:

```text
python -m codesys_opcua_interface.demo --columns 200 --ticks 12
```

Resultado observado:

- `REAL_IO_ENABLED=false`;
- 200 columnas simuladas;
- flujo columna 1: `90.0 kg/h`;
- comando `set_flow` aplicado por `CODESYS-A`;
- failover simulado a `CODESYS-B`;
- doble escritura prevenida.

### Gateway

Se agregaron:

- configuracion estructurada;
- autoridad de escritura;
- buffer de eventos;
- metricas;
- health;
- driver base;
- driver simulado funcional en memoria;
- parser de referencia LP7516;
- adaptadores Modbus/RS232 que fallan explicitamente si falta dependencia/hardware;
- servicio `GatewayService`;
- systemd unit base;
- Dockerfile base;
- empaquetado tar.gz portable.

Pruebas ejecutadas:

```text
7 passed
```

Comando probado:

```text
python -m column_gateway.cli devices test
```

Resultado observado:

- lectura simulada de balanza;
- lectura simulada de bomba;
- calidad 1.0 en driver simulado conectado.
