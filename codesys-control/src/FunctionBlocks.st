FUNCTION_BLOCK FB_DataQuality
VAR_INPUT
    ValidInput : BOOL;
    StableInput : BOOL;
    QualityInput : REAL;
END_VAR
VAR_OUTPUT
    Quality : ST_DataQuality;
END_VAR
Quality.Valid := ValidInput;
Quality.Stable := StableInput;
IF QualityInput < 0.0 THEN
    Quality.Quality := 0.0;
ELSIF QualityInput > 1.0 THEN
    Quality.Quality := 1.0;
ELSE
    Quality.Quality := QualityInput;
END_IF
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_InputScale
VAR_INPUT
    RawWeightKg : REAL;
    Valid : BOOL;
    Stable : BOOL;
END_VAR
VAR_OUTPUT
    Reading : ST_ScaleReading;
END_VAR
Reading.WeightKg := RawWeightKg;
Reading.Quality.Valid := Valid;
Reading.Quality.Stable := Stable;
Reading.Quality.Quality := SEL(Valid AND Stable, 0.0, 1.0);
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_OutputScale EXTENDS FB_InputScale
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_GravimetricFlowEstimator
VAR_INPUT
    Enable : BOOL;
    Sample : ST_ScaleReading;
    NowMs : ULINT;
    WindowS : REAL := 120.0;
    MinPoints : UINT := 8;
    MaxStepKg : REAL := 50.0;
END_VAR
VAR_OUTPUT
    FlowKgH : REAL;
    Quality : REAL;
    Frozen : BOOL;
    ReasonCode : UINT;
END_VAR
VAR
    Weights : ARRAY[1..120] OF REAL;
    TimesS : ARRAY[1..120] OF REAL;
    Count : UINT;
    Index : UINT;
    I : UINT;
    MeanT : REAL;
    MeanW : REAL;
    Denom : REAL;
    Slope : REAL;
    LastWeight : REAL;
END_VAR

IF NOT Enable OR NOT Sample.Quality.Valid OR NOT Sample.Quality.Stable THEN
    Frozen := TRUE;
    ReasonCode := 10;
    RETURN;
END_IF

IF Count > 0 AND ABS(Sample.WeightKg - LastWeight) > MaxStepKg THEN
    Frozen := TRUE;
    ReasonCode := 20; (* refill/outlier/tare/vessel change candidate *)
    RETURN;
END_IF

Index := Index + 1;
IF Index > 120 THEN Index := 1; END_IF
Weights[Index] := Sample.WeightKg;
TimesS[Index] := ULINT_TO_REAL(NowMs) / 1000.0;
LastWeight := Sample.WeightKg;
IF Count < 120 THEN Count := Count + 1; END_IF

IF Count < MinPoints THEN
    Frozen := TRUE;
    ReasonCode := 30;
    RETURN;
END_IF

MeanT := 0.0;
MeanW := 0.0;
FOR I := 1 TO Count DO
    MeanT := MeanT + TimesS[I];
    MeanW := MeanW + Weights[I];
END_FOR
MeanT := MeanT / UINT_TO_REAL(Count);
MeanW := MeanW / UINT_TO_REAL(Count);

Denom := 0.0;
Slope := 0.0;
FOR I := 1 TO Count DO
    Denom := Denom + (TimesS[I] - MeanT) * (TimesS[I] - MeanT);
    Slope := Slope + (TimesS[I] - MeanT) * (Weights[I] - MeanW);
END_FOR

IF Denom <= 0.0 THEN
    Frozen := TRUE;
    ReasonCode := 40;
    RETURN;
END_IF

Slope := Slope / Denom;
FlowKgH := MAX(0.0, -Slope * 3600.0);
Quality := 1.0;
Frozen := FALSE;
ReasonCode := 0;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_SlowPIController
VAR_INPUT
    Enable : BOOL;
    SetpointKgH : REAL;
    MeasuredKgH : REAL;
    DtS : REAL;
    Freeze : BOOL;
    Kp : REAL := 0.08;
    Ki : REAL := 0.01;
    DeadbandPct : REAL := 0.03;
    MaxOutputPct : REAL := 100.0;
    MaxDeltaPct : REAL := 3.0;
END_VAR
VAR_OUTPUT
    OutputPct : REAL;
    IntegratorFrozen : BOOL;
END_VAR
VAR
    Error : REAL;
    Raw : REAL;
    Delta : REAL;
    Integral : REAL;
END_VAR

IF NOT Enable OR Freeze OR SetpointKgH <= 0.0 THEN
    IntegratorFrozen := TRUE;
    RETURN;
END_IF

Error := SetpointKgH - MeasuredKgH;
IF ABS(Error) / SetpointKgH <= DeadbandPct THEN
    IntegratorFrozen := FALSE;
    RETURN;
END_IF

Integral := Integral + Ki * Error * DtS;
Raw := Kp * Error + Integral;
Raw := LIMIT(0.0, Raw, MaxOutputPct);
Delta := LIMIT(-MaxDeltaPct, Raw - OutputPct, MaxDeltaPct);
OutputPct := LIMIT(0.0, OutputPct + Delta, MaxOutputPct);
IntegratorFrozen := FALSE;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_Pump
VAR_INPUT
    Enable : BOOL;
    RequestedPct : REAL;
    SafeStop : BOOL;
END_VAR
VAR_OUTPUT
    Command : ST_PumpCommand;
END_VAR
Command.Enable := Enable AND NOT SafeStop;
Command.SafeStop := SafeStop;
Command.OutputPct := SEL(Command.Enable, 0.0, LIMIT(0.0, RequestedPct, 100.0));
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_TemperatureController
VAR_INPUT
    Enable : BOOL;
    PvC : REAL;
    SpC : REAL;
END_VAR
VAR_OUTPUT
    AlarmHigh : BOOL;
END_VAR
AlarmHigh := Enable AND PvC > SpC + 5.0;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_Aeration
VAR_INPUT
    Enable : BOOL;
    InterlockOk : BOOL;
END_VAR
VAR_OUTPUT
    ValveOpen : BOOL;
END_VAR
ValveOpen := Enable AND InterlockOk;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_Alarm
VAR_INPUT
    ActiveInput : BOOL;
    CodeInput : STRING[40];
    MessageInput : STRING[120];
    Ack : BOOL;
END_VAR
VAR_OUTPUT
    Alarm : ST_ColumnAlarm;
END_VAR
IF ActiveInput THEN
    Alarm.Active := TRUE;
    Alarm.Code := CodeInput;
    Alarm.Message := MessageInput;
    Alarm.RequiresAck := TRUE;
END_IF
IF Ack THEN Alarm.Acked := TRUE; END_IF
IF NOT ActiveInput AND Alarm.Acked THEN Alarm.Active := FALSE; END_IF
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_CommandMailbox
VAR_INPUT
    NowMs : ULINT;
    Incoming : ST_ColumnCommand;
    HasIncoming : BOOL;
END_VAR
VAR_OUTPUT
    Current : ST_ColumnCommand;
    HasPending : BOOL;
END_VAR
IF HasIncoming AND Incoming.ExpiresAtMs > NowMs THEN
    Current := Incoming;
    Current.Status := Accepted;
    HasPending := TRUE;
ELSIF HasIncoming THEN
    Current := Incoming;
    Current.Status := Expired;
    HasPending := FALSE;
END_IF
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_GatewayHealth
VAR_INPUT
    NowMs : ULINT;
    Status : ST_GatewayStatus;
    TimeoutMs : ULINT := 5000;
END_VAR
VAR_OUTPUT
    Healthy : BOOL;
END_VAR
Healthy := Status.Online AND (NowMs - Status.LastHeartbeatMs) <= TimeoutMs AND NOT Status.SafeStateActive;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_RecipeRuntime
VAR_INPUT
    Parameters : ST_RecipeParameters;
END_VAR
VAR_OUTPUT
    ActiveSetpointKgH : REAL;
END_VAR
ActiveSetpointKgH := Parameters.FlowSetpointKgH;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_CampaignRuntime
VAR_INPUT
    Enable : BOOL;
END_VAR
VAR_OUTPUT
    Running : BOOL;
END_VAR
Running := Enable;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_FailSafe
VAR_INPUT
    CriticalAlarm : BOOL;
    GatewayHealthy : BOOL;
    DataValid : BOOL;
END_VAR
VAR_OUTPUT
    SafeStop : BOOL;
END_VAR
SafeStop := CriticalAlarm OR NOT GatewayHealthy OR NOT DataValid;
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_ColumnStateMachine
VAR_INPUT
    Enabled : BOOL;
    Start : BOOL;
    Pause : BOOL;
    Stop : BOOL;
    MaintenanceMode : BOOL;
    AlarmActive : BOOL;
END_VAR
VAR_OUTPUT
    State : E_ColumnState;
END_VAR
IF NOT Enabled THEN
    State := OutOfService;
ELSIF MaintenanceMode THEN
    State := Maintenance;
ELSIF AlarmActive THEN
    State := Alarm;
ELSIF Stop THEN
    State := Available;
ELSIF Pause THEN
    State := Paused;
ELSIF Start THEN
    State := Running;
ELSIF State = Offline THEN
    State := Available;
END_IF
END_FUNCTION_BLOCK

FUNCTION_BLOCK FB_Column
VAR_INPUT
    Config : ST_ColumnConfig;
    NowMs : ULINT;
    InputScale : ST_ScaleReading;
    OutputScale : ST_ScaleReading;
    Command : ST_ColumnCommand;
    GatewayStatus : ST_GatewayStatus;
END_VAR
VAR_OUTPUT
    Status : ST_ColumnStatus;
    PumpCommand : ST_PumpCommand;
END_VAR
VAR
    Estimator : FB_GravimetricFlowEstimator;
    PI : FB_SlowPIController;
    Pump : FB_Pump;
    Gateway : FB_GatewayHealth;
    FailSafe : FB_FailSafe;
    StateMachine : FB_ColumnStateMachine;
END_VAR

Gateway(NowMs := NowMs, Status := GatewayStatus);
Estimator(Enable := Config.Enabled, Sample := InputScale, NowMs := NowMs, WindowS := Config.FlowWindowS, MinPoints := Config.MinFlowPoints);
FailSafe(CriticalAlarm := Status.Alarm.Active, GatewayHealthy := Gateway.Healthy, DataValid := InputScale.Quality.Valid);
PI(Enable := Config.Enabled, SetpointKgH := Config.FlowSetpointKgH, MeasuredKgH := Estimator.FlowKgH, DtS := 30.0, Freeze := FailSafe.SafeStop OR Estimator.Frozen);
Pump(Enable := Config.Enabled, RequestedPct := PI.OutputPct, SafeStop := FailSafe.SafeStop);
StateMachine(Enabled := Config.Enabled, Start := Command.CommandType = 'start', Pause := Command.CommandType = 'pause', Stop := Command.CommandType = 'stop', MaintenanceMode := Command.CommandType = 'maintenance', AlarmActive := Status.Alarm.Active);

Status.State := StateMachine.State;
Status.InputScale := InputScale;
Status.OutputScale := OutputScale;
Status.FlowMeasuredKgH := Estimator.FlowKgH;
Status.FlowQuality := Estimator.Quality;
Status.PumpOutputPct := Pump.Command.OutputPct;
Status.PIIntegratorFrozen := PI.IntegratorFrozen;
Status.GatewayHealthy := Gateway.Healthy;
PumpCommand := Pump.Command;
END_FUNCTION_BLOCK
