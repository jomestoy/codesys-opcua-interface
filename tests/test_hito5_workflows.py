from __future__ import annotations

from fastapi.testclient import TestClient

from codesys_opcua_interface.platform_store import PlatformService, TokenManager, build_demo_connector, create_demo_store
from services.api.app import create_app


def _admin_store():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    return store, store.authenticate("admin", "AdminTemporal!2026")


def test_recipe_hito5_versioning_clone_reject_compare_obsolete_and_assign():
    store, admin = _admin_store()

    recipe = store.create_recipe(admin, {"name": "Receta H5", "flow_setpoint_kg_h": 10.5})
    clone = store.clone_recipe(admin, recipe.id, {"change_note": "ajuste flujo"})
    store.reject_recipe(admin, clone.id, "requiere revision metalurgica")
    updated = store.update_recipe(admin, clone.id, {"flow_setpoint_kg_h": 11.0, "change_note": "corregida"})
    approved = store.approve_recipe(admin, updated.id)
    comparison = store.compare_recipes(admin, recipe.id, approved.id)
    assigned = store.assign_recipe(admin, approved.id, [1, 2, 3])
    obsolete = store.obsolete_recipe(admin, recipe.id)

    assert clone.version == 2
    assert approved.status == "approved"
    assert "flow_setpoint_kg_h" in comparison["differences"]
    assert assigned["column_ids"] == [1, 2, 3]
    assert store.columns[1].recipe_id == approved.id
    assert obsolete.status == "obsolete"


def test_campaign_hito5_schedule_pause_finish_cancel_compare_and_export():
    store, admin = _admin_store()
    recipe = store.create_recipe(admin, {"name": "Receta campaña H5", "flow_setpoint_kg_h": 9.0})
    store.approve_recipe(admin, recipe.id)
    campaign = store.create_campaign(admin, {"name": "Campaña H5", "recipe_id": recipe.id, "column_ids": [21, 22]})
    store.schedule_campaign(admin, campaign.id, "2026-07-20T08:00:00Z")
    store.start_campaign(admin, campaign.id)
    paused = store.pause_campaign(admin, campaign.id)
    paused_status = paused.status
    exported = store.export_campaign(admin, campaign.id)
    finished = store.finalize_campaign(admin, campaign.id)

    second = store.create_campaign(admin, {"name": "Campaña H5 cancel", "recipe_id": recipe.id, "column_ids": [23, 24]})
    cancelled = store.cancel_campaign(admin, second.id, "prueba cancelacion")
    comparison = store.compare_campaigns(admin, campaign.id, second.id)

    assert paused_status == "paused"
    assert exported["summary"]["column_count"] == 2
    assert finished.status == "finished"
    assert store.columns[21].campaign_id is None
    assert cancelled.status == "cancelled"
    assert comparison["differences"]["status"]["left"] == "finished"


def test_alarm_hito5_configurable_rule_history_ack_clear_and_export():
    store, admin = _admin_store()
    rule = store.create_alarm_rule(
        admin,
        {
            "name": "Calidad baja H5",
            "variable": "data_quality",
            "operator": "lt",
            "threshold": 0.5,
            "priority": "critical",
            "target_scope": "columns",
            "column_ids": [42],
            "action": "notify",
        },
    )
    triggered = store.evaluate_alarm_rules(admin)
    alarm = triggered[0]
    acked = store.acknowledge_alarm(admin, alarm.id, "verificado por supervisor")
    cleared = store.clear_alarm(admin, alarm.id, "dato recuperado")
    exported = store.export_alarms(admin)

    assert rule.version == 1
    assert alarm.column_id == 42
    assert acked.acknowledged_by == "admin"
    assert cleared.active is False
    assert len(store.alarm_history) >= 3
    assert any(item["id"] == alarm.id for item in exported["alarms"])


def test_hito5_api_endpoints_for_recipes_campaigns_and_alarm_rules():
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    app = create_app(
        store=store,
        token_manager=TokenManager(secret="test-secret"),
        service=PlatformService(store, build_demo_connector()),
    )
    client = TestClient(app)
    token = client.post("/auth/login", json={"username": "admin", "password": "AdminTemporal!2026"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    recipe = client.post("/recipes/REC-DEMO-001/clone", headers=headers, json={"change_note": "API clone"})
    assert recipe.status_code == 200
    recipe_id = recipe.json()["id"]
    assert client.post(f"/recipes/{recipe_id}/reject", headers=headers, json={"reason": "API reject"}).status_code == 200
    assert client.patch(f"/recipes/{recipe_id}", headers=headers, json={"flow_setpoint_kg_h": 15.0}).status_code == 200
    assert client.post(f"/recipes/{recipe_id}/approve", headers=headers).status_code == 200
    assert client.get(f"/recipes/compare?left_id=REC-DEMO-001&right_id={recipe_id}", headers=headers).status_code == 200
    assert client.post(f"/recipes/{recipe_id}/assign", headers=headers, json={"column_ids": [5, 6]}).status_code == 200

    campaign = client.post(
        "/campaigns",
        headers=headers,
        json={"name": "API H5", "recipe_id": recipe_id, "column_ids": [5, 6]},
    )
    assert campaign.status_code == 200
    campaign_id = campaign.json()["id"]
    assert client.post(f"/campaigns/{campaign_id}/schedule", headers=headers, json={"scheduled_start": "2026-07-20T08:00:00Z"}).status_code == 200
    assert client.post(f"/campaigns/{campaign_id}/start", headers=headers).status_code == 200
    assert client.get(f"/campaigns/{campaign_id}/export", headers=headers).status_code == 200

    rule = client.post(
        "/alarm-rules",
        headers=headers,
        json={
            "name": "API calidad baja",
            "variable": "data_quality",
            "operator": "lt",
            "threshold": 0.5,
            "target_scope": "columns",
            "column_ids": [42],
        },
    )
    assert rule.status_code == 200
    triggered = client.post("/alarm-rules/evaluate", headers=headers)
    assert triggered.status_code == 200
    assert triggered.json()
