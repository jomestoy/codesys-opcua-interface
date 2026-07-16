from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codesys_opcua_interface.codesys_project import validate_codesys_sources, write_plcopen_xml


def main() -> int:
    codesys_root = REPO_ROOT / "codesys-control"
    validation = validate_codesys_sources(codesys_root)
    if not validation.ok:
        print("CODESYS source validation failed")
        print(validation)
        return 1

    output = write_plcopen_xml(codesys_root, codesys_root / "plcopen" / "codesys-control.plcopen.xml")
    print(f"PLCopen preliminary source written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
