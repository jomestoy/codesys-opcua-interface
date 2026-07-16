from __future__ import annotations

import asyncio

import pytest

from codesys_opcua_interface.platform_store import (
    PermissionDenied,
    PlatformService,
    TokenManager,
    build_demo_connector,
    create_demo_store,
)


def test_demo_store_has_roles_users_and_200_columns():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")

    assert len(store.columns) == 200
    assert store.summary()["columns_total"] == 200
    assert store.summary()["real_io_enabled"] is False
    assert store.roles["admin"].permissions == {"*"}
    assert store.authenticate("admin", "AdminTemporal!2026").username == "admin"


def test_token_manager_rejects_tampered_tokens():
    manager = TokenManager(secret="test-secret")
    token = manager.issue("admin", "admin")

    assert manager.verify(token)["sub"] == "admin"
    with pytest.raises(PermissionDenied):
        manager.verify(token + "tampered")


def test_operator_cannot_create_recipe_but_admin_can_approve_it():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    admin = store.authenticate("admin", "AdminTemporal!2026")
    operator = store.authenticate("operador", "OperadorTemporal!2026")

    with pytest.raises(PermissionDenied):
        store.create_recipe(operator, {"name": "No autorizado", "flow_setpoint_kg_h": 10})

    recipe = store.create_recipe(admin, {"name": "Prueba", "flow_setpoint_kg_h": 13.5})
    approved = store.approve_recipe(admin, recipe.id)

    assert approved.status == "approved"
    assert approved.approved_by == "admin"


def test_command_request_goes_through_simulated_codesys_connector_and_audit():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    operator = store.authenticate("operador", "OperadorTemporal!2026")
    service = PlatformService(store, build_demo_connector())

    command = asyncio.run(service.request_command(operator, 10, "start"))

    assert command.status.value == "Applied"
    assert command.result == "applied_by:CODESYS-A"
    assert store.columns[10].state == "Running"
    assert any(event.action == "commands.request" for event in store.audit_events)


def test_campaign_lifecycle_assigns_columns():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    admin = store.authenticate("admin", "AdminTemporal!2026")
    recipe = store.create_recipe(admin, {"name": "Campaña test", "flow_setpoint_kg_h": 9.5})
    store.approve_recipe(admin, recipe.id)

    campaign = store.create_campaign(
        admin,
        {"name": "Test bloque 2", "recipe_id": recipe.id, "column_ids": list(range(21, 41))},
    )
    running = store.start_campaign(admin, campaign.id)

    assert running.status == "running"
    assert store.columns[21].campaign_id == campaign.id
    assert store.columns[21].recipe_id == recipe.id
