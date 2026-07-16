from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from codesys_opcua_interface.integrations import (
    CONTROL_KEYWORDS,
    integration_status,
    list_grafana_dashboards,
    list_node_red_flows,
)
from codesys_opcua_interface.platform_store import PlatformService, TokenManager, build_demo_connector, create_demo_store
from services.api.app import create_app


ROOT = Path(__file__).resolve().parents[1]


def test_grafana_dashboards_are_provisioned_read_only() -> None:
    dashboards = list_grafana_dashboards(ROOT)

    assert {dashboard.uid for dashboard in dashboards} >= {
        "column-overview",
        "column-trends",
        "communications-diagnostics",
    }
    assert all(dashboard.editable is False for dashboard in dashboards)
    assert all(dashboard.panels > 0 for dashboard in dashboards)
    assert all("readonly" in dashboard.tags for dashboard in dashboards)

    datasource = (ROOT / "grafana" / "provisioning" / "datasources" / "platform-postgres.yaml").read_text(encoding="utf-8")
    assert "Platform PostgreSQL Readonly" in datasource
    assert "editable: false" in datasource
    assert "${GRAFANA_POSTGRES_PASSWORD}" in datasource


def test_node_red_flows_are_observability_only() -> None:
    flows = list_node_red_flows(ROOT)

    assert flows
    assert all(flow.contains_control_keywords is False for flow in flows)
    assert any(flow.label == "Notificaciones y reportes" for flow in flows)

    serialized = (ROOT / "node-red" / "flows" / "notifications.json").read_text(encoding="utf-8")
    for keyword in CONTROL_KEYWORDS:
        assert keyword not in serialized


def test_reverse_proxy_keeps_admin_editor_closed_by_default() -> None:
    nginx_conf = (ROOT / "reverse-proxy" / "nginx.conf").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.demo.yml").read_text(encoding="utf-8")

    assert "location /grafana/" in nginx_conf
    assert "location /node-red/" in nginx_conf
    assert "location /node-red-admin/" in nginx_conf
    assert "return 403;" in nginx_conf
    assert 'REAL_IO_ENABLED: "false"' in compose
    assert 'NODE_RED_DISABLE_EDITOR: "true"' in compose


def test_api_exposes_integration_status_without_control_authority() -> None:
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    app = create_app(
        store=store,
        token_manager=TokenManager(secret="test-secret"),
        service=PlatformService(store, build_demo_connector()),
    )
    client = TestClient(app)
    token = client.post("/auth/login", json={"username": "admin", "password": "AdminTemporal!2026"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/integrations", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["grafana"]["control_allowed"] is False
    assert payload["node_red"]["control_allowed"] is False
    assert len(payload["grafana"]["dashboards"]) >= 3
    assert all(not item["editable"] for item in payload["grafana"]["dashboards"])
    assert all(not item["contains_control_keywords"] for item in payload["node_red"]["flows"])


def test_integration_status_shape_is_stable() -> None:
    payload = integration_status(ROOT)

    assert payload["grafana"]["base_path"] == "/grafana/"
    assert payload["node_red"]["runtime_base_path"] == "/node-red/"
    assert payload["node_red"]["admin_base_path"] == "/node-red-admin/"
