"""verification_type: software_test. Synthetic controls are not physical measurements."""

import json
import math
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from upi.dna import DNAReader
from upi.spiral_flow import (
    DetectionPolicy,
    NavierMode,
    SimulationState,
    advance_particles,
    detect_dynamic_nodes,
    differentiate,
    dynamic_reference_points,
    estimate_crossing_frequency,
    frequency_state,
    integrate_phase_samples,
    interpolate_frequency,
    navier_stokes_residual,
    rigid_vortex_velocity,
    rotation_terms,
    run_dynamic_series,
    select_mode,
)

POLICY = DetectionPolicy(
    rapid_rate_hz_s=5, stable_rate_hz_s=0.01, jump_hz=2, response_prominence=0.5
)
ROOT = Path(__file__).resolve().parents[1]


def run(times, frequencies, **kwargs):
    options = {
        "initial_positions": ((0.1, 0.2, 0.3), (0.2, -0.1, -0.2)),
        "phase0_rad": 0.7,
        "density": 1000,
        "viscosity": 1e-6,
        "force_mode": "manufactured_rotation",
        "detection": POLICY,
        "residual_tolerance": 1e-8,
    }
    options.update(kwargs)
    return run_dynamic_series(times, frequencies, **options)


@pytest.mark.parametrize("f", [1.766, 7.834125, 1 / 0.126, 8, 11.321])
def test_constant_frequency_controls(f):
    report = run([0, 0.001, 0.002, 0.003], [f] * 4, force_mode="none")
    assert report["state"] == "PASS"
    for row in report["rows"]:
        assert row["T"] * f == pytest.approx(1)
        assert row["omega"] == pytest.approx(2 * math.pi * f)
        assert row["curl_magnitude"] == pytest.approx(4 * math.pi * f)
        assert row["domega_dt"] == 0
        assert row["divergence"] == 0
        assert row["phi"] == pytest.approx(0.7 + 2 * math.pi * f * row["t"])


def test_reference_difference_is_signed_and_normalized_explicitly():
    points = {p.label: p for p in dynamic_reference_points()}
    assert points["gen_pulse_0.126s"].frequency_hz != points["resonance_7.834125"].frequency_hz
    report = run([0, 0.1, 0.2], [1, 1, 1])
    difference = report["reference_difference"]
    assert difference["delta_T_s"] == pytest.approx(0.126 - 1 / 7.834125)
    assert difference["relative_to_resonance_period"] == pytest.approx(0.126 * 7.834125 - 1)


def test_chirp_phase_rejects_instantaneous_frequency_times_elapsed_time():
    times = [2, 2.01, 2.03, 2.06]
    freq = [1 + 3 * (t - 2) for t in times]
    phase = integrate_phase_samples(times, freq, 0.4)
    expected = 0.4
    for n in range(1, len(times)):
        expected += 2 * math.pi * freq[n] * (times[n] - times[n - 1])
        assert phase[n] == pytest.approx(expected)
    assert phase[-1] != pytest.approx(0.4 + 2 * math.pi * freq[-1] * (times[-1] - times[0]))
    assert differentiate(times, freq) == pytest.approx([3] * 4)
    report = run(times, freq)
    assert [r["domega_dt"] for r in report["rows"]] == pytest.approx([6 * math.pi] * 4)


def test_right_quadrature_converges_to_chirp_integral():
    errors = []
    for n in [100, 200]:
        t = [i / n for i in range(n + 1)]
        phase = integrate_phase_samples(t, [2 + 3 * x for x in t], 0)
        exact = 2 * math.pi * (2 + 1.5)
        errors.append(abs(phase[-1] - exact))
    assert errors[1] == pytest.approx(errors[0] / 2, rel=1e-10)


def test_nonuniform_derivative_and_interpolation():
    t = [0, 0.1, 0.4, 0.7, 1]
    assert differentiate(t, [x * x for x in t])[1:-1] == pytest.approx([0.2, 0.8, 1.4])
    assert interpolate_frequency([0, 0.2, 1], [1, 3, 5], 0.6) == pytest.approx(4)
    with pytest.raises(ValueError):
        interpolate_frequency([0, 0.2, 1], [1, 3, 5], 2)


def test_unsteady_spatial_and_temporal_terms_against_finite_differences():
    point = (0.3, -0.4, 0.2)
    f, rate, eps = 1.766, 0.9, 1e-6
    omega, alpha = 2 * math.pi * f, 2 * math.pi * rate
    terms = rotation_terms(point, f, rate, 1000, 1e-6, force=(0, 0, 0))
    plus = rigid_vortex_velocity(point[0], point[1], f + rate * eps)
    minus = rigid_vortex_velocity(point[0], point[1], f - rate * eps)
    assert terms["dt_velocity"] == pytest.approx(
        tuple((p - m) / (2 * eps) for p, m in zip(plus, minus, strict=True))
    )
    assert terms["convective"] == pytest.approx((-(omega**2) * point[0], -(omega**2) * point[1], 0))
    assert terms["laplacian_velocity"] == (0, 0, 0)
    dxvy = (
        rigid_vortex_velocity(point[0] + eps, point[1], f)[1]
        - rigid_vortex_velocity(point[0] - eps, point[1], f)[1]
    ) / (2 * eps)
    dyvx = (
        rigid_vortex_velocity(point[0], point[1] + eps, f)[0]
        - rigid_vortex_velocity(point[0], point[1] - eps, f)[0]
    ) / (2 * eps)
    assert dxvy - dyvx == pytest.approx(terms["curl"][2])
    assert terms["residual"] == pytest.approx((-alpha * point[1], alpha * point[0], 0))
    balanced = rotation_terms(
        point, f, rate, 1000, 1e-6, force=(-alpha * point[1], alpha * point[0], 0)
    )
    assert balanced["residual"] == pytest.approx((0, 0, 0), abs=1e-12)


def test_missing_forcing_fails_without_changing_kinematic_classification():
    report = run([0, 0.01, 0.02], [2, 3, 4], force_mode="none")
    assert report["state"] == "STOP"
    assert all(r["residual_validation"] == "FAIL" for r in report["rows"])
    assert all(r["kinematic_validation"] == "PASS" and r["status"] == "DER" for r in report["rows"])
    assert report["promotion"] == "BLOCKED"


def test_three_modes_use_identical_particles_time_frequency_and_phase():
    times = [i * 0.001 for i in range(12)]
    frequencies = [2 + t for t in times]
    cycling = run(times, frequencies)
    fixed = run(times, frequencies, modes=(NavierMode.VELOCITY,))
    for a, b in zip(cycling["rows"], fixed["rows"], strict=True):
        for key in ["t", "f", "omega", "phi", "particle_positions", "particle_fields"]:
            assert a[key] == b[key]
    assert cycling["rows"][3]["navier_mode"] == "velocity_field"
    state = SimulationState(0, 0, 2, 4 * math.pi, 1, ((1, 0, 0),))
    for mode in NavierMode:
        viewed = state.with_mode(mode)
        assert (
            viewed.positions == state.positions and viewed.t == state.t and viewed.phi == state.phi
        )
    with pytest.raises(ValueError):
        select_mode(0, ())


def test_euler_particle_step_and_radius_error_convergence():
    initial = SimulationState(0, 0, 1, 2 * math.pi, 0, ((1, 0, 3),))
    advanced = advance_particles(initial, 0.01, 2)
    assert advanced.positions[0] == pytest.approx((1, 0.02 * math.pi, 3))
    assert advanced.phi == pytest.approx(0.04 * math.pi)
    errors = []
    for n in [100, 200]:
        state = initial
        for i in range(1, n + 1):
            state = advance_particles(state, i * 0.1 / n, 1)
        errors.append(abs(math.hypot(*state.positions[0][:2]) - 1))
    assert errors[0] > 0 and errors[1] < errors[0] * 0.51


def test_new_dynamic_features_do_not_require_dna_reference_points():
    f = [11, 11, 11, 11, 11, 12, 15, 12, 10, 12, 12, 12, 12, 12]
    t = [i * 0.1 for i in range(len(f))]
    nodes = detect_dynamic_nodes(t, f, POLICY)
    kinds = {n["kind"] for n in nodes}
    assert {
        "local_maximum",
        "local_minimum",
        "rapid_transition",
        "abrupt_sample_change",
        "stable_region",
    } <= kinds
    assert all(n["status"] == "DER" and n["origin"] == "DYNAMIC" for n in nodes)
    assert any(n["f"] == 15 for n in nodes)
    assert not any("resonance" in n["kind"] for n in nodes)
    cubic_t = [i * 0.1 for i in range(-10, 11)]
    cubic_f = [20 + x**3 for x in cubic_t]
    assert any(
        n["kind"] == "inflexion_candidate" for n in detect_dynamic_nodes(cubic_t, cubic_f, POLICY)
    )
    peaks = detect_dynamic_nodes([0, 1, 2], [11, 12, 13], POLICY, [1, 5, 1])
    peak = next(n for n in peaks if n["kind"] == "resonance_like_response_peak")
    assert peak["interpretation_status"] == "HYP"


def test_opt_in_waveform_frequency_estimate_and_insufficient_data():
    t = [i * 0.001 for i in range(2001)]
    estimate = estimate_crossing_frequency(
        t, [math.sin(2 * math.pi * 4.321 * x) for x in t], crossing_level=0
    )
    assert estimate["frequencies_hz"] == pytest.approx(
        [4.321] * len(estimate["frequencies_hz"]), rel=1e-5
    )
    assert estimate["physical_interpretation"] == "STOP"
    with pytest.raises(ValueError):
        estimate_crossing_frequency([0, 1, 2], [1, 1, 1], crossing_level=0)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_values_rejected_at_each_entry(bad):
    with pytest.raises(ValueError):
        run([0, 0.1, 0.2], [1, bad, 2])
    with pytest.raises(ValueError):
        run([0, bad, 0.2], [1, 1, 2])
    with pytest.raises(ValueError):
        run([0, 0.1, 0.2], [1, 1, 2], initial_positions=((bad, 0, 0),))
    with pytest.raises(ValueError):
        run([0, 0.1, 0.2], [1, 1, 2], phase0_rad=bad)
    with pytest.raises(ValueError):
        navier_stokes_residual((bad, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), 1, 0)


@pytest.mark.parametrize(
    "times,f",
    [([0, 0, 1], [1, 2, 3]), ([0, 1], [1, 2]), ([0, 1, 2], [1, 0, 1]), ([0, 1, 2], [1, -1, 1])],
)
def test_invalid_sampling_and_domain(times, f):
    with pytest.raises(ValueError):
        run(times, f)


def test_extreme_finite_input_does_not_export_infinity():
    with pytest.raises(ValueError):
        frequency_state(5e-324)
    with pytest.raises(ValueError):
        run([0, 1, 2], [1e307] * 3)


def test_dna_dataset_and_dynamic_candidates_follow_existing_node_schema():
    payload = json.loads((ROOT / "examples/dynamics/frequency-series.json").read_bytes())
    reader = DNAReader(ROOT / "data")
    report = reader.analyze_dynamic(payload)
    assert report["state"] == "PASS"
    assert report["candidates"] and all(n["status"] == "DER" for n in report["candidates"])
    assert report["input_sha256"] and report["code_sha256"]["spiral_flow.py"]
    json.dumps(report, allow_nan=False)
    changed = deepcopy(payload)
    changed["input_kind"] = "unknown"
    with pytest.raises(ValueError):
        reader.analyze_dynamic(changed)


@pytest.mark.parametrize(
    "name",
    [
        "constant",
        "linear",
        "sinusoidal",
        "cross_TF1766",
        "cross_resonance_7.834125",
        "cross_gen_pulse_0.126s",
        "cross_target_8Hz",
    ],
)
def test_deterministic_control_matrix_and_visible_negative_residual(name):
    cases = runpy.run_path(str(ROOT / "examples/dynamics/run_controls.py"))["controls"]()
    reader = DNAReader(ROOT / "data")
    positive = reader.analyze_dynamic(cases[name + "__manufactured_rotation"])
    negative = reader.analyze_dynamic(cases[name + "__none"])
    assert positive["state"] == "PASS"
    assert negative["state"] == ("PASS" if name == "constant" else "STOP")
    assert all(row["kinematic_validation"] == "PASS" for row in negative["rows"])
    assert positive["frequency_estimation"] is None
    assert len(positive["rows"]) == len(cases[name + "__none"]["times_s"])
