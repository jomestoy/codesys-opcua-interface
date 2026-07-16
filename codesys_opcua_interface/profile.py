from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from typing import Any


REAL_IO_ENABLED = os.getenv("REAL_IO_ENABLED", "false").strip().lower() == "true"


@dataclass(frozen=True)
class NodeTemplate:
    key: str
    label: str
    node_template: str
    direction: str
    unit: str
    metric: str
    required: bool = True


NODE_TEMPLATES: list[NodeTemplate] = [
    NodeTemplate("input_weight", "Peso entrada", "ns=<validado>;s=GVL_Columns.C{column:03}.InputWeightKg", "read", "kg", "input_weight"),
    NodeTemplate("output_weight", "Peso salida", "ns=<validado>;s=GVL_Columns.C{column:03}.OutputWeightKg", "read", "kg", "output_weight"),
    NodeTemplate("temperature_pv", "Temperatura PV", "ns=<validado>;s=GVL_Columns.C{column:03}.TemperaturePv", "read", "C", "temperature_pv"),
    NodeTemplate("pump_output", "Salida bomba", "ns=<validado>;s=GVL_Columns.C{column:03}.PumpOutputPct", "write_guarded", "%", "pump_output"),
    NodeTemplate("flow_setpoint", "SP flujo", "ns=<validado>;s=GVL_Columns.C{column:03}.FlowSetpointLph", "write_guarded", "L/h", "flow_setpoint"),
    NodeTemplate("command", "Comando seguro", "ns=<validado>;s=GVL_Columns.C{column:03}.Command", "write_guarded", "enum", "command", required=False),
    NodeTemplate("heartbeat", "Heartbeat CODESYS", "ns=<validado>;s=GVL_System.Heartbeat", "read", "bool", "heartbeat"),
]


def build_profile() -> dict[str, Any]:
    endpoint = os.getenv("CODESYS_OPCUA_ENDPOINT", "opc.tcp://<codesys-runtime>:4840")
    namespace = os.getenv("CODESYS_OPCUA_NAMESPACE", "urn:<codesys-project>:columnas")
    profile = {
        "id": "CODESYS-OPCUA-01",
        "name": "Interface CODESYS OPC UA",
        "mode": "Plantilla segura",
        "server_role": "CODESYS OPC UA Server",
        "client_role": "Gateway/API como OPC UA client",
        "endpoint_url": endpoint,
        "namespace_uri": namespace,
        "security_policy": os.getenv("CODESYS_OPCUA_SECURITY_POLICY", "Basic256Sha256"),
        "security_mode": os.getenv("CODESYS_OPCUA_SECURITY_MODE", "SignAndEncrypt"),
        "polling_ms": int(os.getenv("OPCUA_POLLING_MS", "1000")),
        "real_io_enabled": REAL_IO_ENABLED,
        "write_authority": "Bloqueada",
        "nodes": [asdict(node) for node in NODE_TEMPLATES],
        "command_flow": [
            "Operador solicita cambio en interfaz",
            "API valida permiso, rango, receta/campana y auditoria",
            "Gateway prepara escritura OPC UA con TTL e idempotencia",
            "CODESYS confirma y aplica interlocks locales",
            "API refleja estado por lectura OPC UA",
        ],
    }
    profile["validation_errors"] = validate_profile(profile)
    return profile


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    endpoint = str(profile.get("endpoint_url", ""))
    if not endpoint.startswith("opc.tcp://"):
        errors.append("endpoint_url debe usar opc.tcp://")
    if profile.get("security_mode") != "SignAndEncrypt":
        errors.append("security_mode debe ser SignAndEncrypt")
    if profile.get("real_io_enabled"):
        errors.append("REAL_IO_ENABLED debe permanecer false en esta plantilla")
    keys = {node["key"] for node in profile.get("nodes", [])}
    for required in {"input_weight", "output_weight", "flow_setpoint", "pump_output", "heartbeat"}:
        if required not in keys:
            errors.append(f"Falta simbolo requerido: {required}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(prog="codesys-opcua-interface")
    parser.add_argument("command", choices=["export", "validate"])
    args = parser.parse_args()
    profile = build_profile()
    if args.command == "export":
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    if args.command == "validate":
        errors = profile["validation_errors"]
        print("Perfil valido offline" if not errors else "\n".join(errors))
        raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
