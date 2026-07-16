# Modelo de control CODESYS — Hito 3

Estado: fuente Structured Text validada de forma estatica. No esta compilada en CODESYS Development System.

## Archivos principales

- `src/Types.st`: enums, estructuras de columna, comandos, calidad, runtime OPC UA y banco de 200 columnas.
- `src/FunctionBlocks.st`: bloques funcionales de columna, estimador gravimetrico, PI lento, bomba, alarmas, fail-safe y gateway health.
- `src/GVL.st`: variables globales expuestas como `GVL_System`, `GVL_OPCUA`, `GVL_Columns`, `GVL_Recipes`, `GVL_Gateways` y `GVL_Simulation`.
- `src/PRG_ColumnControl.st`: programa principal que inicializa y ejecuta 200 columnas con `GVL_ColumnInstances`.
- `src/PRG_Simulation.st`: simulador IEC offline. Sale inmediatamente si `GVL_System.RealIoEnabled=TRUE`.
- `src/TaskModel.st`: constantes de periodos iniciales y documentacion de tareas.

## Flujo de comando

1. La API/conector escribe una solicitud autorizada en `GVL_OPCUA.CommandMailbox`.
2. `PRG_ColumnControl` verifica controlador activo, TTL, rango de columna y habilitacion.
3. CODESYS acepta, rechaza o expira el comando.
4. La columna correspondiente recibe el comando mediante `FB_Column`.
5. `GVL_OPCUA.CommandConfirmation` publica el resultado.

La aplicacion web no escribe salidas de campo. Grafana y Node-RED no participan en control.

## Control gravimetrico

`FB_GravimetricFlowEstimator` usa una ventana circular de muestras y calcula el flujo masico por pendiente de regresion lineal:

```text
flujo kg/h = -pendiente(peso respecto del tiempo) * 3600
```

El PI lento se congela ante mala calidad de dato, fail-safe, modo no habilitado o perdida de condiciones operacionales. Los parametros iniciales estan pensados para FAT/SAT, no como tuning final.

## Tareas propuestas

| Tarea | Periodo inicial | Uso |
| --- | ---: | --- |
| Fast | 100 ms | heartbeat, watchdog, salidas seguras |
| Normal | 1 s | estados, comandos, alarmas |
| Slow | 30 s | estimador gravimetrico y PI |
| Comms | 500 ms | preparacion OPC UA |

Estos periodos deben configurarse en el proyecto CODESYS real y validarse con carga de 200 columnas.

## Limitaciones

- No se genero archivo `.project`.
- El PLCopen XML es preliminar y requiere importacion/compilacion en CODESYS.
- No se valido OPC UA Server real de CODESYS.
- No se valido redundancia real entre dos runtimes.
- No se valido hardware, drivers de campo ni tiempos reales.
