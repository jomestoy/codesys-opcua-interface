from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from .command_model import ColumnCommand, CommandMailbox, CommandStatus
from .opcua_nodes import SYSTEM_NODES, command_confirmation_symbol, command_mailbox_symbol


class CodesysClientProtocol(Protocol):
    endpoint_url: str

    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def read_value(self, symbol: str): ...
    async def read_many(self, symbols: list[str]) -> dict[str, object]: ...
    async def write_value(self, symbol: str, value: object) -> None: ...


@dataclass
class EndpointHealth:
    endpoint_url: str
    controller_id: str
    controller_role: str
    is_active: bool
    online: bool
    redundancy_healthy: bool
    heartbeat: int | None
    application_version: str
    control_authority: str
    last_error: str = ""


class RedundancyError(RuntimeError):
    pass


class CodesysOpcuaConnector:
    def __init__(self, primary: CodesysClientProtocol, secondary: CodesysClientProtocol) -> None:
        self.primary = primary
        self.secondary = secondary
        self.mailbox = CommandMailbox()
        self.last_health: list[EndpointHealth] = []

    async def connect_all(self) -> list[EndpointHealth]:
        health: list[EndpointHealth] = []
        for client in [self.primary, self.secondary]:
            try:
                await client.connect()
                health.append(await self.read_endpoint_health(client, online=True))
            except Exception as exc:  # noqa: BLE001 - report endpoint health, do not hide state
                health.append(EndpointHealth(
                    endpoint_url=client.endpoint_url,
                    controller_id="unknown",
                    controller_role="unknown",
                    is_active=False,
                    online=False,
                    redundancy_healthy=False,
                    heartbeat=None,
                    application_version="unknown",
                    control_authority="unknown",
                    last_error=str(exc),
                ))
        self.last_health = health
        return health

    async def read_endpoint_health(self, client: CodesysClientProtocol, online: bool = True) -> EndpointHealth:
        symbols = {key: spec.symbol() for key, spec in SYSTEM_NODES.items()}
        values = await client.read_many(list(symbols.values()))
        return EndpointHealth(
            endpoint_url=client.endpoint_url,
            controller_id=str(values.get(symbols["controller_id"], "unknown")),
            controller_role=str(values.get(symbols["controller_role"], "unknown")),
            is_active=bool(values.get(symbols["is_active"], False)),
            online=online,
            redundancy_healthy=bool(values.get(symbols["redundancy_healthy"], False)),
            heartbeat=int(values.get(symbols["heartbeat"], 0) or 0),
            application_version=str(values.get(symbols["application_version"], "unknown")),
            control_authority=str(values.get(symbols["control_authority"], "unknown")),
        )

    async def active_client(self) -> CodesysClientProtocol:
        health = await self.connect_all()
        active = [item for item in health if item.online and item.is_active and item.control_authority == "codesys"]
        if len(active) != 1:
            raise RedundancyError(f"se esperaba exactamente un CODESYS activo, activos={len(active)}")
        active_url = active[0].endpoint_url
        return self.primary if self.primary.endpoint_url == active_url else self.secondary

    async def submit_command(self, command: ColumnCommand, idempotency_key: str | None = None) -> ColumnCommand:
        submitted = self.mailbox.submit(command, idempotency_key=idempotency_key)
        active = await self.active_client()
        await active.write_value(command_mailbox_symbol(), submitted.as_mailbox_payload())
        confirmation = await active.read_value(command_confirmation_symbol())
        return self._apply_confirmation(submitted.command_id, confirmation)

    async def subscribe_status(self, symbols: list[str], callback, publishing_interval_ms: int = 1000):
        active = await self.active_client()
        if not hasattr(active, "subscribe"):
            raise RuntimeError("cliente activo no soporta suscripciones")
        return await active.subscribe(symbols, callback, publishing_interval_ms=publishing_interval_ms)

    def _apply_confirmation(self, command_id: str, confirmation: dict | None) -> ColumnCommand:
        command = self.mailbox.get(command_id)
        if not confirmation:
            command.status = CommandStatus.FAILED
            command.result = "sin_confirmacion_codesys"
            return command
        if confirmation.get("CommandId") != command_id:
            command.status = CommandStatus.FAILED
            command.result = "confirmacion_no_coincide"
            return command
        status = confirmation.get("Status")
        if status == CommandStatus.APPLIED.value:
            command.status = CommandStatus.APPLIED
            command.result = str(confirmation.get("Result", "applied"))
            command.applied_at = datetime.now(timezone.utc)
        elif status == CommandStatus.ACCEPTED.value:
            self.mailbox.acknowledge_from_codesys(command_id, accepted=True, result=str(confirmation.get("Result", "")))
        elif status == CommandStatus.REJECTED.value:
            self.mailbox.acknowledge_from_codesys(command_id, accepted=False, result=str(confirmation.get("Result", "")))
        else:
            command.status = CommandStatus.FAILED
            command.result = f"estado_confirmacion_desconocido:{status}"
        return command
