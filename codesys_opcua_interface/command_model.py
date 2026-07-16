from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class CommandStatus(str, Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    APPLIED = "Applied"
    EXPIRED = "Expired"
    FAILED = "Failed"


ALLOWED_COMMAND_TYPES = {
    "start",
    "pause",
    "stop",
    "set_flow",
    "declare_refill",
    "tare",
    "change_vessel",
    "maintenance",
}


@dataclass
class ColumnCommand:
    column_id: int
    command_type: str
    requested_by: str
    requested_value: float | str | bool | None = None
    ttl_s: int = 30
    command_id: str = field(default_factory=lambda: f"CMD-{uuid4().hex[:12].upper()}")
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sequence: int = 0
    status: CommandStatus = CommandStatus.PENDING
    result: str = ""
    applied_at: datetime | None = None

    @property
    def expires_at(self) -> datetime:
        return self.requested_at + timedelta(seconds=self.ttl_s)

    def as_mailbox_payload(self) -> dict[str, Any]:
        return {
            "CommandId": self.command_id,
            "ColumnId": self.column_id,
            "CommandType": self.command_type,
            "RequestedValue": self.requested_value,
            "RequestedBy": self.requested_by,
            "RequestedAt": self.requested_at.isoformat(),
            "ExpiresAt": self.expires_at.isoformat(),
            "Sequence": self.sequence,
            "Status": self.status.value,
            "Result": self.result,
            "AppliedAt": self.applied_at.isoformat() if self.applied_at else None,
        }


class CommandMailbox:
    def __init__(self) -> None:
        self._commands: dict[str, ColumnCommand] = {}
        self._last_sequence = 0
        self._idempotency: dict[str, str] = {}

    def submit(self, command: ColumnCommand, idempotency_key: str | None = None) -> ColumnCommand:
        self._validate(command)
        if idempotency_key and idempotency_key in self._idempotency:
            return self._commands[self._idempotency[idempotency_key]]
        self._last_sequence += 1
        command.sequence = self._last_sequence
        self._commands[command.command_id] = command
        if idempotency_key:
            self._idempotency[idempotency_key] = command.command_id
        return command

    def acknowledge_from_codesys(self, command_id: str, accepted: bool, result: str = "") -> ColumnCommand:
        command = self._commands[command_id]
        if command.status == CommandStatus.EXPIRED:
            return command
        command.status = CommandStatus.ACCEPTED if accepted else CommandStatus.REJECTED
        command.result = result
        return command

    def apply_from_codesys(self, command_id: str, result: str = "applied") -> ColumnCommand:
        command = self._commands[command_id]
        if command.status not in {CommandStatus.ACCEPTED, CommandStatus.PENDING}:
            return command
        command.status = CommandStatus.APPLIED
        command.result = result
        command.applied_at = datetime.now(timezone.utc)
        return command

    def expire(self, now: datetime | None = None) -> list[ColumnCommand]:
        now = now or datetime.now(timezone.utc)
        expired: list[ColumnCommand] = []
        for command in self._commands.values():
            if command.status == CommandStatus.PENDING and command.expires_at <= now:
                command.status = CommandStatus.EXPIRED
                command.result = "ttl_expired"
                expired.append(command)
        return expired

    def get(self, command_id: str) -> ColumnCommand:
        return self._commands[command_id]

    def _validate(self, command: ColumnCommand) -> None:
        if not 1 <= command.column_id <= 200:
            raise ValueError("column_id fuera de rango 1..200")
        if command.command_type not in ALLOWED_COMMAND_TYPES:
            raise ValueError(f"command_type no autorizado: {command.command_type}")
        if command.ttl_s <= 0 or command.ttl_s > 300:
            raise ValueError("ttl_s debe estar entre 1 y 300")
        if command.command_type == "set_flow":
            value = float(command.requested_value or 0)
            if value < 0 or value > 100:
                raise ValueError("set_flow fuera de rango 0..100")
