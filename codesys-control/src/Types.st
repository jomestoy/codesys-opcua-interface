TYPE E_ColumnState :
(
    Offline,
    OutOfService,
    Available,
    Preparation,
    Ready,
    Running,
    Paused,
    Alarm,
    Finished,
    Maintenance
);
END_TYPE

TYPE E_CommandStatus :
(
    Pending,
    Accepted,
    Rejected,
    Applied,
    Expired,
    Failed
);
END_TYPE

TYPE ST_DataQuality :
STRUCT
    Valid : BOOL;
    Stable : BOOL;
    Quality : REAL;
    SourceTimestampMs : ULINT;
    ReasonCode : UINT;
END_STRUCT
END_TYPE

TYPE ST_ScaleReading :
STRUCT
    WeightKg : REAL;
    Quality : ST_DataQuality;
    IsRefill : BOOL;
    IsTare : BOOL;
    VesselChanged : BOOL;
END_STRUCT
END_TYPE

TYPE ST_PumpCommand :
STRUCT
    OutputPct : REAL;
    Enable : BOOL;
    SafeStop : BOOL;
END_STRUCT
END_TYPE

TYPE ST_RecipeParameters :
STRUCT
    RecipeId : STRING[40];
    FlowSetpointKgH : REAL;
    TemperatureSetpointC : REAL;
    AerationEnabled : BOOL;
    PIKp : REAL;
    PIKi : REAL;
END_STRUCT
END_TYPE

TYPE ST_ColumnCommand :
STRUCT
    CommandId : STRING[64];
    ColumnId : UINT;
    CommandType : STRING[32];
    RequestedValue : REAL;
    RequestedBy : STRING[80];
    RequestedAtMs : ULINT;
    ExpiresAtMs : ULINT;
    Sequence : UDINT;
    Status : E_CommandStatus;
    Result : STRING[120];
    AppliedAtMs : ULINT;
END_STRUCT
END_TYPE

TYPE ST_ColumnAlarm :
STRUCT
    Active : BOOL;
    Severity : UINT;
    Code : STRING[40];
    Message : STRING[120];
    RequiresAck : BOOL;
    Acked : BOOL;
END_STRUCT
END_TYPE

TYPE ST_ColumnConfig :
STRUCT
    ColumnId : UINT;
    Enabled : BOOL;
    FlowSetpointKgH : REAL;
    FlowWindowS : REAL;
    MinFlowPoints : UINT;
    MaxPumpOutputPct : REAL;
    MaxOutputDeltaPct : REAL;
    BriefLossTimeoutMs : ULINT;
    ProlongedLossTimeoutMs : ULINT;
END_STRUCT
END_TYPE

TYPE ST_ColumnStatus :
STRUCT
    State : E_ColumnState;
    InputScale : ST_ScaleReading;
    OutputScale : ST_ScaleReading;
    FlowMeasuredKgH : REAL;
    FlowQuality : REAL;
    PumpOutputPct : REAL;
    TemperaturePvC : REAL;
    PIIntegratorFrozen : BOOL;
    GatewayHealthy : BOOL;
    Alarm : ST_ColumnAlarm;
END_STRUCT
END_TYPE

TYPE ST_GatewayStatus :
STRUCT
    GatewayId : STRING[40];
    Online : BOOL;
    LastHeartbeatMs : ULINT;
    Quality : REAL;
    SafeStateActive : BOOL;
END_STRUCT
END_TYPE

TYPE ST_SystemRuntime :
STRUCT
    Heartbeat : ULINT;
    NowMs : ULINT;
    ControllerId : STRING[40];
    ControllerRole : STRING[20];
    IsActive : BOOL;
    RedundancyHealthy : BOOL;
    ApplicationVersion : STRING[40];
    ControlAuthority : STRING[40];
    RealIoEnabled : BOOL;
END_STRUCT
END_TYPE

TYPE ST_OpcuaRuntime :
STRUCT
    CommandMailbox : ST_ColumnCommand;
    CommandConfirmation : ST_ColumnCommand;
    HasCommand : BOOL;
    LastAcceptedSequence : UDINT;
    LastRejectedSequence : UDINT;
END_STRUCT
END_TYPE

TYPE ST_ColumnRuntime :
STRUCT
    Config : ST_ColumnConfig;
    Status : ST_ColumnStatus;
    InputScale : ST_ScaleReading;
    OutputScale : ST_ScaleReading;
    GatewayStatus : ST_GatewayStatus;
    PumpCommand : ST_PumpCommand;
    LastCommand : ST_ColumnCommand;
END_STRUCT
END_TYPE

TYPE ST_ColumnBank :
STRUCT
    Columns : ARRAY[1..200] OF ST_ColumnRuntime;
END_STRUCT
END_TYPE

TYPE ST_SimulationRuntime :
STRUCT
    Enabled : BOOL;
    Scenario : STRING[40];
    FaultColumnId : UINT;
    ForcePrimaryOffline : BOOL;
    ForceGatewayOffline : BOOL;
    ForceScaleOffline : BOOL;
    ForceRefill : BOOL;
    ForceTare : BOOL;
    ForceCriticalAlarm : BOOL;
END_STRUCT
END_TYPE
