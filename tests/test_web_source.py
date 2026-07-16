from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPO_ROOT / "apps" / "web"


def test_web_package_declares_required_hito4_stack():
    package = json.loads((WEB_ROOT / "package.json").read_text(encoding="utf-8"))
    dependencies = {**package["dependencies"], **package["devDependencies"]}

    for dependency in ["react", "vite", "@mui/material", "@tanstack/react-query", "typescript"]:
        assert dependency in dependencies


def test_web_source_contains_functional_screens_and_control_flow():
    app_source = (WEB_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    api_source = (WEB_ROOT / "src" / "api.ts").read_text(encoding="utf-8")

    for label in ["Resumen", "Planta", "Recetas", "Campañas", "Alarmas", "Integraciones", "Usuarios", "Auditoría"]:
        assert label in app_source

    for route in [
        "/auth/login",
        "/system/summary",
        "/columns",
        "/commands",
        "/recipes",
        "/recipes/compare",
        "/campaigns",
        "/alarm-rules",
        "/alarms/export",
        "/integrations",
        "/users",
    ]:
        assert route in api_source

    assert "api.command" in app_source
    assert "api.cloneRecipe" in app_source
    assert "api.pauseCampaign" in app_source
    assert "api.createAlarmRule" in app_source
    assert "api.integrations" in app_source
    assert "REAL_IO_ENABLED" in app_source
