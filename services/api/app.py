from __future__ import annotations

from typing import Any
import asyncio
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from codesys_opcua_interface.platform_store import (
    NotFound,
    PermissionDenied,
    PlatformService,
    PlatformStore,
    TokenManager,
    build_demo_connector,
    create_demo_store,
)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    username: str | None = None
    new_password: str = Field(min_length=10)


class CommandRequest(BaseModel):
    column_id: int = Field(ge=1, le=200)
    command_type: str
    requested_value: float | str | bool | None = None
    idempotency_key: str | None = None


class RecipeRequest(BaseModel):
    name: str
    flow_setpoint_kg_h: float = Field(ge=0, le=100)
    temperature_setpoint_c: float = Field(default=25.0, ge=0, le=90)
    aeration_enabled: bool = True
    change_note: str = ""


class RecipeUpdateRequest(BaseModel):
    name: str | None = None
    flow_setpoint_kg_h: float | None = Field(default=None, ge=0, le=100)
    temperature_setpoint_c: float | None = Field(default=None, ge=0, le=90)
    aeration_enabled: bool | None = None
    change_note: str | None = None


class RecipeCloneRequest(BaseModel):
    name: str | None = None
    change_note: str = ""


class RejectRequest(BaseModel):
    reason: str


class AssignRecipeRequest(BaseModel):
    column_ids: list[int]


class CampaignRequest(BaseModel):
    name: str
    recipe_id: str
    column_ids: list[int]
    scheduled_start: str | None = None
    notes: str = ""


class CampaignScheduleRequest(BaseModel):
    scheduled_start: str | None = None


class CampaignCancelRequest(BaseModel):
    reason: str = ""


class AlarmRuleRequest(BaseModel):
    name: str
    variable: str
    operator: str = "gt"
    threshold: float
    hysteresis: float = 0.0
    delay_s: int = 0
    priority: str = "warning"
    action: str = "notify"
    target_scope: str = "all"
    column_ids: list[int] = []
    enabled: bool = True


class AlarmRuleUpdateRequest(BaseModel):
    name: str | None = None
    variable: str | None = None
    operator: str | None = None
    threshold: float | None = None
    hysteresis: float | None = None
    delay_s: int | None = None
    priority: str | None = None
    action: str | None = None
    target_scope: str | None = None
    column_ids: list[int] | None = None
    enabled: bool | None = None


class AlarmActionRequest(BaseModel):
    comment: str = ""


class UserCreateRequest(BaseModel):
    username: str
    display_name: str
    role_id: str
    temporary_password: str = Field(min_length=10)


class UserProfileRequest(BaseModel):
    display_name: str | None = None
    profile_photo_url: str | None = None


def create_app(
    store: PlatformStore | None = None,
    token_manager: TokenManager | None = None,
    service: PlatformService | None = None,
) -> FastAPI:
    store = store or create_demo_store(
        admin_password=os.getenv("DEMO_ADMIN_PASSWORD"),
        operator_password=os.getenv("DEMO_OPERATOR_PASSWORD"),
    )
    token_manager = token_manager or TokenManager(secret=os.getenv("API_TOKEN_SECRET"))
    service = service or PlatformService(store, build_demo_connector())

    app = FastAPI(title="CODESYS OPC UA Platform API", version="0.5.0-hito5")
    app.state.store = store
    app.state.token_manager = token_manager
    app.state.service = service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://localhost:8080").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(PermissionDenied)
    async def permission_handler(_: Request, exc: PermissionDenied) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})

    @app.exception_handler(NotFound)
    async def not_found_handler(_: Request, exc: NotFound) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

    def current_user(authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token requerido")
        try:
            payload = token_manager.verify(authorization.removeprefix("Bearer ").strip())
            user = store.users[payload["sub"]]
            return user
        except PermissionDenied as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "usuario no existe") from exc

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": "demo" if not store.real_io_enabled else "real_io",
            "real_io_enabled": store.real_io_enabled,
            "columns": len(store.columns),
        }

    @app.get("/auth/demo-credentials")
    def demo_credentials() -> dict[str, str]:
        if os.getenv("DEMO_MODE", "true").lower() != "true":
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no disponible")
        return store.demo_credentials

    @app.post("/auth/login")
    def login(request: LoginRequest) -> dict[str, Any]:
        try:
            user = store.authenticate(request.username, request.password)
        except PermissionDenied as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
        role = store.roles[user.role_id]
        return {
            "access_token": token_manager.issue(user.username, user.role_id),
            "token_type": "bearer",
            "user": user.public_dict(role),
        }

    @app.get("/auth/me")
    def me(user=Depends(current_user)) -> dict[str, Any]:
        return user.public_dict(store.roles[user.role_id])

    @app.post("/auth/change-password")
    def change_password(request: ChangePasswordRequest, user=Depends(current_user)) -> dict[str, Any]:
        target = request.username or user.username
        try:
            store.change_password(user, target, request.new_password)
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)
        return {"status": "changed", "username": target}

    @app.get("/users")
    def users(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "users.read")
        return [item.public_dict(store.roles[item.role_id]) for item in store.users.values()]

    @app.post("/users")
    def create_user(request: UserCreateRequest, user=Depends(current_user)) -> dict[str, Any]:
        store.require_permission(user, "users.manage")
        try:
            created = store.create_user(
                request.username,
                request.display_name,
                request.role_id,
                request.temporary_password,
                password_change_required=True,
            )
            return created.public_dict(store.roles[created.role_id])
        except ValueError as exc:
            raise _http_error(exc)

    @app.patch("/users/{username}/profile")
    def update_profile(username: str, request: UserProfileRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            updated = store.update_profile(user, username, request.display_name, request.profile_photo_url)
            return updated.public_dict(store.roles[updated.role_id])
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.get("/system/summary")
    def summary(user=Depends(current_user)) -> dict[str, Any]:
        store.require_permission(user, "system.read")
        return store.summary()

    @app.websocket("/ws/summary")
    async def summary_socket(websocket: WebSocket) -> None:
        token = websocket.query_params.get("token", "")
        try:
            payload = token_manager.verify(token)
            user = store.users[payload["sub"]]
            store.require_permission(user, "system.read")
        except Exception:  # noqa: BLE001 - websocket auth closes instead of leaking details
            await websocket.close(code=1008)
            return

        await websocket.accept()
        try:
            while True:
                await websocket.send_json(store.summary())
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            return

    @app.get("/columns")
    def columns(block_id: int | None = None, state: str | None = None, user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "columns.read")
        items = list(store.columns.values())
        if block_id is not None:
            items = [item for item in items if item.block_id == block_id]
        if state:
            items = [item for item in items if item.state == state]
        return [item.to_dict() for item in items]

    @app.get("/columns/{column_id}")
    def column_detail(column_id: int, user=Depends(current_user)) -> dict[str, Any]:
        store.require_permission(user, "columns.read")
        try:
            return store.get_column(column_id).to_dict()
        except NotFound as exc:
            raise _http_error(exc)

    @app.post("/commands")
    async def request_command(request: CommandRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            command = await service.request_command(
                user,
                request.column_id,
                request.command_type,
                request.requested_value,
                request.idempotency_key,
            )
            return command.as_mailbox_payload()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.get("/commands")
    def commands(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "commands.request")
        return list(store.commands.values())

    @app.get("/recipes")
    def recipes(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "recipes.read")
        return [item.to_dict() for item in store.recipes.values()]

    @app.post("/recipes")
    def create_recipe(request: RecipeRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.create_recipe(user, _model_dump(request)).to_dict()
        except (PermissionDenied, ValueError) as exc:
            raise _http_error(exc)

    @app.get("/recipes/compare")
    def compare_recipes(left_id: str, right_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.compare_recipes(user, left_id, right_id)
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.get("/recipes/{recipe_id}")
    def recipe_detail(recipe_id: str, user=Depends(current_user)) -> dict[str, Any]:
        store.require_permission(user, "recipes.read")
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "receta no existe")
        return recipe.to_dict()

    @app.patch("/recipes/{recipe_id}")
    def update_recipe(recipe_id: str, request: RecipeUpdateRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.update_recipe(user, recipe_id, _model_dump(request)).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/recipes/{recipe_id}/clone")
    def clone_recipe(recipe_id: str, request: RecipeCloneRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.clone_recipe(user, recipe_id, _model_dump(request)).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/recipes/{recipe_id}/approve")
    def approve_recipe(recipe_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.approve_recipe(user, recipe_id).to_dict()
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.post("/recipes/{recipe_id}/reject")
    def reject_recipe(recipe_id: str, request: RejectRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.reject_recipe(user, recipe_id, request.reason).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/recipes/{recipe_id}/obsolete")
    def obsolete_recipe(recipe_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.obsolete_recipe(user, recipe_id).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/recipes/{recipe_id}/assign")
    def assign_recipe(recipe_id: str, request: AssignRecipeRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.assign_recipe(user, recipe_id, request.column_ids)
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.get("/campaigns")
    def campaigns(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "campaigns.read")
        return [item.to_dict() for item in store.campaigns.values()]

    @app.post("/campaigns")
    def create_campaign(request: CampaignRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.create_campaign(user, _model_dump(request)).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.get("/campaigns/compare")
    def compare_campaigns(left_id: str, right_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.compare_campaigns(user, left_id, right_id)
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.get("/campaigns/{campaign_id}/export")
    def export_campaign(campaign_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.export_campaign(user, campaign_id)
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.post("/campaigns/{campaign_id}/schedule")
    def schedule_campaign(campaign_id: str, request: CampaignScheduleRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.schedule_campaign(user, campaign_id, request.scheduled_start).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/campaigns/{campaign_id}/start")
    def start_campaign(campaign_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.start_campaign(user, campaign_id).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/campaigns/{campaign_id}/pause")
    def pause_campaign(campaign_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.pause_campaign(user, campaign_id).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/campaigns/{campaign_id}/finish")
    def finish_campaign(campaign_id: str, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.finalize_campaign(user, campaign_id).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/campaigns/{campaign_id}/cancel")
    def cancel_campaign(campaign_id: str, request: CampaignCancelRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.cancel_campaign(user, campaign_id, request.reason).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.get("/alarms")
    def alarms(active: bool | None = None, user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "alarms.read")
        items = list(store.alarms.values())
        if active is not None:
            items = [item for item in items if item.active is active]
        return [item.to_dict() for item in items]

    @app.get("/alarms/export")
    def export_alarms(active: bool | None = None, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.export_alarms(user, active)
        except PermissionDenied as exc:
            raise _http_error(exc)

    @app.get("/alarm-history")
    def alarm_history(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "alarms.read")
        return [item.to_dict() for item in store.alarm_history]

    @app.get("/alarm-rules")
    def alarm_rules(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "alarms.read")
        return [item.to_dict() for item in store.alarm_rules.values()]

    @app.post("/alarm-rules")
    def create_alarm_rule(request: AlarmRuleRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.create_alarm_rule(user, _model_dump(request)).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.patch("/alarm-rules/{rule_id}")
    def update_alarm_rule(rule_id: str, request: AlarmRuleUpdateRequest, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.update_alarm_rule(user, rule_id, _model_dump(request)).to_dict()
        except (PermissionDenied, NotFound, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/alarm-rules/evaluate")
    def evaluate_alarm_rules(user=Depends(current_user)) -> list[dict[str, Any]]:
        try:
            return [alarm.to_dict() for alarm in store.evaluate_alarm_rules(user)]
        except (PermissionDenied, ValueError) as exc:
            raise _http_error(exc)

    @app.post("/alarms/{alarm_id}/ack")
    def acknowledge_alarm(alarm_id: str, request: AlarmActionRequest | None = None, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.acknowledge_alarm(user, alarm_id, request.comment if request else "").to_dict()
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.post("/alarms/{alarm_id}/clear")
    def clear_alarm(alarm_id: str, request: AlarmActionRequest | None = None, user=Depends(current_user)) -> dict[str, Any]:
        try:
            return store.clear_alarm(user, alarm_id, request.comment if request else "").to_dict()
        except (PermissionDenied, NotFound) as exc:
            raise _http_error(exc)

    @app.get("/audit")
    def audit(user=Depends(current_user)) -> list[dict[str, Any]]:
        store.require_permission(user, "audit.read")
        return [item.to_dict() for item in store.audit_events[-200:]]

    return app


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PermissionDenied):
        return HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    if isinstance(exc, NotFound):
        return HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


def _model_dump(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


app = create_app()
