from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import secrets
from typing import Any
from uuid import uuid4

from .command_model import ColumnCommand
from .opcua_connector import CodesysOpcuaConnector
from .opcua_simulator import SimulatedOpcuaEndpoint


PERMISSIONS_BY_ROLE: dict[str, set[str]] = {
    "admin": {"*"},
    "engineer": {
        "columns.read",
        "commands.request",
        "recipes.manage",
        "recipes.approve",
        "recipes.read",
        "campaigns.manage",
        "campaigns.read",
        "alarms.manage",
        "alarms.read",
        "users.read",
        "audit.read",
        "system.read",
    },
    "supervisor": {
        "columns.read",
        "commands.request",
        "recipes.read",
        "campaigns.manage",
        "alarms.ack",
        "audit.read",
        "system.read",
    },
    "operator": {
        "columns.read",
        "commands.request",
        "recipes.read",
        "campaigns.read",
        "alarms.ack",
        "system.read",
    },
    "maintenance": {
        "columns.read",
        "commands.request",
        "maintenance.manage",
        "devices.read",
        "system.read",
    },
    "viewer": {
        "columns.read",
        "recipes.read",
        "campaigns.read",
        "alarms.read",
        "system.read",
    },
}


@dataclass
class Role:
    id: str
    name: str
    permissions: set[str]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "permissions": sorted(self.permissions)}


@dataclass
class User:
    id: str
    username: str
    display_name: str
    role_id: str
    password_hash: str
    active: bool = True
    password_change_required: bool = True
    profile_photo_url: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def public_dict(self, role: Role) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": role.to_dict(),
            "active": self.active,
            "password_change_required": self.password_change_required,
            "profile_photo_url": self.profile_photo_url,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Column:
    id: int
    block_id: int
    state: str = "Available"
    flow_setpoint_kg_h: float = 12.0
    flow_measured_kg_h: float = 0.0
    pump_output_pct: float = 0.0
    input_weight_kg: float = 1000.0
    output_weight_kg: float = 0.0
    temperature_pv_c: float = 25.0
    data_quality: float = 1.0
    recipe_id: str | None = None
    campaign_id: str | None = None
    gateway_id: str = "gateway-demo"
    codesys_controller: str = "CODESYS-A"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Recipe:
    id: str
    name: str
    version: int
    status: str
    flow_setpoint_kg_h: float
    temperature_setpoint_c: float
    aeration_enabled: bool
    created_by: str
    approved_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Campaign:
    id: str
    name: str
    status: str
    recipe_id: str
    column_ids: list[int]
    created_by: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Alarm:
    id: str
    column_id: int
    severity: str
    code: str
    message: str
    active: bool = True
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["acknowledged_at"] = self.acknowledged_at.isoformat() if self.acknowledged_at else None
        return data


@dataclass
class AuditEvent:
    id: int
    username: str
    action: str
    target: str
    detail: dict[str, Any]
    event_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "action": self.action,
            "target": self.target,
            "detail": self.detail,
            "event_time": self.event_time.isoformat(),
        }


class PermissionDenied(PermissionError):
    pass


class NotFound(KeyError):
    pass


def hash_password(password: str, salt: str | None = None) -> str:
    salt_bytes = base64.urlsafe_b64decode(salt.encode()) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 120_000)
    return "pbkdf2_sha256$120000${salt}${digest}".format(
        salt=base64.urlsafe_b64encode(salt_bytes).decode(),
        digest=base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256" or iterations != "120000":
        return False
    calculated = hash_password(password, salt).split("$", 3)[3]
    return hmac.compare_digest(calculated, digest)


class TokenManager:
    def __init__(self, secret: str | None = None, ttl_minutes: int = 480) -> None:
        self.secret = (secret or secrets.token_urlsafe(32)).encode("utf-8")
        self.ttl_minutes = ttl_minutes

    def issue(self, username: str, role_id: str) -> str:
        payload = {
            "sub": username,
            "role": role_id,
            "exp": (datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)).timestamp(),
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")
        signature = hmac.new(self.secret, payload_b64.encode(), hashlib.sha256).digest()
        return f"{payload_b64}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"

    def verify(self, token: str) -> dict[str, Any]:
        try:
            payload_b64, signature_b64 = token.split(".", 1)
            expected = hmac.new(self.secret, payload_b64.encode(), hashlib.sha256).digest()
            provided = base64.urlsafe_b64decode(_pad_base64(signature_b64))
            if not hmac.compare_digest(expected, provided):
                raise PermissionDenied("token invalido")
            payload = json.loads(base64.urlsafe_b64decode(_pad_base64(payload_b64)))
        except Exception as exc:  # noqa: BLE001 - normalize token errors
            raise PermissionDenied("token invalido") from exc
        if float(payload.get("exp", 0)) < datetime.now(timezone.utc).timestamp():
            raise PermissionDenied("token expirado")
        return payload


def _pad_base64(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode()


class PlatformStore:
    def __init__(self) -> None:
        self.roles: dict[str, Role] = {}
        self.users: dict[str, User] = {}
        self.columns: dict[int, Column] = {}
        self.recipes: dict[str, Recipe] = {}
        self.campaigns: dict[str, Campaign] = {}
        self.alarms: dict[str, Alarm] = {}
        self.audit_events: list[AuditEvent] = []
        self.commands: dict[str, dict[str, Any]] = {}
        self.real_io_enabled = False
        self.demo_credentials: dict[str, str] = {}
        self._audit_sequence = 0

    def seed_demo(self, admin_password: str | None = None, operator_password: str | None = None) -> None:
        for role_id, permissions in PERMISSIONS_BY_ROLE.items():
            self.roles[role_id] = Role(role_id, _role_name(role_id), permissions)

        admin_password = admin_password or secrets.token_urlsafe(14)
        operator_password = operator_password or secrets.token_urlsafe(14)
        self.demo_credentials = {"admin": admin_password, "operador": operator_password}
        self.create_user("admin", "Administrador Demo", "admin", admin_password, password_change_required=True)
        self.create_user("operador", "Operador Demo", "operator", operator_password, password_change_required=True)

        for column_id in range(1, 201):
            block_id = ((column_id - 1) // 20) + 1
            self.columns[column_id] = Column(
                id=column_id,
                block_id=block_id,
                state="Running" if column_id <= 8 else "Available",
                flow_setpoint_kg_h=12.0 + (column_id % 5),
                flow_measured_kg_h=11.5 + (column_id % 7) * 0.2,
                pump_output_pct=45.0 + (column_id % 9),
                data_quality=0.97,
                recipe_id="REC-DEMO-001",
                campaign_id="CAM-DEMO-001" if column_id <= 20 else None,
            )
        self.columns[42].state = "Alarm"
        self.columns[42].data_quality = 0.2
        self.alarms["ALM-DEMO-042"] = Alarm(
            id="ALM-DEMO-042",
            column_id=42,
            severity="critical",
            code="SCALE_OFFLINE",
            message="Balanza de entrada sin comunicacion",
        )
        self.recipes["REC-DEMO-001"] = Recipe(
            id="REC-DEMO-001",
            name="Receta demo sulfato",
            version=1,
            status="approved",
            flow_setpoint_kg_h=12.0,
            temperature_setpoint_c=25.0,
            aeration_enabled=True,
            created_by="admin",
            approved_by="admin",
        )
        self.campaigns["CAM-DEMO-001"] = Campaign(
            id="CAM-DEMO-001",
            name="Campaña demo bloque 1",
            status="running",
            recipe_id="REC-DEMO-001",
            column_ids=list(range(1, 21)),
            created_by="admin",
        )

    def create_user(
        self,
        username: str,
        display_name: str,
        role_id: str,
        password: str,
        password_change_required: bool = True,
    ) -> User:
        if role_id not in self.roles:
            raise ValueError("rol inexistente")
        if username in self.users:
            raise ValueError("usuario ya existe")
        user = User(
            id=f"USR-{uuid4().hex[:10].upper()}",
            username=username,
            display_name=display_name,
            role_id=role_id,
            password_hash=hash_password(password),
            password_change_required=password_change_required,
        )
        self.users[username] = user
        self.audit("system", "users.create", username, {"role_id": role_id})
        return user

    def authenticate(self, username: str, password: str) -> User:
        user = self.users.get(username)
        if not user or not user.active or not verify_password(password, user.password_hash):
            raise PermissionDenied("credenciales invalidas")
        self.audit(username, "auth.login", username, {})
        return user

    def change_password(self, actor: User, username: str, new_password: str) -> None:
        if actor.username != username and not self.has_permission(actor, "users.manage"):
            raise PermissionDenied("sin permiso para cambiar contrasena de terceros")
        target = self.users.get(username)
        if not target:
            raise NotFound("usuario no existe")
        target.password_hash = hash_password(new_password)
        target.password_change_required = False
        self.audit(actor.username, "users.password.change", username, {"self": actor.username == username})

    def update_profile(self, actor: User, username: str, display_name: str | None = None, profile_photo_url: str | None = None) -> User:
        if actor.username != username and not self.has_permission(actor, "users.manage"):
            raise PermissionDenied("sin permiso para editar perfil de terceros")
        target = self.users.get(username)
        if not target:
            raise NotFound("usuario no existe")
        if display_name is not None:
            target.display_name = display_name
        if profile_photo_url is not None:
            target.profile_photo_url = profile_photo_url
        self.audit(actor.username, "users.profile.update", username, {"self": actor.username == username})
        return target

    def has_permission(self, user: User, permission: str) -> bool:
        role = self.roles[user.role_id]
        return "*" in role.permissions or permission in role.permissions

    def require_permission(self, user: User, permission: str) -> None:
        if not self.has_permission(user, permission):
            raise PermissionDenied(f"permiso requerido: {permission}")

    def summary(self) -> dict[str, Any]:
        states = {state: 0 for state in ["Running", "Paused", "Alarm", "Offline", "Available"]}
        for column in self.columns.values():
            states[column.state] = states.get(column.state, 0) + 1
        flow_total = round(sum(column.flow_measured_kg_h for column in self.columns.values()), 3)
        quality = round(sum(column.data_quality for column in self.columns.values()) / len(self.columns), 4)
        return {
            "columns_total": len(self.columns),
            "running": states.get("Running", 0),
            "paused": states.get("Paused", 0),
            "alarm": states.get("Alarm", 0),
            "offline": states.get("Offline", 0),
            "available": states.get("Available", 0),
            "active_campaigns": len([c for c in self.campaigns.values() if c.status == "running"]),
            "flow_total_kg_h": flow_total,
            "data_quality": quality,
            "real_io_enabled": self.real_io_enabled,
            "codesys": {
                "primary": {"controller_id": "CODESYS-A", "role": "primary", "active": True, "healthy": True},
                "secondary": {"controller_id": "CODESYS-B", "role": "secondary", "active": False, "healthy": True},
            },
            "gateways": [{"gateway_id": "gateway-demo", "online": True, "quality": 1.0}],
            "critical_alarms": len([a for a in self.alarms.values() if a.active and a.severity == "critical"]),
        }

    def get_column(self, column_id: int) -> Column:
        try:
            return self.columns[column_id]
        except KeyError as exc:
            raise NotFound("columna no existe") from exc

    def create_recipe(self, actor: User, payload: dict[str, Any]) -> Recipe:
        self.require_permission(actor, "recipes.manage")
        recipe_id = payload.get("id") or f"REC-{uuid4().hex[:8].upper()}"
        recipe = Recipe(
            id=recipe_id,
            name=str(payload["name"]),
            version=int(payload.get("version", 1)),
            status="draft",
            flow_setpoint_kg_h=float(payload["flow_setpoint_kg_h"]),
            temperature_setpoint_c=float(payload.get("temperature_setpoint_c", 25.0)),
            aeration_enabled=bool(payload.get("aeration_enabled", True)),
            created_by=actor.username,
        )
        self.recipes[recipe_id] = recipe
        self.audit(actor.username, "recipes.create", recipe_id, recipe.to_dict())
        return recipe

    def approve_recipe(self, actor: User, recipe_id: str) -> Recipe:
        self.require_permission(actor, "recipes.approve")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        recipe.status = "approved"
        recipe.approved_by = actor.username
        self.audit(actor.username, "recipes.approve", recipe_id, {})
        return recipe

    def create_campaign(self, actor: User, payload: dict[str, Any]) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        recipe_id = str(payload["recipe_id"])
        if recipe_id not in self.recipes or self.recipes[recipe_id].status != "approved":
            raise ValueError("receta debe existir y estar aprobada")
        column_ids = [int(item) for item in payload.get("column_ids", [])]
        if not column_ids or any(column_id not in self.columns for column_id in column_ids):
            raise ValueError("columnas invalidas")
        campaign_id = payload.get("id") or f"CAM-{uuid4().hex[:8].upper()}"
        campaign = Campaign(
            id=campaign_id,
            name=str(payload["name"]),
            status="planned",
            recipe_id=recipe_id,
            column_ids=column_ids,
            created_by=actor.username,
        )
        self.campaigns[campaign_id] = campaign
        self.audit(actor.username, "campaigns.create", campaign_id, campaign.to_dict())
        return campaign

    def start_campaign(self, actor: User, campaign_id: str) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise NotFound("campana no existe")
        campaign.status = "running"
        for column_id in campaign.column_ids:
            self.columns[column_id].campaign_id = campaign_id
            self.columns[column_id].recipe_id = campaign.recipe_id
        self.audit(actor.username, "campaigns.start", campaign_id, {"columns": campaign.column_ids})
        return campaign

    def record_command_result(self, actor: User, command: ColumnCommand) -> None:
        self.commands[command.command_id] = command.as_mailbox_payload()
        if command.status.value == "Applied":
            column = self.get_column(command.column_id)
            if command.command_type == "start":
                column.state = "Running"
            elif command.command_type == "pause":
                column.state = "Paused"
            elif command.command_type == "stop":
                column.state = "Available"
            elif command.command_type == "maintenance":
                column.state = "Maintenance"
            elif command.command_type == "set_flow":
                column.flow_setpoint_kg_h = float(command.requested_value or 0.0)
            column.codesys_controller = command.result.replace("applied_by:", "") if command.result.startswith("applied_by:") else "CODESYS-A"
        self.audit(actor.username, "commands.request", f"column:{command.column_id}", command.as_mailbox_payload())

    def acknowledge_alarm(self, actor: User, alarm_id: str) -> Alarm:
        self.require_permission(actor, "alarms.ack")
        alarm = self.alarms.get(alarm_id)
        if not alarm:
            raise NotFound("alarma no existe")
        alarm.acknowledged_by = actor.username
        alarm.acknowledged_at = datetime.now(timezone.utc)
        self.audit(actor.username, "alarms.ack", alarm_id, {})
        return alarm

    def audit(self, username: str, action: str, target: str, detail: dict[str, Any]) -> None:
        self._audit_sequence += 1
        self.audit_events.append(AuditEvent(self._audit_sequence, username, action, target, detail))


class PlatformService:
    def __init__(self, store: PlatformStore, connector: CodesysOpcuaConnector) -> None:
        self.store = store
        self.connector = connector

    async def request_command(
        self,
        actor: User,
        column_id: int,
        command_type: str,
        requested_value: float | str | bool | None = None,
        idempotency_key: str | None = None,
    ) -> ColumnCommand:
        self.store.require_permission(actor, "commands.request")
        command = ColumnCommand(
            column_id=column_id,
            command_type=command_type,
            requested_value=requested_value,
            requested_by=actor.username,
        )
        result = await self.connector.submit_command(command, idempotency_key=idempotency_key)
        self.store.record_command_result(actor, result)
        return result


def build_demo_connector() -> CodesysOpcuaConnector:
    primary = SimulatedOpcuaEndpoint("opc.tcp://codesys-a:4840", controller_id="CODESYS-A", is_active=True)
    secondary = SimulatedOpcuaEndpoint(
        "opc.tcp://codesys-b:4840",
        controller_id="CODESYS-B",
        controller_role="secondary",
        is_active=False,
    )
    return CodesysOpcuaConnector(primary, secondary)


def create_demo_store(admin_password: str | None = None, operator_password: str | None = None) -> PlatformStore:
    store = PlatformStore()
    store.seed_demo(admin_password=admin_password, operator_password=operator_password)
    return store


def _role_name(role_id: str) -> str:
    return {
        "admin": "Administrador",
        "engineer": "Ingeniero",
        "supervisor": "Supervisor",
        "operator": "Operador",
        "maintenance": "Mantenimiento",
        "viewer": "Visualizador",
    }[role_id]
