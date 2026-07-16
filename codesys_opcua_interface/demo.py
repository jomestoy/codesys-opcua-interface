from __future__ import annotations

import argparse
import json

from .command_model import ColumnCommand
from .control_math import GravimetricFlowEstimator, SlowPIController, WeightSample
from .redundancy import RedundantCodesysSimulator


def run_demo(columns: int = 200, ticks: int = 10) -> dict[str, object]:
    sim = RedundantCodesysSimulator("opc.tcp://codesys-a:4840", "opc.tcp://codesys-b:4840")
    estimators = [GravimetricFlowEstimator(min_points=4, window_s=180) for _ in range(columns)]
    controller = SlowPIController()
    for t in range(ticks):
        sim.tick()
        for idx, estimator in enumerate(estimators, start=1):
            estimator.add_sample(WeightSample(timestamp_s=t * 10.0, weight_kg=1000.0 - idx * 0.01 - t * 0.25))
    estimate = estimators[0].estimate()
    pi = controller.update(setpoint=90.0, measured=estimate.flow_kg_h, dt_s=30.0)
    command = sim.submit_command(ColumnCommand(column_id=1, command_type="set_flow", requested_value=90.0, requested_by="demo.admin"), idempotency_key="demo-1")
    sim.fail_primary()
    sim.tick()
    return {
        "real_io_enabled": False,
        "columns": columns,
        "estimate_column_1": estimate.__dict__,
        "pi_column_1": pi.__dict__,
        "command": command.as_mailbox_payload(),
        "redundancy": sim.status(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--columns", type=int, default=200)
    parser.add_argument("--ticks", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(run_demo(args.columns, args.ticks), indent=2, default=str))


if __name__ == "__main__":
    main()
