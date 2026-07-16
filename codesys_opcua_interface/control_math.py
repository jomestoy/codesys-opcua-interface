from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from statistics import median


@dataclass(frozen=True)
class WeightSample:
    timestamp_s: float
    weight_kg: float
    quality: float = 1.0
    stable: bool = True


@dataclass
class FlowEstimate:
    flow_kg_h: float
    quality: float
    point_count: int
    frozen: bool
    reason: str = ""


@dataclass
class GravimetricFlowEstimator:
    """Offline equivalent of the CODESYS gravimetric estimator.

    Flow is the negative slope of weight vs monotonic time, converted to kg/h.
    It intentionally avoids two-point delta calculations.
    """

    window_s: float = 120.0
    min_points: int = 8
    max_points: int = 120
    max_step_kg: float = 50.0
    min_quality: float = 0.5
    samples: list[WeightSample] = field(default_factory=list)
    frozen: bool = False
    freeze_reason: str = ""

    def add_sample(self, sample: WeightSample) -> None:
        if not isfinite(sample.timestamp_s) or not isfinite(sample.weight_kg):
            self.freeze("invalid_sample")
            return
        if self.samples and sample.timestamp_s <= self.samples[-1].timestamp_s:
            self.freeze("non_monotonic_timestamp")
            return
        if sample.quality < self.min_quality or not sample.stable:
            self.freeze("bad_quality")
        if self.samples and abs(sample.weight_kg - self.samples[-1].weight_kg) > self.max_step_kg:
            self.freeze("outlier_or_refill")
        self.samples.append(sample)
        cutoff = sample.timestamp_s - self.window_s
        self.samples = [item for item in self.samples[-self.max_points :] if item.timestamp_s >= cutoff]

    def freeze(self, reason: str) -> None:
        self.frozen = True
        self.freeze_reason = reason

    def clear_freeze(self) -> None:
        self.frozen = False
        self.freeze_reason = ""

    def estimate(self) -> FlowEstimate:
        valid = [s for s in self.samples if s.quality >= self.min_quality and s.stable]
        if self.frozen:
            return FlowEstimate(0.0, 0.0, len(valid), True, self.freeze_reason)
        if len(valid) < self.min_points:
            return FlowEstimate(0.0, 0.0, len(valid), True, "insufficient_points")

        weights = [s.weight_kg for s in valid]
        med = median(weights)
        filtered = [s for s in valid if abs(s.weight_kg - med) <= self.max_step_kg]
        if len(filtered) < self.min_points:
            return FlowEstimate(0.0, 0.0, len(filtered), True, "outlier_filter_removed_points")

        n = len(filtered)
        mean_t = sum(s.timestamp_s for s in filtered) / n
        mean_w = sum(s.weight_kg for s in filtered) / n
        denom = sum((s.timestamp_s - mean_t) ** 2 for s in filtered)
        if denom <= 0:
            return FlowEstimate(0.0, 0.0, n, True, "zero_time_variance")
        slope_kg_s = sum((s.timestamp_s - mean_t) * (s.weight_kg - mean_w) for s in filtered) / denom
        fitted = [mean_w + slope_kg_s * (s.timestamp_s - mean_t) for s in filtered]
        residual = sum(abs(s.weight_kg - fit) for s, fit in zip(filtered, fitted)) / n
        span = max(weights) - min(weights)
        quality = max(0.0, min(1.0, 1.0 - residual / max(span, 1.0)))
        return FlowEstimate(flow_kg_h=max(0.0, -slope_kg_s * 3600.0), quality=quality, point_count=n, frozen=False)


@dataclass
class PIState:
    output_pct: float
    integral: float
    frozen: bool
    reason: str = ""


@dataclass
class SlowPIController:
    kp: float = 0.08
    ki: float = 0.01
    deadband_pct: float = 0.03
    output_min_pct: float = 0.0
    output_max_pct: float = 100.0
    max_delta_pct: float = 3.0
    integral: float = 0.0
    last_output_pct: float = 0.0

    def update(self, setpoint: float, measured: float, dt_s: float, freeze: bool = False, manual_output: float | None = None, reason: str = "") -> PIState:
        if manual_output is not None:
            self.last_output_pct = self._clamp(manual_output)
            self.integral = self.last_output_pct
            return PIState(self.last_output_pct, self.integral, True, "manual")
        if freeze:
            return PIState(self.last_output_pct, self.integral, True, reason or "freeze")
        if setpoint <= 0 or dt_s <= 0:
            return PIState(self.last_output_pct, self.integral, True, "invalid_setpoint_or_dt")
        error = setpoint - measured
        if abs(error) / setpoint <= self.deadband_pct:
            return PIState(self.last_output_pct, self.integral, False, "deadband")
        proposed_integral = self.integral + self.ki * error * dt_s
        raw = self.kp * error + proposed_integral
        limited = self._clamp(raw)
        if limited == raw:
            self.integral = proposed_integral
        delta = max(-self.max_delta_pct, min(self.max_delta_pct, limited - self.last_output_pct))
        self.last_output_pct = self._clamp(self.last_output_pct + delta)
        return PIState(self.last_output_pct, self.integral, False)

    def _clamp(self, value: float) -> float:
        return max(self.output_min_pct, min(self.output_max_pct, value))
