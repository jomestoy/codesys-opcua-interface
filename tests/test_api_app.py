from __future__ import annotations

from fastapi.testclient import TestClient

from codesys_opcua_interface.platform_store import PlatformService, TokenManager, build_demo_connector, create_demo_store
from services.api.app import create_app


def test_api_login_summary_columns_and_command_flow():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    app = create_app(
        store=store,
        token_manager=TokenManager(secret="test-secret"),
        service=PlatformService(store, build_demo_connector()),
    )

    client = TestClient(app)
    login = client.post("/auth/login", json={"username": "admin", "password": "AdminTemporal!2026"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    summary = client.get("/system/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["columns_total"] == 200
    assert summary.json()["real_io_enabled"] is False

    columns = client.get("/columns?block_id=1", headers=headers)
    assert columns.status_code == 200
    assert len(columns.json()) == 20

    command = client.post("/commands", headers=headers, json={"column_id": 5, "command_type": "start"})
    assert command.status_code == 200
    assert command.json()["Status"] == "Applied"
    assert store.columns[5].state == "Running"


def test_api_recipe_and_campaign_are_functional():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    app = create_app(
        store=store,
        token_manager=TokenManager(secret="test-secret"),
        service=PlatformService(store, build_demo_connector()),
    )
    client = TestClient(app)
    token = client.post("/auth/login", json={"username": "admin", "password": "AdminTemporal!2026"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    recipe = client.post(
        "/recipes",
        headers=headers,
        json={"name": "Receta API", "flow_setpoint_kg_h": 14.2, "temperature_setpoint_c": 26.0},
    )
    assert recipe.status_code == 200
    recipe_id = recipe.json()["id"]

    approved = client.post(f"/recipes/{recipe_id}/approve", headers=headers)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    campaign = client.post(
        "/campaigns",
        headers=headers,
        json={"name": "Campaña API", "recipe_id": recipe_id, "column_ids": [1, 2, 3]},
    )
    assert campaign.status_code == 200
    campaign_id = campaign.json()["id"]

    started = client.post(f"/campaigns/{campaign_id}/start", headers=headers)
    assert started.status_code == 200
    assert started.json()["status"] == "running"


def test_api_admin_can_create_user_and_update_profile():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    app = create_app(
        store=store,
        token_manager=TokenManager(secret="test-secret"),
        service=PlatformService(store, build_demo_connector()),
    )
    client = TestClient(app)
    token = client.post("/auth/login", json={"username": "admin", "password": "AdminTemporal!2026"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/users",
        headers=headers,
        json={
            "username": "supervisor1",
            "display_name": "Supervisor Uno",
            "role_id": "supervisor",
            "temporary_password": "Temporal!2026",
        },
    )
    assert created.status_code == 200
    assert created.json()["username"] == "supervisor1"

    updated = client.patch(
        "/users/supervisor1/profile",
        headers=headers,
        json={"profile_photo_url": "https://example.invalid/avatar.png"},
    )
    assert updated.status_code == 200
    assert updated.json()["profile_photo_url"].endswith("avatar.png")
