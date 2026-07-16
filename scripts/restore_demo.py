from __future__ import annotations

import argparse
import shutil
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PREFIXES = (
    "platform-demo/config/",
    "platform-demo/database/migrations/",
    "platform-demo/database/seeds/",
    "platform-demo/grafana/dashboards/",
    "platform-demo/grafana/provisioning/",
    "platform-demo/node-red/flows/",
    "platform-demo/node-red/settings/",
    "platform-demo/mosquitto/",
    "platform-demo/reverse-proxy/",
    "platform-demo/docker-compose.demo.yml",
    "platform-demo/.env.example",
)


def validate_backup(archive: Path) -> list[str]:
    errors: list[str] = []
    if not archive.exists():
        return [f"backup no existe: {archive}"]
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            if member.islnk() or member.issym():
                errors.append(f"links no permitidos: {member.name}")
            if ".." in Path(member.name).parts:
                errors.append(f"ruta insegura: {member.name}")
            if not any(member.name == prefix.rstrip("/") or member.name.startswith(prefix) for prefix in ALLOWED_PREFIXES):
                errors.append(f"ruta fuera de alcance: {member.name}")
    return errors


def restore_backup(archive: Path, root: Path = ROOT, apply: bool = False) -> dict[str, object]:
    errors = validate_backup(archive)
    if errors:
        return {"status": "invalid", "errors": errors, "applied": False}
    if not apply:
        return {"status": "validated", "errors": [], "applied": False}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(tmp_path)
        source = tmp_path / "platform-demo"
        for child in source.iterdir():
            target = root / child.name
            if child.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(child, target)
            else:
                shutil.copy2(child, target)
    return {"status": "restored", "errors": [], "applied": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = restore_backup(args.archive, apply=args.apply)
    print(result)
    raise SystemExit(0 if result["status"] in {"validated", "restored"} else 1)


if __name__ == "__main__":
    main()
