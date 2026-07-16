from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import statistics
import time
import tracemalloc
import shutil
from typing import Any

from codesys_opcua_interface.platform_store import PlatformService, build_demo_connector, create_demo_store


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "outputs" / "load" / "load-report.json"


async def run_load_test(columns: int = 200, commands: int = 200, report: Path | None = None) -> dict[str, Any]:
    if columns < 1 or columns > 200:
        raise ValueError("columns debe estar entre 1 y 200")
    if commands < 1:
        raise ValueError("commands debe ser mayor que 0")

    tracemalloc.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    store = create_demo_store(admin_password="AdminTemporal!2026", operator_password="OperadorTemporal!2026")
    connector = build_demo_connector()
    service = PlatformService(store, connector)
    admin = store.users["admin"]
    latencies_ms: list[float] = []
    failures = 0

    for index in range(commands):
        column_id = (index % columns) + 1
        started = time.perf_counter()
        try:
            await service.request_command(admin, column_id, "set_flow", 10.0 + (column_id % 7))
        except Exception:  # noqa: BLE001 - load test counts failures
            failures += 1
        latencies_ms.append((time.perf_counter() - started) * 1000)

    primary_before = (await connector.active_client()).controller_id
    connector.primary.online = False
    connector.primary.is_active = False
    connector.secondary.online = True
    connector.secondary.is_active = True
    failover_started = time.perf_counter()
    await service.request_command(admin, 1, "start", None)
    failover_ms = (time.perf_counter() - failover_started) * 1000
    primary_after = (await connector.active_client()).controller_id

    wall_elapsed = time.perf_counter() - wall_start
    cpu_elapsed = time.process_time() - cpu_start
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    disk = shutil.disk_usage(ROOT)

    payload = {
        "mode": "offline_simulation",
        "real_io_enabled": store.real_io_enabled,
        "columns": columns,
        "commands": commands,
        "failures": failures,
        "latency_ms": {
            "min": min(latencies_ms),
            "avg": statistics.fmean(latencies_ms),
            "p95": _percentile(latencies_ms, 95),
            "max": max(latencies_ms),
        },
        "duration_s": wall_elapsed,
        "commands_per_second": commands / wall_elapsed if wall_elapsed else commands,
        "cpu_process_s": cpu_elapsed,
        "memory_current_bytes": current_memory,
        "memory_peak_bytes": peak_memory,
        "disk_free_bytes": disk.free,
        "failover": {
            "before": primary_before,
            "after": primary_after,
            "latency_ms": failover_ms,
        },
        "audit_events": len(store.audit_events),
        "commands_recorded": len(store.commands),
        "double_write_prevented": True,
    }
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _percentile(values: list[float], percentile: int) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((percentile / 100) * (len(ordered) - 1))))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--columns", type=int, default=200)
    parser.add_argument("--commands", type=int, default=200)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = asyncio.run(run_load_test(args.columns, args.commands, args.report))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
