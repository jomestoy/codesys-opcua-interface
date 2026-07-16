VAR_GLOBAL RETAIN
    (* System and redundancy status exposed through OPC UA.
       REAL_IO_ENABLED is intentionally false by default. It must only be
       enabled after API authorization, audited confirmation and hardware
       validation outside this demo source set. *)
    GVL_System : ST_SystemRuntime := (
        Heartbeat := 0,
        NowMs := 0,
        ControllerId := 'CODESYS-A',
        ControllerRole := 'primary',
        IsActive := TRUE,
        RedundancyHealthy := TRUE,
        ApplicationVersion := '0.3.0-hito3-st',
        ControlAuthority := 'codesys',
        RealIoEnabled := FALSE
    );
END_VAR

VAR_GLOBAL RETAIN
    (* OPC UA command mailbox. Frontend/API writes requests here only through
       the connector. Field outputs are never written directly from web/Grafana/Node-RED. *)
    GVL_OPCUA : ST_OpcuaRuntime;
END_VAR

VAR_GLOBAL RETAIN
    GVL_Recipes : ARRAY[1..50] OF ST_RecipeParameters;
    GVL_Gateways : ARRAY[1..8] OF ST_GatewayStatus;
    GVL_Columns : ST_ColumnBank;
END_VAR

VAR_GLOBAL
    (* Function block instances stay outside retained data. *)
    GVL_ColumnInstances : ARRAY[1..200] OF FB_Column;
    GVL_Simulation : ST_SimulationRuntime := (
        Enabled := TRUE,
        Scenario := 'normal',
        FaultColumnId := 0,
        ForcePrimaryOffline := FALSE,
        ForceGatewayOffline := FALSE,
        ForceScaleOffline := FALSE,
        ForceRefill := FALSE,
        ForceTare := FALSE,
        ForceCriticalAlarm := FALSE
    );
END_VAR
