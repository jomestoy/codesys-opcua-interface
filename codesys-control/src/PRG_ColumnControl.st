PROGRAM PRG_ColumnControl
VAR
    ColumnIndex : UINT;
    InitDone : BOOL;
    CommandForColumn : ST_ColumnCommand;
    EmptyCommand : ST_ColumnCommand;
    TargetColumnId : UINT;
    AcceptCommand : BOOL;
    RejectCommand : BOOL;
END_VAR

(* Main control program for the 200-column model.
   Intended task: normal task, after fast watchdog/input refresh.
   CODESYS remains final authority: commands are accepted only from the OPC UA
   mailbox, checked here, then applied to the corresponding FB_Column. *)

IF NOT InitDone THEN
    FOR ColumnIndex := 1 TO 200 DO
        GVL_Columns.Columns[ColumnIndex].Config.ColumnId := ColumnIndex;
        GVL_Columns.Columns[ColumnIndex].Config.Enabled := TRUE;
        GVL_Columns.Columns[ColumnIndex].Config.FlowSetpointKgH := 12.0;
        GVL_Columns.Columns[ColumnIndex].Config.FlowWindowS := 120.0;
        GVL_Columns.Columns[ColumnIndex].Config.MinFlowPoints := 8;
        GVL_Columns.Columns[ColumnIndex].Config.MaxPumpOutputPct := 100.0;
        GVL_Columns.Columns[ColumnIndex].Config.MaxOutputDeltaPct := 3.0;
        GVL_Columns.Columns[ColumnIndex].Config.BriefLossTimeoutMs := 15000;
        GVL_Columns.Columns[ColumnIndex].Config.ProlongedLossTimeoutMs := 60000;
        GVL_Columns.Columns[ColumnIndex].InputScale.WeightKg := 1000.0;
        GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Valid := TRUE;
        GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Stable := TRUE;
        GVL_Columns.Columns[ColumnIndex].InputScale.Quality.Quality := 1.0;
        GVL_Columns.Columns[ColumnIndex].OutputScale.WeightKg := 0.0;
        GVL_Columns.Columns[ColumnIndex].OutputScale.Quality.Valid := TRUE;
        GVL_Columns.Columns[ColumnIndex].OutputScale.Quality.Stable := TRUE;
        GVL_Columns.Columns[ColumnIndex].OutputScale.Quality.Quality := 1.0;
        GVL_Columns.Columns[ColumnIndex].GatewayStatus.GatewayId := 'gateway-demo';
        GVL_Columns.Columns[ColumnIndex].GatewayStatus.Online := TRUE;
        GVL_Columns.Columns[ColumnIndex].GatewayStatus.Quality := 1.0;
        GVL_Columns.Columns[ColumnIndex].Status.State := Available;
    END_FOR
    GVL_Recipes[1].RecipeId := 'REC-DEMO-001';
    GVL_Recipes[1].FlowSetpointKgH := 12.0;
    GVL_Recipes[1].TemperatureSetpointC := 25.0;
    GVL_Recipes[1].AerationEnabled := TRUE;
    GVL_Recipes[1].PIKp := 0.08;
    GVL_Recipes[1].PIKi := 0.01;
    InitDone := TRUE;
END_IF

GVL_System.Heartbeat := GVL_System.Heartbeat + 1;
GVL_System.NowMs := GVL_System.NowMs + 100;
GVL_System.ControlAuthority := 'codesys';

AcceptCommand := FALSE;
RejectCommand := FALSE;
TargetColumnId := GVL_OPCUA.CommandMailbox.ColumnId;

IF GVL_OPCUA.HasCommand AND GVL_OPCUA.CommandMailbox.Status = Pending THEN
    IF NOT GVL_System.IsActive THEN
        RejectCommand := TRUE;
        GVL_OPCUA.CommandMailbox.Result := 'controlador no activo';
    ELSIF GVL_OPCUA.CommandMailbox.ExpiresAtMs <= GVL_System.NowMs THEN
        GVL_OPCUA.CommandMailbox.Status := Expired;
        RejectCommand := TRUE;
        GVL_OPCUA.CommandMailbox.Result := 'comando expirado';
    ELSIF TargetColumnId < 1 OR TargetColumnId > 200 THEN
        RejectCommand := TRUE;
        GVL_OPCUA.CommandMailbox.Result := 'columna fuera de rango';
    ELSIF NOT GVL_Columns.Columns[TargetColumnId].Config.Enabled THEN
        RejectCommand := TRUE;
        GVL_OPCUA.CommandMailbox.Result := 'columna deshabilitada';
    ELSE
        AcceptCommand := TRUE;
        GVL_OPCUA.CommandMailbox.Status := Accepted;
        GVL_OPCUA.CommandMailbox.Result := 'aceptado por CODESYS';
        GVL_OPCUA.LastAcceptedSequence := GVL_OPCUA.CommandMailbox.Sequence;
    END_IF
END_IF

IF RejectCommand THEN
    IF GVL_OPCUA.CommandMailbox.Status <> Expired THEN
        GVL_OPCUA.CommandMailbox.Status := Rejected;
    END_IF
    GVL_OPCUA.LastRejectedSequence := GVL_OPCUA.CommandMailbox.Sequence;
    GVL_OPCUA.CommandMailbox.AppliedAtMs := GVL_System.NowMs;
    GVL_OPCUA.CommandConfirmation := GVL_OPCUA.CommandMailbox;
    GVL_OPCUA.HasCommand := FALSE;
END_IF

FOR ColumnIndex := 1 TO 200 DO
    CommandForColumn := EmptyCommand;
    IF AcceptCommand AND TargetColumnId = ColumnIndex THEN
        CommandForColumn := GVL_OPCUA.CommandMailbox;
        GVL_Columns.Columns[ColumnIndex].LastCommand := GVL_OPCUA.CommandMailbox;
    END_IF

    GVL_ColumnInstances[ColumnIndex](
        Config := GVL_Columns.Columns[ColumnIndex].Config,
        NowMs := GVL_System.NowMs,
        InputScale := GVL_Columns.Columns[ColumnIndex].InputScale,
        OutputScale := GVL_Columns.Columns[ColumnIndex].OutputScale,
        Command := CommandForColumn,
        GatewayStatus := GVL_Columns.Columns[ColumnIndex].GatewayStatus
    );

    GVL_Columns.Columns[ColumnIndex].Status := GVL_ColumnInstances[ColumnIndex].Status;
    GVL_Columns.Columns[ColumnIndex].PumpCommand := GVL_ColumnInstances[ColumnIndex].PumpCommand;
END_FOR

IF AcceptCommand THEN
    GVL_OPCUA.CommandMailbox.Status := Applied;
    GVL_OPCUA.CommandMailbox.AppliedAtMs := GVL_System.NowMs;
    GVL_OPCUA.CommandConfirmation := GVL_OPCUA.CommandMailbox;
    GVL_OPCUA.HasCommand := FALSE;
END_IF
END_PROGRAM
