from codesys_opcua_interface.control_math import GravimetricFlowEstimator, SlowPIController, WeightSample


def test_gravimetric_estimator_uses_regression_slope():
    estimator = GravimetricFlowEstimator(window_s=180, min_points=6, max_step_kg=100)
    for i in range(12):
        estimator.add_sample(WeightSample(timestamp_s=i * 10.0, weight_kg=1000.0 - i * 0.5))

    estimate = estimator.estimate()

    assert estimate.frozen is False
    assert estimate.point_count == 12
    assert 175 <= estimate.flow_kg_h <= 185
    assert estimate.quality > 0.9


def test_estimator_freezes_on_non_monotonic_time():
    estimator = GravimetricFlowEstimator(min_points=2)
    estimator.add_sample(WeightSample(timestamp_s=10.0, weight_kg=1000.0))
    estimator.add_sample(WeightSample(timestamp_s=9.0, weight_kg=999.0))

    estimate = estimator.estimate()

    assert estimate.frozen is True
    assert estimate.reason == "non_monotonic_timestamp"


def test_slow_pi_rate_limits_and_freezes_integrator():
    pi = SlowPIController(kp=0.2, ki=0.05, max_delta_pct=2.0)

    first = pi.update(setpoint=100.0, measured=80.0, dt_s=30.0)
    frozen = pi.update(setpoint=100.0, measured=70.0, dt_s=30.0, freeze=True, reason="bad_quality")

    assert first.output_pct == 2.0
    assert frozen.output_pct == first.output_pct
    assert frozen.frozen is True
    assert frozen.reason == "bad_quality"
