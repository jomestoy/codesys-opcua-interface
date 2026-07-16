VAR_GLOBAL CONSTANT
    TASK_FAST_PERIOD_MS : UDINT := 100;      (* watchdog, heartbeat, salida segura *)
    TASK_NORMAL_PERIOD_MS : UDINT := 1000;   (* estados, comandos, alarmas *)
    TASK_SLOW_PERIOD_MS : UDINT := 30000;    (* estimador gravimetrico y PI lento *)
    TASK_COMM_PERIOD_MS : UDINT := 500;      (* preparacion variables OPC UA *)
END_VAR

(* Configuracion propuesta de tareas:
   - PRG_Simulation: solo demo/offline; nunca con RealIoEnabled=TRUE.
   - PRG_ColumnControl: tarea normal; usa FB_Column para 200 columnas.
   - En CODESYS real, los periodos deben configurarse en Task Configuration,
     no solamente en este archivo fuente documental. *)
