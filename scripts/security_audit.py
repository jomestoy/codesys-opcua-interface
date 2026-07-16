from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "outputs" / "security" / "security-audit.json"
SECRET_PATTERNS = {
    "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC |)PRIVATE KEY"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    "api_secret_assignment": re.compile(r"API_TOKEN_SECRET[ \t]*=[ \t]*['\"]?[A-Za-z0-9][^\s'\"]+"),
    "postgres_password_assignment": re.compile(r"(?:POSTGRES_PASSWORD|GRAFANA_POSTGRES_PASSWORD)[ \t]*=[ \t]*['\"]?[A-Za-z0-9][^\s'\"]+"),
}
SCAN_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".md", ".sql", ".toml", ".example"}
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", "outputs", "__pycache__"}


def run_security_audit(root: Path = ROOT, report: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for path in _iter_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(root).as_posix()
        for name, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                if _is_allowed_placeholder(relative, match.group(0)):
                    continue
                findings.append({"type": name, "path": relative})
        if "REAL_IO_ENABLED=true" in text or 'REAL_IO_ENABLED: "true"' in text:
            findings.append({"type": "real_io_enabled_true", "path": relative})
        if "auth_anonymous_org_role: Admin" in text:
            findings.append({"type": "grafana_anonymous_admin", "path": relative})

    required_false = (root / ".env.example").read_text(encoding="utf-8")
    if "REAL_IO_ENABLED=false" not in required_false:
        findings.append({"type": "real_io_default_missing", "path": ".env.example"})

    payload = {
        "status": "passed" if not findings else "failed",
        "findings": findings,
        "scanned_files": len(list(_iter_files(root))),
        "real_io_default": "false",
    }
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "security_audit.py":
            continue
        if path.is_file() and (path.suffix in SCAN_EXTENSIONS or path.name.endswith(".example")):
            yield path


def _is_allowed_placeholder(relative: str, text: str) -> bool:
    if relative == ".env.example" and (text.endswith("=") or text.endswith("=.+")):
        return True
    return "${" in text or "<" in text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = run_security_audit(report=args.report)
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(0 if payload["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
