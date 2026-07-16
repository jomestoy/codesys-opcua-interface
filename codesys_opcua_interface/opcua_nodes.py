from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NodeDirection(str, Enum):
    READ = "read"
    WRITE_GUARDED = "write_guarded"


@dataclass(frozen=True)
class OpcuaNodeSpec:
    key: str
    symbol_template: str
    direction: NodeDirection
    data_type: str
    description: str

    def symbol(self, column_id: int | None = None) -> str:
        if "{column:03}" in self.symbol_template:
            if column_id is None or not 1 <= column_id <= 200:
                raise ValueError("column_id requerido en rango 1..200")
            return self.symbol_template.format(column=column_id)
        return self.symbol_template


SYSTEM_NODES: dict[str, OpcuaNodeSpec] = {
    "controller_id": OpcuaNodeSpec("controller_id", "GVL_System.ControllerId", NodeDirection.READ, "STRING", "Identificador controlador"),
    "controller_role": OpcuaNodeSpec("controller_role", "GVL_System.ControllerRole", NodeDirection.READ, "STRING", "Primary/Secondary"),
    "is_active": OpcuaNodeSpec("is_active", "GVL_System.IsActive", NodeDirection.READ, "BOOL", "Controlador activo"),
    "redundancy_healthy": OpcuaNodeSpec("redundancy_healthy", "GVL_System.RedundancyHealthy", NodeDirection.READ, "BOOL", "Salud redundancia"),
    "heartbeat": OpcuaNodeSpec("heartbeat", "GVL_System.Heartbeat", NodeDirection.READ, "ULINT", "Heartbeat"),
    "application_version": OpcuaNodeSpec("application_version", "GVL_System.ApplicationVersion", NodeDirection.READ, "STRING", "Version aplicacion"),
    "control_authority": OpcuaNodeSpec("control_authority", "GVL_System.ControlAuthority", NodeDirection.READ, "STRING", "Autoridad de control"),
}


COLUMN_NODES: dict[str, OpcuaNodeSpec] = {
    "input_weight_kg": OpcuaNodeSpec("input_weight_kg", "GVL_Columns.Columns[{column:03}].Status.InputScale.WeightKg", NodeDirection.READ, "REAL", "Peso alimentacion"),
    "output_weight_kg": OpcuaNodeSpec("output_weight_kg", "GVL_Columns.Columns[{column:03}].Status.OutputScale.WeightKg", NodeDirection.READ, "REAL", "Peso salida"),
    "flow_measured_kg_h": OpcuaNodeSpec("flow_measured_kg_h", "GVL_Columns.Columns[{column:03}].Status.FlowMeasuredKgH", NodeDirection.READ, "REAL", "Flujo calculado CODESYS"),
    "flow_setpoint_kg_h": OpcuaNodeSpec("flow_setpoint_kg_h", "GVL_Columns.Columns[{column:03}].Config.FlowSetpointKgH", NodeDirection.WRITE_GUARDED, "REAL", "Setpoint de flujo autorizado"),
    "pump_output_pct": OpcuaNodeSpec("pump_output_pct", "GVL_Columns.Columns[{column:03}].Status.PumpOutputPct", NodeDirection.READ, "REAL", "Mando bomba calculado CODESYS"),
    "state": OpcuaNodeSpec("state", "GVL_Columns.Columns[{column:03}].Status.State", NodeDirection.READ, "E_ColumnState", "Estado columna"),
    "data_quality": OpcuaNodeSpec("data_quality", "GVL_Columns.Columns[{column:03}].Status.FlowQuality", NodeDirection.READ, "REAL", "Calidad dato control"),
}


COMMAND_NODES: dict[str, OpcuaNodeSpec] = {
    "mailbox": OpcuaNodeSpec("mailbox", "GVL_OPCUA.CommandMailbox", NodeDirection.WRITE_GUARDED, "ST_ColumnCommand", "Buzon de solicitud de comando"),
    "confirmation": OpcuaNodeSpec("confirmation", "GVL_OPCUA.CommandConfirmation", NodeDirection.READ, "ST_ColumnCommand", "Confirmacion publicada por CODESYS"),
}


def all_node_specs() -> dict[str, OpcuaNodeSpec]:
    return {**SYSTEM_NODES, **COLUMN_NODES, **COMMAND_NODES}


def command_mailbox_symbol() -> str:
    return COMMAND_NODES["mailbox"].symbol()


def command_confirmation_symbol() -> str:
    return COMMAND_NODES["confirmation"].symbol()
