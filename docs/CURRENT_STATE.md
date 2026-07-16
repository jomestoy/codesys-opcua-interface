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
- mapa OPC UA Hito 2 sin indices de namespace fijos;
- conector primario/secundario que escribe solo al activo;
- bloqueo por doble activo;
- suscripciones simuladas;
- simulador OPC UA compatible con el contrato del conector;
- estructura base de plataforma principal;
- migracion SQL inicial;
- seed de 200 columnas;
- dashboard Grafana inicial de solo lectura;
- flow Node-RED inicial sin control;
- reverse proxy inicial;
- codigo Structured Text base para CODESYS;
- runtime Structured Text de 200 columnas con `GVL_System`, `GVL_OPCUA` y `GVL_Columns`;
- `PRG_ColumnControl` para inicializar/ejecutar 200 instancias reutilizables `FB_Column`;
- `PRG_Simulation` para demo offline con `REAL_IO_ENABLED=false`;
- `TaskModel.st` con periodos propuestos documentados;
- `codesys-control/plcopen/codesys-control.plcopen.xml` como export preliminar de fuentes ST;
- validador offline de fuentes CODESYS y generador PLCopen preliminar.

Pruebas ejecutadas despues de Hito 2:

```text
17 passed
```

Pruebas ejecutadas despues de Hito 3:

```text
22 passed
```

Pruebas ejecutadas despues de Hito 4:

```text
32 passed
```

Pruebas ejecutadas despues de Hito 5:

```text
36 passed
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

Estado Hito 3:

- el modelo CODESYS ya existe como fuente ST y se valida de forma estatica;
- no se ha compilado ni importado en CODESYS Development System;
- no existe binario `.project`;
- el PLCopen XML generado es preliminar y debe validarse en CODESYS antes de usarlo en runtime real.

Estado Hito 4:

- API FastAPI funcional offline;
- usuarios, roles, permisos, cambio de contrasena y foto de perfil;
- endpoints de resumen, columnas, comandos, recetas, campanas, alarmas, auditoria y WebSocket;
- comandos pasan por API hacia conector OPC UA simulado y reciben confirmacion CODESYS simulada;
- frontend React/Vite/MUI implementado como fuente;
- migracion SQL ampliada para modelos principales;
- PostgreSQL/SQLAlchemy/Alembic reales siguen pendientes;
- frontend no compilado por falta de dependencias Node instaladas en el ambiente.

Estado Hito 5:

- recetas con crear, editar borrador, clonar, aprobar, rechazar, obsoletar, comparar y asignar columnas;
- campanas con crear, programar, iniciar, pausar, finalizar, cancelar, comparar y exportar;
- alarmas configurables por reglas con variable, operador, umbral, histeresis, retardo, prioridad, accion, alcance y version;
- historial de alarmas, reconocimiento con comentario, limpieza y exportacion;
- API y fuente frontend actualizadas para estas acciones;
- todo sigue operando offline/simulacion; CODESYS real y PostgreSQL real siguen pendientes.

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
