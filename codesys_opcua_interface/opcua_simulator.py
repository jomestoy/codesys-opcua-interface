from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .command_model import CommandStatus
from .opcua_nodes import command_confirmation_symbol, command_mailbox_symbol


@dataclass
class SimulatedOpcuaEndpoint:
    endpoint_url: str
    namespace_uri: str = "urn:<codesys-project>:columnas"
    controller_id: str = "CODESYS-A"
    controller_role: str = "primary"
    is_active: bool = True
    online: bool = True
    nodes: dict[str, Any] = field(default_factory=dict)
    writes: list[tuple[str, Any]] = field(default_factory=list)
    namespace_index: int = 4

    async def connect(self) -> None:
        if not self.online:
            raise ConnectionError(f"{self.endpoint_url} offline")
        self._seed_system_nodes()

    async def disconnect(self) -> None:
        return None

    def node_id(self, symbol: str) -> str:
        return f"ns={self.namespace_index};s={symbol}"

    async def read_value(self, symbol: str) -> Any:
        self._seed_system_nodes()
        return self.nodes.get(symbol)

    async def read_many(self, symbols: list[str]) -> dict[str, Any]:
        return {symbol: await self.read_value(symbol) for symbol in symbols}

    async def write_value(self, symbol: str, value: Any) -> None:
        if symbol == command_mailbox_symbol():
            self._handle_mailbox(value)
        else:
            self.nodes[symbol] = value
        self.writes.append((symbol, value))

    async def subscribe(self, symbols: list[str], callback: Any, publishing_interval_ms: int = 1000) -> list[str]:
        return [self.node_id(symbol) for symbol in symbols]

    def _seed_system_nodes(self) -> None:
        self.nodes["GVL_System.ControllerId"] = self.controller_id
        self.nodes["GVL_System.ControllerRole"] = self.controller_role
        self.nodes["GVL_System.IsActive"] = self.is_active
        self.nodes["GVL_System.RedundancyHealthy"] = self.online
        self.nodes["GVL_System.Heartbeat"] = int(datetime.now(timezone.utc).timestamp())
        self.nodes["GVL_System.ApplicationVersion"] = "0.1.0-sim-opcua"
        self.nodes["GVL_System.ControlAuthority"] = "codesys"

    def _handle_mailbox(self, payload: dict[str, Any]) -> None:
        confirmation = dict(payload)
        if not self.is_active:
            confirmation["Status"] = CommandStatus.REJECTED.value
            confirmation["Result"] = f"rejected_by_standby:{self.controller_id}"
        else:
            confirmation["Status"] = CommandStatus.APPLIED.value
            confirmation["Result"] = f"applied_by:{self.controller_id}"
            confirmation["AppliedAt"] = datetime.now(timezone.utc).isoformat()
        self.nodes[command_confirmation_symbol()] = confirmation
