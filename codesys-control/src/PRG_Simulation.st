PROGRAM PRG_Simulation
VAR
    ColumnIndex : UINT;
    ConsumptionKg : REAL;
    SimulatedFlowKgH : REAL;
    Faulted : BOOL;
END_VAR

(* Offline simulation task. This program must not be used as real hardware I/O.
   It is disabled automatically when RealIoEnabled becomes TRUE. *)

IF NOT GVL_Simulation.Enabled OR GVL_System.RealIoEnabled THEN
    RETURN;
END_IF

IF GVL_Simulation.ForcePrimaryOffline THEN
    GVL_System.IsActive := FALSE;
    GVL_System.ControllerRole := 'primary-offline';
ELSE
    GVL_System.IsActive := TRUE;
    GVL_System.ControllerRole := 'primary';
END_IF

FOR ColumnIndex := 1 TO 200 DO
    Faulted := GVL_Simulation.FaultColumnId = ColumnIndex;

    GVL_Columns.Columns[ColumnIndex].GatewayStatus.Online := NOT (GVL_Simulation.ForceGatewayOffline AND Faulted);
    GVL_Columns.Columns[ColumnIndex].GatewayStatus.LastHeartbeatMs := GVL_System.NowMs;
    GVL_Columns.Columns[ColumnIndex].GatewayStatus.SafeStateActive := GVL_Simulation.ForceGatewayOffline AND Faulted;

    GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Valid := NOT (GVL_Simulation.ForceScaleOffline AND Faulted);
    GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Stable := NOT (GVL_Simulation.ForceTare AND Faulted);
    GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Quality := SEL(GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Valid, 0.0, 1.0);
    GVL_Columns.Columns[ColumnIndex].InputScale.IsRefill := GVL_Simulation.ForceRefill AND Faulted;
    GVL_Columns.Columns[ColumnIndex].InputScale.IsTare := GVL_Simulation.ForceTare AND Faulted;

    IF GVL_Simulation.ForceRefill AND Faulted THEN
        GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg := GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg + 100.0;
    ELSIF GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Valid THEN
        SimulatedFlowKgH := GVL_Columns.Columns[ColumnIndex].PumpCommand.OutputPct / 100.0 * GVL_Columns.Columns[ColumnIndex].Config.FlowSetpointKgH;
        ConsumptionKg := SimulatedFlowKgH / 36000.0; (* Approx. 100 ms task step. *)
        IF GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg > ConsumptionKg THEN
            GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg := GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg - ConsumptionKg;
        END_IF
        GVL_Columns.Columns[ColumnIndex].OutputScale.WeightKg := GVL_Columns.Columns[ColumnIndex].OutputScale.WeightKg + ConsumptionKg * 0.98;
    END_IF

    IF GVL_Simulation.ForceCriticalAlarm AND Faulted THEN
        GVL_Columns.Columns[ColumnIndex].Status.Alarm.Active := TRUE;
        GVL_Columns.Columns[ColumnIndex].Status.Alarm.Severity := 3;
        GVL_Columns.Columns[ColumnIndex].Status.Alarm.Code := 'SIM_CRITICAL';
        GVL_Columns.Columns[ColumnIndex].Status.Alarm.Message := 'alarma critica simulada';
        GVL_Columns.Columns[ColumnIndex].Status.Alarm.RequiresAck := TRUE;
    END_IF
END_FOR
END_PROGRAM
