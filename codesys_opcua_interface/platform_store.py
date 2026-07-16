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
        "recipes.assign",
        "campaigns.manage",
        "campaigns.read",
        "alarms.manage",
        "alarms.read",
        "alarms.ack",
        "alarms.config",
        "users.read",
        "audit.read",
        "system.read",
    },
    "supervisor": {
        "columns.read",
        "commands.request",
        "recipes.read",
        "campaigns.manage",
        "campaigns.read",
        "recipes.assign",
        "alarms.read",
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
    base_recipe_id: str | None = None
    change_note: str = ""
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejected_by: str | None = None
    rejected_reason: str = ""
    obsoleted_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["approved_at"] = self.approved_at.isoformat() if self.approved_at else None
        return data


@dataclass
class Campaign:
    id: str
    name: str
    status: str
    recipe_id: str
    column_ids: list[int]
    created_by: str
    scheduled_start: datetime | None = None
    started_at: datetime | None = None
    paused_at: datetime | None = None
    finished_at: datetime | None = None
    cancelled_at: datetime | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ["scheduled_start", "started_at", "paused_at", "finished_at", "cancelled_at"]:
            data[key] = getattr(self, key).isoformat() if getattr(self, key) else None
        return data


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
    comment: str = ""
    source: str = "application"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cleared_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["acknowledged_at"] = self.acknowledged_at.isoformat() if self.acknowledged_at else None
        data["created_at"] = self.created_at.isoformat()
        data["cleared_at"] = self.cleared_at.isoformat() if self.cleared_at else None
        return data


@dataclass
class AlarmRule:
    id: str
    name: str
    variable: str
    operator: str
    threshold: float
    hysteresis: float
    delay_s: int
    priority: str
    action: str
    target_scope: str
    column_ids: list[int]
    enabled: bool
    version: int
    created_by: str
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["updated_at"] = self.updated_at.isoformat()
        return data


@dataclass
class AlarmHistoryEntry:
    id: int
    alarm_id: str
    username: str
    action: str
    comment: str
    event_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "alarm_id": self.alarm_id,
            "username": self.username,
            "action": self.action,
            "comment": self.comment,
            "event_time": self.event_time.isoformat(),
        }


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
        self.alarm_rules: dict[str, AlarmRule] = {}
        self.alarm_history: list[AlarmHistoryEntry] = []
        self.audit_events: list[AuditEvent] = []
        self.commands: dict[str, dict[str, Any]] = {}
        self.real_io_enabled = False
        self.demo_credentials: dict[str, str] = {}
        self._audit_sequence = 0
        self._alarm_history_sequence = 0

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
            source="codesys-sim",
        )
        self._record_alarm_history("ALM-DEMO-042", "system", "created", "alarma demo inicial")
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
            approved_at=datetime.now(timezone.utc),
        )
        self.campaigns["CAM-DEMO-001"] = Campaign(
            id="CAM-DEMO-001",
            name="Campaña demo bloque 1",
            status="running",
            recipe_id="REC-DEMO-001",
            column_ids=list(range(1, 21)),
            created_by="admin",
            started_at=datetime.now(timezone.utc),
        )
        self.alarm_rules["AR-DEMO-FLOW"] = AlarmRule(
            id="AR-DEMO-FLOW",
            name="Flujo bajo demo",
            variable="flow_measured_kg_h",
            operator="lt",
            threshold=8.0,
            hysteresis=0.5,
            delay_s=30,
            priority="warning",
            action="notify",
            target_scope="all",
            column_ids=[],
            enabled=True,
            version=1,
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
        name = str(payload["name"])
        version = int(payload.get("version") or self._next_recipe_version(name))
        recipe = Recipe(
            id=recipe_id,
            name=name,
            version=version,
            status="draft",
            flow_setpoint_kg_h=float(payload["flow_setpoint_kg_h"]),
            temperature_setpoint_c=float(payload.get("temperature_setpoint_c", 25.0)),
            aeration_enabled=bool(payload.get("aeration_enabled", True)),
            created_by=actor.username,
            base_recipe_id=payload.get("base_recipe_id"),
            change_note=str(payload.get("change_note", "")),
        )
        self.recipes[recipe_id] = recipe
        self.audit(actor.username, "recipes.create", recipe_id, recipe.to_dict())
        return recipe

    def update_recipe(self, actor: User, recipe_id: str, payload: dict[str, Any]) -> Recipe:
        self.require_permission(actor, "recipes.manage")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        if recipe.status not in {"draft", "rejected"}:
            raise ValueError("solo se pueden editar recetas draft o rejected")
        if "name" in payload and payload["name"] is not None:
            recipe.name = str(payload["name"])
        if "flow_setpoint_kg_h" in payload and payload["flow_setpoint_kg_h"] is not None:
            recipe.flow_setpoint_kg_h = float(payload["flow_setpoint_kg_h"])
        if "temperature_setpoint_c" in payload and payload["temperature_setpoint_c"] is not None:
            recipe.temperature_setpoint_c = float(payload["temperature_setpoint_c"])
        if "aeration_enabled" in payload and payload["aeration_enabled"] is not None:
            recipe.aeration_enabled = bool(payload["aeration_enabled"])
        if "change_note" in payload and payload["change_note"] is not None:
            recipe.change_note = str(payload["change_note"])
        recipe.status = "draft"
        recipe.rejected_by = None
        recipe.rejected_reason = ""
        self.audit(actor.username, "recipes.update", recipe_id, payload)
        return recipe

    def clone_recipe(self, actor: User, recipe_id: str, payload: dict[str, Any] | None = None) -> Recipe:
        self.require_permission(actor, "recipes.manage")
        payload = payload or {}
        source = self.recipes.get(recipe_id)
        if not source:
            raise NotFound("receta no existe")
        return self.create_recipe(
            actor,
            {
                "name": payload.get("name") or source.name,
                "flow_setpoint_kg_h": payload.get("flow_setpoint_kg_h", source.flow_setpoint_kg_h),
                "temperature_setpoint_c": payload.get("temperature_setpoint_c", source.temperature_setpoint_c),
                "aeration_enabled": payload.get("aeration_enabled", source.aeration_enabled),
                "base_recipe_id": source.id,
                "change_note": payload.get("change_note", f"clonada desde {source.id}"),
            },
        )

    def approve_recipe(self, actor: User, recipe_id: str) -> Recipe:
        self.require_permission(actor, "recipes.approve")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        if recipe.status == "obsolete":
            raise ValueError("receta obsoleta no puede aprobarse")
        recipe.status = "approved"
        recipe.approved_by = actor.username
        recipe.approved_at = datetime.now(timezone.utc)
        self.audit(actor.username, "recipes.approve", recipe_id, {})
        return recipe

    def reject_recipe(self, actor: User, recipe_id: str, reason: str) -> Recipe:
        self.require_permission(actor, "recipes.approve")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        if recipe.status == "obsolete":
            raise ValueError("receta obsoleta no puede rechazarse")
        recipe.status = "rejected"
        recipe.rejected_by = actor.username
        recipe.rejected_reason = reason
        self.audit(actor.username, "recipes.reject", recipe_id, {"reason": reason})
        return recipe

    def obsolete_recipe(self, actor: User, recipe_id: str) -> Recipe:
        self.require_permission(actor, "recipes.approve")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        recipe.status = "obsolete"
        recipe.obsoleted_by = actor.username
        self.audit(actor.username, "recipes.obsolete", recipe_id, {})
        return recipe

    def compare_recipes(self, actor: User, left_id: str, right_id: str) -> dict[str, Any]:
        self.require_permission(actor, "recipes.read")
        left = self.recipes.get(left_id)
        right = self.recipes.get(right_id)
        if not left or not right:
            raise NotFound("receta no existe")
        fields = ["name", "version", "status", "flow_setpoint_kg_h", "temperature_setpoint_c", "aeration_enabled"]
        return {
            "left": left.to_dict(),
            "right": right.to_dict(),
            "differences": {
                field_name: {"left": getattr(left, field_name), "right": getattr(right, field_name)}
                for field_name in fields
                if getattr(left, field_name) != getattr(right, field_name)
            },
        }

    def assign_recipe(self, actor: User, recipe_id: str, column_ids: list[int]) -> dict[str, Any]:
        self.require_permission(actor, "recipes.assign")
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            raise NotFound("receta no existe")
        if recipe.status != "approved":
            raise ValueError("solo se pueden asignar recetas aprobadas")
        self._validate_columns(column_ids)
        for column_id in column_ids:
            self.columns[column_id].recipe_id = recipe_id
            self.columns[column_id].flow_setpoint_kg_h = recipe.flow_setpoint_kg_h
        detail = {"recipe_id": recipe_id, "column_ids": column_ids}
        self.audit(actor.username, "recipes.assign", recipe_id, detail)
        return detail

    def create_campaign(self, actor: User, payload: dict[str, Any]) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        recipe_id = str(payload["recipe_id"])
        if recipe_id not in self.recipes or self.recipes[recipe_id].status != "approved":
            raise ValueError("receta debe existir y estar aprobada")
        column_ids = [int(item) for item in payload.get("column_ids", [])]
        self._validate_columns(column_ids)
        campaign_id = payload.get("id") or f"CAM-{uuid4().hex[:8].upper()}"
        campaign = Campaign(
            id=campaign_id,
            name=str(payload["name"]),
            status="planned",
            recipe_id=recipe_id,
            column_ids=column_ids,
            created_by=actor.username,
            scheduled_start=_parse_datetime(payload.get("scheduled_start")),
            notes=str(payload.get("notes", "")),
        )
        self.campaigns[campaign_id] = campaign
        self.audit(actor.username, "campaigns.create", campaign_id, campaign.to_dict())
        return campaign

    def schedule_campaign(self, actor: User, campaign_id: str, scheduled_start: str | None) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self._get_campaign(campaign_id)
        if campaign.status in {"finished", "cancelled"}:
            raise ValueError("campana cerrada no puede programarse")
        campaign.scheduled_start = _parse_datetime(scheduled_start)
        campaign.status = "scheduled"
        self.audit(actor.username, "campaigns.schedule", campaign_id, {"scheduled_start": scheduled_start})
        return campaign

    def start_campaign(self, actor: User, campaign_id: str) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self._get_campaign(campaign_id)
        if campaign.status in {"finished", "cancelled"}:
            raise ValueError("campana cerrada no puede iniciarse")
        campaign.status = "running"
        campaign.started_at = datetime.now(timezone.utc)
        for column_id in campaign.column_ids:
            self.columns[column_id].campaign_id = campaign_id
            self.columns[column_id].recipe_id = campaign.recipe_id
        self.audit(actor.username, "campaigns.start", campaign_id, {"columns": campaign.column_ids})
        return campaign

    def pause_campaign(self, actor: User, campaign_id: str) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self._get_campaign(campaign_id)
        if campaign.status != "running":
            raise ValueError("solo se puede pausar una campana running")
        campaign.status = "paused"
        campaign.paused_at = datetime.now(timezone.utc)
        for column_id in campaign.column_ids:
            if self.columns[column_id].state == "Running":
                self.columns[column_id].state = "Paused"
        self.audit(actor.username, "campaigns.pause", campaign_id, {})
        return campaign

    def finalize_campaign(self, actor: User, campaign_id: str) -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self._get_campaign(campaign_id)
        if campaign.status not in {"running", "paused", "scheduled", "planned"}:
            raise ValueError("campana no puede finalizarse desde su estado actual")
        campaign.status = "finished"
        campaign.finished_at = datetime.now(timezone.utc)
        for column_id in campaign.column_ids:
            self.columns[column_id].campaign_id = None
        self.audit(actor.username, "campaigns.finish", campaign_id, {})
        return campaign

    def cancel_campaign(self, actor: User, campaign_id: str, reason: str = "") -> Campaign:
        self.require_permission(actor, "campaigns.manage")
        campaign = self._get_campaign(campaign_id)
        if campaign.status == "finished":
            raise ValueError("campana finalizada no puede cancelarse")
        campaign.status = "cancelled"
        campaign.cancelled_at = datetime.now(timezone.utc)
        campaign.notes = reason or campaign.notes
        for column_id in campaign.column_ids:
            self.columns[column_id].campaign_id = None
        self.audit(actor.username, "campaigns.cancel", campaign_id, {"reason": reason})
        return campaign

    def compare_campaigns(self, actor: User, left_id: str, right_id: str) -> dict[str, Any]:
        self.require_permission(actor, "campaigns.read")
        left = self._get_campaign(left_id)
        right = self._get_campaign(right_id)
        return {
            "left": left.to_dict(),
            "right": right.to_dict(),
            "differences": {
                "status": {"left": left.status, "right": right.status} if left.status != right.status else None,
                "recipe_id": {"left": left.recipe_id, "right": right.recipe_id} if left.recipe_id != right.recipe_id else None,
                "column_count": {"left": len(left.column_ids), "right": len(right.column_ids)}
                if len(left.column_ids) != len(right.column_ids) else None,
                "columns_only_left": sorted(set(left.column_ids) - set(right.column_ids)),
                "columns_only_right": sorted(set(right.column_ids) - set(left.column_ids)),
            },
        }

    def export_campaign(self, actor: User, campaign_id: str) -> dict[str, Any]:
        self.require_permission(actor, "campaigns.read")
        campaign = self._get_campaign(campaign_id)
        columns = [self.columns[column_id].to_dict() for column_id in campaign.column_ids]
        total_flow = round(sum(column["flow_measured_kg_h"] for column in columns), 3)
        export = {
            "campaign": campaign.to_dict(),
            "recipe": self.recipes[campaign.recipe_id].to_dict(),
            "columns": columns,
            "summary": {"column_count": len(columns), "flow_total_kg_h": total_flow},
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
        self.audit(actor.username, "campaigns.export", campaign_id, {"column_count": len(columns)})
        return export

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

    def create_alarm_rule(self, actor: User, payload: dict[str, Any]) -> AlarmRule:
        self.require_permission(actor, "alarms.config")
        rule_id = payload.get("id") or f"AR-{uuid4().hex[:8].upper()}"
        column_ids = [int(item) for item in payload.get("column_ids", [])]
        target_scope = str(payload.get("target_scope", "all"))
        if target_scope == "columns":
            self._validate_columns(column_ids)
        rule = AlarmRule(
            id=rule_id,
            name=str(payload["name"]),
            variable=str(payload["variable"]),
            operator=str(payload.get("operator", "gt")),
            threshold=float(payload["threshold"]),
            hysteresis=float(payload.get("hysteresis", 0.0)),
            delay_s=int(payload.get("delay_s", 0)),
            priority=str(payload.get("priority", "warning")),
            action=str(payload.get("action", "notify")),
            target_scope=target_scope,
            column_ids=column_ids,
            enabled=bool(payload.get("enabled", True)),
            version=1,
            created_by=actor.username,
        )
        self.alarm_rules[rule_id] = rule
        self.audit(actor.username, "alarm_rules.create", rule_id, rule.to_dict())
        return rule

    def update_alarm_rule(self, actor: User, rule_id: str, payload: dict[str, Any]) -> AlarmRule:
        self.require_permission(actor, "alarms.config")
        rule = self.alarm_rules.get(rule_id)
        if not rule:
            raise NotFound("regla de alarma no existe")
        for field_name in ["name", "variable", "operator", "priority", "action", "target_scope"]:
            if field_name in payload and payload[field_name] is not None:
                setattr(rule, field_name, str(payload[field_name]))
        for field_name in ["threshold", "hysteresis"]:
            if field_name in payload and payload[field_name] is not None:
                setattr(rule, field_name, float(payload[field_name]))
        if "delay_s" in payload and payload["delay_s"] is not None:
            rule.delay_s = int(payload["delay_s"])
        if "enabled" in payload and payload["enabled"] is not None:
            rule.enabled = bool(payload["enabled"])
        if "column_ids" in payload and payload["column_ids"] is not None:
            column_ids = [int(item) for item in payload["column_ids"]]
            if rule.target_scope == "columns":
                self._validate_columns(column_ids)
            rule.column_ids = column_ids
        rule.version += 1
        rule.updated_at = datetime.now(timezone.utc)
        self.audit(actor.username, "alarm_rules.update", rule_id, rule.to_dict())
        return rule

    def evaluate_alarm_rules(self, actor: User) -> list[Alarm]:
        self.require_permission(actor, "alarms.manage")
        triggered: list[Alarm] = []
        for rule in self.alarm_rules.values():
            if not rule.enabled:
                continue
            for column in self._columns_for_alarm_rule(rule):
                value = getattr(column, rule.variable, None)
                if value is None:
                    continue
                if _matches_rule(float(value), rule.operator, rule.threshold):
                    alarm_id = f"ALM-{rule.id}-{column.id:03}"
                    existing = self.alarms.get(alarm_id)
                    if existing and existing.active:
                        continue
                    alarm = Alarm(
                        id=alarm_id,
                        column_id=column.id,
                        severity=rule.priority,
                        code=rule.id,
                        message=f"{rule.name}: {rule.variable}={value} {rule.operator} {rule.threshold}",
                        source="alarm-rule",
                    )
                    self.alarms[alarm_id] = alarm
                    self._record_alarm_history(alarm_id, actor.username, "created", rule.action)
                    triggered.append(alarm)
        self.audit(actor.username, "alarm_rules.evaluate", "all", {"triggered": [alarm.id for alarm in triggered]})
        return triggered

    def acknowledge_alarm(self, actor: User, alarm_id: str, comment: str = "") -> Alarm:
        self.require_permission(actor, "alarms.ack")
        alarm = self.alarms.get(alarm_id)
        if not alarm:
            raise NotFound("alarma no existe")
        alarm.acknowledged_by = actor.username
        alarm.acknowledged_at = datetime.now(timezone.utc)
        alarm.comment = comment
        self._record_alarm_history(alarm_id, actor.username, "ack", comment)
        self.audit(actor.username, "alarms.ack", alarm_id, {"comment": comment})
        return alarm

    def clear_alarm(self, actor: User, alarm_id: str, comment: str = "") -> Alarm:
        self.require_permission(actor, "alarms.manage")
        alarm = self.alarms.get(alarm_id)
        if not alarm:
            raise NotFound("alarma no existe")
        alarm.active = False
        alarm.cleared_at = datetime.now(timezone.utc)
        if comment:
            alarm.comment = comment
        self._record_alarm_history(alarm_id, actor.username, "clear", comment)
        self.audit(actor.username, "alarms.clear", alarm_id, {"comment": comment})
        return alarm

    def export_alarms(self, actor: User, active: bool | None = None) -> dict[str, Any]:
        self.require_permission(actor, "alarms.read")
        alarms = list(self.alarms.values())
        if active is not None:
            alarms = [alarm for alarm in alarms if alarm.active is active]
        export = {
            "alarms": [alarm.to_dict() for alarm in alarms],
            "history": [entry.to_dict() for entry in self.alarm_history],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
        self.audit(actor.username, "alarms.export", "alarms", {"count": len(alarms)})
        return export

    def audit(self, username: str, action: str, target: str, detail: dict[str, Any]) -> None:
        self._audit_sequence += 1
        self.audit_events.append(AuditEvent(self._audit_sequence, username, action, target, detail))

    def _next_recipe_version(self, name: str) -> int:
        versions = [recipe.version for recipe in self.recipes.values() if recipe.name == name]
        return max(versions, default=0) + 1

    def _validate_columns(self, column_ids: list[int]) -> None:
        if not column_ids:
            raise ValueError("debe indicar al menos una columna")
        if any(column_id not in self.columns for column_id in column_ids):
            raise ValueError("columnas invalidas")

    def _get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise NotFound("campana no existe")
        return campaign

    def _columns_for_alarm_rule(self, rule: AlarmRule) -> list[Column]:
        if rule.target_scope == "all":
            return list(self.columns.values())
        if rule.target_scope == "columns":
            return [self.columns[column_id] for column_id in rule.column_ids if column_id in self.columns]
        if rule.target_scope.startswith("block:"):
            block_id = int(rule.target_scope.split(":", 1)[1])
            return [column for column in self.columns.values() if column.block_id == block_id]
        return []

    def _record_alarm_history(self, alarm_id: str, username: str, action: str, comment: str) -> None:
        self._alarm_history_sequence += 1
        self.alarm_history.append(AlarmHistoryEntry(self._alarm_history_sequence, alarm_id, username, action, comment))


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


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _matches_rule(value: float, operator: str, threshold: float) -> bool:
    if operator == "gt":
        return value > threshold
    if operator == "gte":
        return value >= threshold
    if operator == "lt":
        return value < threshold
    if operator == "lte":
        return value <= threshold
    if operator == "eq":
        return value == threshold
    raise ValueError(f"operador de alarma no soportado: {operator}")
