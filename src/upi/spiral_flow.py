"""Dynamic spiral-flow helpers for reproducible UPI simulations.

This module keeps the declared frequency signal separate from any fluid-model
assumptions. It provides exact kinematic relations and a rigid-vortex control
field, plus a mode switch for velocity, vorticity, and a Navier-Stokes
residual. It does not claim to solve the full 3-D Navier-Stokes existence
problem.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Any

from .physics import (
    angular_frequency,
    energy_from_frequency,
    mass_from_frequency,
    period_from_frequency,
)


class NavierMode(str, Enum):
    """Analysis mode sharing one underlying state."""

    VELOCITY = "velocity_field"
    VORTICITY = "vorticity_curl"
    NAVIER_STOKES_RESIDUAL = "navier_stokes_residual"


@dataclass(frozen=True)
class FrequencyState:
    """One verified point in a frequency trajectory."""

    frequency_hz: float
    period_s: float
    angular_frequency_rad_s: float
    energy_j: float
    mass_equivalent_kg: float


@dataclass(frozen=True)
class DynamicPoint:
    """A frequency-derived diagnostic point."""

    label: str
    frequency_hz: float
    period_s: float
    period_error_s: float


def frequency_state(frequency_hz: float) -> FrequencyState:
    """Return T=1/f, omega=2*pi*f, E=h*f and E/c^2."""
    if not math.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be finite and positive")
    period = period_from_frequency(frequency_hz)
    angular = angular_frequency(frequency_hz)
    energy = energy_from_frequency(frequency_hz)
    mass = mass_from_frequency(frequency_hz)
    if not all(math.isfinite(v) and v > 0 for v in (period, angular, energy, mass)):
        raise ValueError("frequency state exceeds floating-point range")
    return FrequencyState(frequency_hz, period, angular, energy, mass)


def integrate_phase(frequencies_hz: list[float], dt_s: float) -> list[float]:
    """Integrate phase with phi[n]=phi[n-1]+2*pi*f[n]*dt."""
    if not math.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("dt_s must be finite and positive")
    if not frequencies_hz:
        return []
    if any(not math.isfinite(f) or f <= 0 for f in frequencies_hz):
        raise ValueError("all frequencies must be finite and positive")
    phase = [0.0]
    for frequency in frequencies_hz[1:]:
        phase.append(_finite(phase[-1] + angular_frequency(frequency) * dt_s, "phase"))
    return phase


def dynamic_reference_points() -> tuple[DynamicPoint, ...]:
    """Return model reference points without conflating 0.126 s and 7.834125 Hz."""
    resonance = frequency_state(7.834125)
    pulse_period = 0.126
    pulse_frequency = 1.0 / pulse_period
    return (
        DynamicPoint("TF1766", 1.766, 1.0 / 1.766, 0.0),
        DynamicPoint("resonance_7.834125", 7.834125, resonance.period_s, 0.0),
        DynamicPoint(
            "gen_pulse_0.126s",
            pulse_frequency,
            pulse_period,
            pulse_period - resonance.period_s,
        ),
        DynamicPoint("target_8Hz", 8.0, 0.125, 0.0),
    )


def rigid_vortex_velocity(x: float, y: float, frequency_hz: float) -> tuple[float, float, float]:
    """Rigid rotation control field v=(-omega*y, omega*x, 0)."""
    state = frequency_state(frequency_hz)
    _finite(x, "x")
    _finite(y, "y")
    return _vector((-state.angular_frequency_rad_s * y, state.angular_frequency_rad_s * x, 0.0))


def rigid_vortex_curl(frequency_hz: float) -> tuple[float, float, float]:
    """Exact curl of the rigid-vortex control field."""
    state = frequency_state(frequency_hz)
    return _vector((0.0, 0.0, 2.0 * state.angular_frequency_rad_s))


def navier_stokes_residual(
    dt_velocity: tuple[float, float, float],
    convective: tuple[float, float, float],
    pressure_gradient: tuple[float, float, float],
    laplacian_velocity: tuple[float, float, float],
    density: float,
    viscosity: float,
    force: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> tuple[float, float, float]:
    """Return LHS-RHS residual for the declared incompressible NS equation."""
    if not math.isfinite(density) or density <= 0:
        raise ValueError("density must be finite and positive")
    if not math.isfinite(viscosity) or viscosity < 0:
        raise ValueError("viscosity must be finite and non-negative")
    for vector in (dt_velocity, convective, pressure_gradient, laplacian_velocity, force):
        _vector(vector)
    return _vector(
        tuple(
            dt_velocity[i]
            + convective[i]
            + pressure_gradient[i] / density
            - viscosity * laplacian_velocity[i]
            - force[i]
            for i in range(3)
        )
    )


def select_mode(step: int, cycle: tuple[NavierMode, ...] | None = None) -> NavierMode:
    """Cycle analysis modes without resetting the shared simulation state."""
    modes = tuple(NavierMode) if cycle is None else cycle
    if not modes:
        raise ValueError("cycle must contain at least one mode")
    if step < 0:
        raise ValueError("step must be non-negative")
    return modes[step % len(modes)]


Vector = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _vector(values: tuple[float, ...]) -> Vector:
    if len(values) != 3:
        raise ValueError("Expected three vector components")
    return (
        _finite(values[0], "vector"),
        _finite(values[1], "vector"),
        _finite(values[2], "vector"),
    )


def _series(times_s: list[float], values: list[float], minimum: int = 3) -> None:
    if len(times_s) != len(values) or len(values) < minimum:
        raise ValueError(f"Series requires matching arrays with at least {minimum} samples")
    for t, value in zip(times_s, values, strict=True):
        _finite(t, "time")
        _finite(value, "sample")
    if any(b <= a for a, b in zip(times_s, times_s[1:], strict=False)):
        raise ValueError("Times must be strictly increasing")


def differentiate(times_s: list[float], values: list[float]) -> list[float]:
    """Three-point nonuniform interior derivative; one-sided endpoints.

    This is a numerical estimate, including at discontinuities; no smoothness claim.
    """
    _series(times_s, values)
    slopes = [
        (b - a) / (tb - ta)
        for ta, tb, a, b in zip(times_s, times_s[1:], values, values[1:], strict=False)
    ]
    result = [slopes[0]]
    for i in range(1, len(values) - 1):
        left, right = times_s[i] - times_s[i - 1], times_s[i + 1] - times_s[i]
        result.append((right * slopes[i - 1] + left * slopes[i]) / (left + right))
    result.append(slopes[-1])
    return [_finite(v, "derivative") for v in result]


def integrate_phase_samples(
    times_s: list[float], frequencies_hz: list[float], phase0_rad: float
) -> list[float]:
    """Right-endpoint quadrature as requested: phi[n]=phi[n-1]+omega[n]*dt[n]."""
    _series(times_s, frequencies_hz)
    phase = [_finite(phase0_rad, "phase origin")]
    for f in frequencies_hz:
        frequency_state(f)
    for n in range(1, len(times_s)):
        phase.append(
            _finite(
                phase[-1] + angular_frequency(frequencies_hz[n]) * (times_s[n] - times_s[n - 1]),
                "integrated phase",
            )
        )
    return phase


def interpolate_frequency(
    times_s: list[float], frequencies_hz: list[float], time_s: float
) -> float:
    """Explicit piecewise-linear interpolation model; no extrapolation or smoothing."""
    _series(times_s, frequencies_hz)
    _finite(time_s, "query time")
    for f in frequencies_hz:
        frequency_state(f)
    if time_s < times_s[0] or time_s > times_s[-1]:
        raise ValueError("Interpolation outside supplied interval")
    for n in range(1, len(times_s)):
        if time_s <= times_s[n]:
            fraction = (time_s - times_s[n - 1]) / (times_s[n] - times_s[n - 1])
            return frequencies_hz[n - 1] + fraction * (frequencies_hz[n] - frequencies_hz[n - 1])
    return frequencies_hz[-1]


def estimate_crossing_frequency(
    times_s: list[float], amplitudes: list[float], *, crossing_level: float
) -> dict[str, Any]:
    """Opt-in cycle-average estimator for one oscillation with one upward crossing/cycle.

    Caller must justify that model and anti-alias filtering. Never a unique physical
    interpretation of an arbitrary waveform, nor a spectral resonance detector.
    """
    _series(times_s, amplitudes)
    _finite(crossing_level, "crossing level")
    crossings = []
    for i in range(1, len(times_s)):
        a, b = amplitudes[i - 1] - crossing_level, amplitudes[i] - crossing_level
        if a < 0 <= b:
            crossings.append(times_s[i - 1] - a * (times_s[i] - times_s[i - 1]) / (b - a))
    if len(crossings) < 4:
        raise ValueError("STOP: need four upward crossings for three frequency estimates")
    return {
        "times_s": [(a + b) / 2 for a, b in zip(crossings, crossings[1:], strict=False)],
        "frequencies_hz": [
            _finite(1 / (b - a), "cycle frequency")
            for a, b in zip(crossings, crossings[1:], strict=False)
        ],
        "status": "DER",
        "origin": "DYNAMIC",
        "method": "upward_crossing_cycle_average",
        "assumptions": [
            "One upward threshold crossing per physical cycle",
            "Linear crossing-time interpolation; caller supplies threshold",
        ],
        "physical_interpretation": "STOP",
        "stop_reason": "Single-component interpretation and anti-alias provenance need evidence",
    }


@dataclass(frozen=True)
class DetectionPolicy:
    rapid_rate_hz_s: float
    stable_rate_hz_s: float
    jump_hz: float
    response_prominence: float
    stable_min_samples: int = 3

    def __post_init__(self) -> None:
        for value in (
            self.rapid_rate_hz_s,
            self.stable_rate_hz_s,
            self.jump_hz,
            self.response_prominence,
        ):
            if _finite(value, "detection threshold") < 0:
                raise ValueError("Detection thresholds must be nonnegative")
        if (
            self.rapid_rate_hz_s <= self.stable_rate_hz_s
            or self.jump_hz == 0
            or self.stable_min_samples < 2
        ):
            raise ValueError("Invalid detection policy")


def detect_dynamic_nodes(
    times_s: list[float],
    frequencies_hz: list[float],
    policy: DetectionPolicy,
    response_amplitudes: list[float] | None = None,
) -> list[dict[str, Any]]:
    """Detect sample-local features, independent of every stored reference frequency."""
    _series(times_s, frequencies_hz)
    for f in frequencies_hz:
        frequency_state(f)
    if response_amplitudes is not None:
        _series(times_s, response_amplitudes)
    rate = differentiate(times_s, frequencies_hz)
    curvature = differentiate(times_s, rate)
    nodes: list[dict[str, Any]] = []

    def add(kind: str, index: int, **metadata: Any) -> None:
        nodes.append(
            {
                "kind": kind,
                "index": index,
                "t": times_s[index],
                "f": frequencies_hz[index],
                "status": "DER",
                "origin": "DYNAMIC",
                "verification_type": "software_test",
                **metadata,
            }
        )

    for i in range(1, len(times_s) - 1):
        before, value, after = frequencies_hz[i - 1 : i + 2]
        if value > before and value > after:
            add("local_maximum", i)
        if value < before and value < after:
            add("local_minimum", i)
        if response_amplitudes is not None:
            a, b, c = response_amplitudes[i - 1 : i + 2]
            if b > max(a, c) and b - max(a, c) >= policy.response_prominence:
                add(
                    "resonance_like_response_peak",
                    i,
                    interpretation_status="HYP",
                    stop_reason="Response peak is not proof of resonance; transfer function and controls required",
                )
    last_sign, last_index = 0, 0
    for i, value in enumerate(curvature):
        sign = 1 if value > 0 else -1 if value < 0 else 0
        if sign and last_sign and sign != last_sign:
            add(
                "inflexion_candidate",
                (last_index + i) // 2,
                method="sign change in finite-difference curvature",
            )
        if sign:
            last_sign, last_index = sign, i
    for i in range(1, len(times_s)):
        delta = frequencies_hz[i] - frequencies_hz[i - 1]
        slope = delta / (times_s[i] - times_s[i - 1])
        if abs(slope) >= policy.rapid_rate_hz_s:
            add("rapid_transition", i, rate_hz_s=slope)
        if abs(delta) >= policy.jump_hz:
            add("abrupt_sample_change", i, delta_hz=delta)
    start = None
    for i in range(len(rate) + 1):
        stable = i < len(rate) and abs(rate[i]) <= policy.stable_rate_hz_s
        if stable and start is None:
            start = i
        elif not stable and start is not None:
            if i - start >= policy.stable_min_samples:
                add("stable_region", start, end_index=i - 1, end_t=times_s[i - 1])
            start = None
    return nodes


@dataclass(frozen=True)
class SimulationState:
    """One immutable physical state; changing its view never advances its clock."""

    index: int
    t: float
    f: float
    omega: float
    phi: float
    positions: tuple[Vector, ...]
    mode: NavierMode = NavierMode.VELOCITY

    def with_mode(self, mode: NavierMode) -> SimulationState:
        return replace(self, mode=NavierMode(mode))


def rotation_terms(
    position: Vector,
    frequency_hz: float,
    df_dt_hz_s: float,
    density: float,
    viscosity: float,
    *,
    force: Vector,
) -> dict[str, Any]:
    """Analytic spatial terms of the explicit unsteady rigid-rotation control field.

    p-p0=rho*omega(t)^2*(x²+y²)/2 is a declared manufactured pressure, not measured.
    force is acceleration [m/s²]; it is never inferred silently to cancel residuals.
    """
    x, y, _ = _vector(position)
    omega = angular_frequency(frequency_hz)
    omega_squared = _finite(omega * omega, "squared angular frequency")
    alpha = _finite(math.tau * df_dt_hz_s, "angular acceleration")
    velocity = rigid_vortex_velocity(x, y, frequency_hz)
    dt_velocity = _vector((-alpha * y, alpha * x, 0.0))
    convective = _vector((-omega_squared * x, -omega_squared * y, 0.0))
    gradient = _vector((density * omega_squared * x, density * omega_squared * y, 0.0))
    laplacian = (0.0, 0.0, 0.0)
    residual = navier_stokes_residual(
        dt_velocity, convective, gradient, laplacian, density, viscosity, force
    )
    curl = rigid_vortex_curl(frequency_hz)
    return {
        "velocity": velocity,
        "speed": math.hypot(*velocity),
        "curl": curl,
        "curl_magnitude": math.hypot(*curl),
        "divergence": 0.0,
        "dt_velocity": dt_velocity,
        "convective": convective,
        "laplacian_velocity": laplacian,
        "pressure_gradient": gradient,
        "pressure": _finite(density * omega_squared * (x * x + y * y) / 2, "pressure"),
        "force": _vector(force),
        "residual": residual,
        "residual_norm": math.hypot(*residual),
    }


def advance_particles(state: SimulationState, next_t: float, next_f: float) -> SimulationState:
    """Explicit Euler at the old velocity; right-endpoint phase at the new frequency."""
    dt = _finite(next_t - state.t, "dt")
    if dt <= 0:
        raise ValueError("Particle step must advance time")
    frequency_state(next_f)
    positions = []
    for point in state.positions:
        velocity = rigid_vortex_velocity(point[0], point[1], state.f)
        positions.append(_vector(tuple(x + v * dt for x, v in zip(point, velocity, strict=True))))
    return SimulationState(
        state.index + 1,
        next_t,
        next_f,
        angular_frequency(next_f),
        _finite(state.phi + angular_frequency(next_f) * dt, "phase"),
        tuple(positions),
        state.mode,
    )


def run_dynamic_series(
    times_s: list[float],
    frequencies_hz: list[float],
    *,
    initial_positions: tuple[Vector, ...],
    phase0_rad: float,
    density: float,
    viscosity: float,
    force_mode: str,
    detection: DetectionPolicy,
    residual_tolerance: float,
    modes: tuple[NavierMode, ...] = tuple(NavierMode),
    response_amplitudes: list[float] | None = None,
) -> dict[str, Any]:
    """Central data->derivatives->field->residual->Euler->feature verification loop.

    force_mode must explicitly select 'none' or 'manufactured_rotation'. The latter
    supplies F=(-alpha*y,alpha*x,0) solely as a manufactured residual control.
    """
    if force_mode not in {"none", "manufactured_rotation"}:
        raise ValueError("Explicit force_mode required: none or manufactured_rotation")
    if not initial_positions or not modes:
        raise ValueError("Positions and mode cycle must not be empty")
    if _finite(residual_tolerance, "residual tolerance") < 0:
        raise ValueError("Negative residual tolerance")
    phases = integrate_phase_samples(times_s, frequencies_hz, phase0_rad)
    rates = differentiate(times_s, frequencies_hz)
    state = SimulationState(
        0,
        times_s[0],
        frequencies_hz[0],
        angular_frequency(frequencies_hz[0]),
        phases[0],
        tuple(_vector(p) for p in initial_positions),
    )
    rows = []
    for n, (time, frequency) in enumerate(zip(times_s, frequencies_hz, strict=True)):
        previous = state
        if n:
            state = advance_particles(state, time, frequency)
        before_mode = asdict(state)
        state = state.with_mode(select_mode(n, modes))
        after_mode = asdict(state)
        before_mode.pop("mode")
        after_mode.pop("mode")
        alpha = math.tau * rates[n]
        fields = []
        for point in state.positions:
            force = (
                (-alpha * point[1], alpha * point[0], 0.0)
                if force_mode == "manufactured_rotation"
                else (0.0, 0.0, 0.0)
            )
            fields.append(
                rotation_terms(point, frequency, rates[n], density, viscosity, force=force)
            )
        first = fields[0]
        residual_pass = all(f["residual_norm"] <= residual_tolerance for f in fields)
        kinematic_pass = (
            state.phi == phases[n]
            and before_mode == after_mode
            and math.isclose(period_from_frequency(frequency) * frequency, 1, rel_tol=1e-12)
            and all(
                math.isclose(f["curl_magnitude"], 2 * state.omega, rel_tol=1e-12)
                and f["divergence"] == 0
                for f in fields
            )
        )
        if n:
            for old, new in zip(previous.positions, state.positions, strict=True):
                v = rigid_vortex_velocity(old[0], old[1], previous.f)
                expected = tuple(
                    x + speed * (time - previous.t) for x, speed in zip(old, v, strict=True)
                )
                kinematic_pass &= new == expected
        rows.append(
            {
                "t": time,
                "f": frequency,
                "T": period_from_frequency(frequency),
                "omega": state.omega,
                "df_dt": rates[n],
                "domega_dt": alpha,
                "phi": state.phi,
                "vx": first["velocity"][0],
                "vy": first["velocity"][1],
                "vz": first["velocity"][2],
                "speed": first["speed"],
                "curl_x": first["curl"][0],
                "curl_y": first["curl"][1],
                "curl_z": first["curl"][2],
                "curl_magnitude": first["curl_magnitude"],
                "divergence": first["divergence"],
                "pressure": first["pressure"],
                "particle_positions": state.positions,
                "particle_fields": fields,
                "navier_mode": state.mode.value,
                "kinematic_validation": "PASS" if kinematic_pass else "FAIL",
                "residual_validation": "PASS" if residual_pass else "FAIL",
                "validation_status": "PASS" if kinematic_pass and residual_pass else "FAIL",
                "status": "DER",
                "origin": "DYNAMIC",
            }
        )
    passed = all(row["validation_status"] == "PASS" for row in rows)
    resonance = frequency_state(7.834125).period_s
    return {
        "operation": "upi_dynamic_spiral_flow",
        "state": "PASS" if passed else "STOP",
        "promotion": "BLOCKED",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "units": {
            "t": "s",
            "f": "Hz",
            "T": "s",
            "omega": "rad/s",
            "df_dt": "Hz/s",
            "domega_dt": "rad/s^2",
            "phi": "rad",
            "velocity": "m/s",
            "speed": "m/s",
            "curl": "s^-1",
            "divergence": "s^-1",
            "pressure": "Pa",
            "particle_positions": "m",
            "dt_velocity": "m/s^2",
            "convective": "m/s^2",
            "laplacian_velocity": "1/(m*s)",
            "pressure_gradient": "Pa/m",
            "force": "m/s^2",
            "residual": "m/s^2",
        },
        "analysis_layers": {
            "spatial_control": "analytic_identity",
            "frequency_derivatives_phase_particles": "numerical_approximation",
            "full_navier_stokes_solution": "NOT_IMPLEMENTED",
        },
        "rows": rows,
        "dynamic_nodes": detect_dynamic_nodes(
            times_s, frequencies_hz, detection, response_amplitudes
        ),
        "references": [asdict(point) for point in dynamic_reference_points()],
        "reference_difference": {
            "delta_T_s": 0.126 - resonance,
            "relative_to_resonance_period": (0.126 - resonance) / resonance,
        },
        "methods": {
            "phase": "right_endpoint_quadrature",
            "particles": "explicit_euler_old_velocity",
            "derivatives": "three_point_interior_one_sided_endpoints",
            "force": force_mode,
            "field": "analytic_rigid_rotation_control",
            "pressure_origin_pa": 0,
            "navier_stokes_solver": False,
            "detection": asdict(detection),
        },
        "stop_reason": None if passed else "Kinematic or declared-force residual check failed",
        "next_action": "Inspect failed timesteps and supplied forcing; do not fit force to claim physical evidence",
        "limitations": [
            "Euler introduces radial drift; numerical convergence must be assessed",
            "Finite samples do not uniquely determine a continuous signal or physical mechanism",
            "Response peaks require controls before a physical resonance claim",
        ],
    }
