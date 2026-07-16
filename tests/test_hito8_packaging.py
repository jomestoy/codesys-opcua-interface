from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import re
import tarfile


ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_backup_and_restore_validate_demo_configuration(tmp_path: Path) -> None:
    backup_demo = _load_script("backup_demo")
    restore_demo = _load_script("restore_demo")

    archive = backup_demo.create_backup(ROOT, tmp_path)
    result = restore_demo.restore_backup(archive, ROOT, apply=False)

    assert archive.exists()
    assert result["status"] == "validated"
    with tarfile.open(archive, "r:gz") as tar:
        names = set(tar.getnames())
    assert "platform-demo/docker-compose.demo.yml" in names
    assert "platform-demo/grafana/dashboards/column-overview.json" in names


def test_restore_rejects_path_traversal(tmp_path: Path) -> None:
    restore_demo = _load_script("restore_demo")
    archive = tmp_path / "bad.tar.gz"
    payload = b"bad"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("platform-demo/../evil.txt")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))

    errors = restore_demo.validate_backup(archive)

    assert errors
    assert any("ruta insegura" in error or "ruta fuera de alcance" in error for error in errors)


def test_hito8_makefile_and_compose_wire_demo_services() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.demo.yml").read_text(encoding="utf-8")

    assert "$(COMPOSE) up --build" in makefile
    assert "package-gateway" in makefile
    assert "backup_demo.py" in makefile
    assert "restore_demo.py" in makefile
    assert "postgres:" in compose
    assert "POSTGRES_HOST_AUTH_METHOD" in compose
    assert 'REAL_IO_ENABLED: "false"' in compose


def test_grafana_queries_match_demo_schema() -> None:
    dashboards = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "grafana" / "dashboards").glob("*.json"))

    assert "series_time" in dashboards
    assert "codesys_endpoints" in dashboards
    assert "opcua_metrics" in dashboards
    assert "gateway_metrics" in dashboards
    assert not re.search(r"select\s+ts\s+as\s+time[^\";]+historical_series", dashboards, flags=re.IGNORECASE)
