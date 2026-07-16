VAR_GLOBAL
    (* System and redundancy status exposed through OPC UA. *)
    GVL_System_Heartbeat : ULINT;
    GVL_System_ControllerId : STRING[40] := 'CODESYS-A';
    GVL_System_ControllerRole : STRING[20] := 'primary';
    GVL_System_IsActive : BOOL := TRUE;
    GVL_System_RedundancyHealthy : BOOL := TRUE;
    GVL_System_ApplicationVersion : STRING[40] := '0.1.0-st-template';
    GVL_System_ControlAuthority : STRING[40] := 'codesys';
END_VAR

VAR_GLOBAL
    GVL_OPCUA_CommandMailbox : ST_ColumnCommand;
    GVL_OPCUA_CommandConfirmation : ST_ColumnCommand;
END_VAR

VAR_GLOBAL
    GVL_Recipes : ARRAY[1..50] OF ST_RecipeParameters;
    GVL_Gateways : ARRAY[1..8] OF ST_GatewayStatus;
END_VAR

VAR_GLOBAL
    GVL_Columns_Config : ARRAY[1..200] OF ST_ColumnConfig;
    GVL_Columns_Status : ARRAY[1..200] OF ST_ColumnStatus;
    GVL_Columns_Instances : ARRAY[1..200] OF FB_Column;
END_VAR
