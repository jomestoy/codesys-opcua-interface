from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_test_simulates_200_columns_and_failover(tmp_path: Path) -> None:
    load_test = _load_script("load_test")

    report = tmp_path / "load.json"
    payload = asyncio.run(load_test.run_load_test(columns=200, commands=40, report=report))

    assert payload["mode"] == "offline_simulation"
    assert payload["real_io_enabled"] is False
    assert payload["columns"] == 200
    assert payload["commands"] == 40
    assert payload["failures"] == 0
    assert payload["failover"]["before"] == "CODESYS-A"
    assert payload["failover"]["after"] == "CODESYS-B"
    assert payload["commands_recorded"] >= 41
    assert report.exists()


def test_security_audit_passes_without_secrets_or_real_io() -> None:
    security_audit = _load_script("security_audit")

    payload = security_audit.run_security_audit(ROOT)

    assert payload["status"] == "passed"
    assert payload["findings"] == []
    assert payload["real_io_default"] == "false"


def test_playwright_sources_are_present_for_ui_hito9() -> None:
    package = (ROOT / "apps" / "web" / "package.json").read_text(encoding="utf-8")
    spec = (ROOT / "apps" / "web" / "tests" / "e2e.spec.ts").read_text(encoding="utf-8")
    config = (ROOT / "apps" / "web" / "playwright.config.ts").read_text(encoding="utf-8")

    assert "@playwright/test" in package
    assert "test:e2e" in package
    assert "Inicio de sesión" in spec
    assert "Integraciones" in spec
    assert "baseURL" in config
