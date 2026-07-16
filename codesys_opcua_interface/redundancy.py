from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .command_model import ColumnCommand, CommandMailbox


class ControllerRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


@dataclass
class ControllerState:
    controller_id: str
    endpoint_url: str
    role: ControllerRole
    is_active: bool
    online: bool = True
    redundancy_healthy: bool = True
    heartbeat: int = 0
    application_version: str = "0.1.0-sim"
    control_authority: str = "codesys"


class RedundantCodesysSimulator:
    """Deterministic simulator for two CODESYS endpoints.

    It does not validate real CODESYS redundancy. It models the safety rule:
    only one active endpoint may accept commands.
    """

    def __init__(self, primary_url: str, secondary_url: str) -> None:
        self.primary = ControllerState("CODESYS-A", primary_url, ControllerRole.PRIMARY, True)
        self.secondary = ControllerState("CODESYS-B", secondary_url, ControllerRole.SECONDARY, False)
        self.mailbox = CommandMailbox()

    def active(self) -> ControllerState:
        for controller in [self.primary, self.secondary]:
            if controller.online and controller.is_active:
                return controller
        raise RuntimeError("sin controlador activo")

    def tick(self) -> None:
        for controller in [self.primary, self.secondary]:
            if controller.online:
                controller.heartbeat += 1
        self._enforce_single_active()

    def fail_primary(self) -> None:
        self.primary.online = False
        self.primary.is_active = False
        self.secondary.is_active = True
        self.secondary.redundancy_healthy = False

    def restore_primary_as_standby(self) -> None:
        self.primary.online = True
        self.primary.is_active = False
        self.secondary.is_active = True
        self.primary.redundancy_healthy = True
        self.secondary.redundancy_healthy = True

    def submit_command(self, command: ColumnCommand, idempotency_key: str | None = None) -> ColumnCommand:
        controller = self.active()
        if controller.control_authority != "codesys":
            raise RuntimeError("autoridad de control invalida")
        submitted = self.mailbox.submit(command, idempotency_key=idempotency_key)
        self.mailbox.acknowledge_from_codesys(submitted.command_id, accepted=True, result=f"accepted_by:{controller.controller_id}")
        self.mailbox.apply_from_codesys(submitted.command_id, result=f"applied_by:{controller.controller_id}")
        return submitted

    def status(self) -> dict[str, object]:
        return {
            "primary": self.primary.__dict__,
            "secondary": self.secondary.__dict__,
            "active_controller": self.active().controller_id,
            "double_write_prevented": not (self.primary.is_active and self.secondary.is_active),
        }

    def _enforce_single_active(self) -> None:
        if self.primary.is_active and self.secondary.is_active:
            self.secondary.is_active = False
            self.primary.redundancy_healthy = False
            self.secondary.redundancy_healthy = False
