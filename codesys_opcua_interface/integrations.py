from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any


CONTROL_KEYWORDS = {
    "/commands",
    "CommandMailbox",
    "pump_output_pct write",
    "write_register",
    "write_coil",
    "modbus-write",
    "control_command",
}


@dataclass(frozen=True)
class DashboardInfo:
    uid: str
    title: str
    path: str
    editable: bool
    tags: list[str]
    panels: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FlowInfo:
    id: str
    label: str
    path: str
    disabled: bool
    contains_control_keywords: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def list_grafana_dashboards(root: Path | None = None) -> list[DashboardInfo]:
    base = (root or repository_root()) / "grafana" / "dashboards"
    dashboards: list[DashboardInfo] = []
    for path in sorted(base.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        dashboards.append(
            DashboardInfo(
                uid=str(data.get("uid", path.stem)),
                title=str(data.get("title", path.stem)),
                path=str(path.relative_to(root or repository_root())),
                editable=bool(data.get("editable", False)),
                tags=[str(tag) for tag in data.get("tags", [])],
                panels=len(data.get("panels", [])),
            )
        )
    return dashboards


def list_node_red_flows(root: Path | None = None) -> list[FlowInfo]:
    base = (root or repository_root()) / "node-red" / "flows"
    flows: list[FlowInfo] = []
    for path in sorted(base.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        serialized = json.dumps(data)
        contains_control = any(keyword in serialized for keyword in CONTROL_KEYWORDS)
        for node in data:
            if node.get("type") == "tab":
                flows.append(
                    FlowInfo(
                        id=str(node.get("id", path.stem)),
                        label=str(node.get("label", path.stem)),
                        path=str(path.relative_to(root or repository_root())),
                        disabled=bool(node.get("disabled", False)),
                        contains_control_keywords=contains_control,
                    )
                )
    return flows


def integration_status(root: Path | None = None) -> dict[str, Any]:
    dashboards = list_grafana_dashboards(root)
    flows = list_node_red_flows(root)
    return {
        "grafana": {
            "enabled": True,
            "base_path": "/grafana/",
            "dashboards": [dashboard.to_dict() for dashboard in dashboards],
            "control_allowed": False,
        },
        "node_red": {
            "enabled": True,
            "runtime_base_path": "/node-red/",
            "admin_base_path": "/node-red-admin/",
            "flows": [flow.to_dict() for flow in flows],
            "control_allowed": False,
        },
    }
