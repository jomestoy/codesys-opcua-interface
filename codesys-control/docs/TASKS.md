# Tareas CODESYS propuestas

Estos periodos son parametros iniciales de diseno y deben validarse en FAT/SAT.

| Tarea | Periodo inicial | Responsabilidad |
| --- | ---: | --- |
| `TaskFast` | 100 ms | Watchdog, heartbeat, estado seguro y preparacion de salidas |
| `TaskNormal` | 1 s | Estados, entradas, alarmas e interlocks |
| `TaskSlow` | 20-60 s | Estimacion gravimetrica, PI lento y ajustes de bomba |
| `TaskComms` | 1 s | Preparacion de variables OPC UA y buzon de comandos |

La perdida del frontend, Grafana o Node-RED no debe detener columnas. La perdida prolongada de datos de control debe llevar la columna a estado seguro desde CODESYS.
