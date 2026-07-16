from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_DIR = ROOT / "backups"
BACKUP_PATHS = (
    "config",
    "database/migrations",
    "database/seeds",
    "grafana/dashboards",
    "grafana/provisioning",
    "node-red/flows",
    "node-red/settings",
    "mosquitto",
    "reverse-proxy",
    "docker-compose.demo.yml",
    ".env.example",
)


def create_backup(root: Path = ROOT, output_dir: Path = DEFAULT_BACKUP_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = output_dir / f"platform-demo-backup-{stamp}.tar.gz"
    with tarfile.open(target, "w:gz") as tar:
        for relative in BACKUP_PATHS:
            path = root / relative
            if path.exists():
                tar.add(path, arcname=f"platform-demo/{relative}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    args = parser.parse_args()
    print(create_backup(output_dir=args.output_dir))


if __name__ == "__main__":
    main()
