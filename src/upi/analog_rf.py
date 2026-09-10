"""Protected continuous reference, sampled representation and bounded RF experiments.

ANGELICA/EMILIA are architecture aliases. Numerical models are not analog hardware.
No function in this module actuates a radio, valve, device or external capability.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import asdict, dataclass

from .constants import C
from .models import ScientificStatus
from .resilience import content_hash

ANALOG_FUNCTION_REQUIRED = True
OPTIMIZER_MAY_REMOVE_ANALOG = False
ALLOWED_ANALOG_ACTIONS = frozenset({"PRESERVE", "TEST", "ISOLATE", "COMPARE", "HUMAN_REVIEW"})
RF_BANDS = (450e6, 900e6, 2.4e9, 5e9, 6e9)


def finite(x: float, name: str, minimum: float | None = None) -> None:
    if isinstance(x, bool) or not math.isfinite(x) or (minimum is not None and x < minimum):
        raise ValueError(f"invalid {name}")


def positive(x: float, name: str) -> None:
    finite(x, name, 0)
    if x == 0:
        raise ValueError(f"{name} must be positive")


def optimizer_action(action: str) -> dict:
    if action not in ALLOWED_ANALOG_ACTIONS:
        raise ValueError("analog function is protected; removal is forbidden")
    return {
        "status": "DER",
        "action": action,
        "analog_function_required": True,
        "may_remove_analog": False,
    }


@dataclass(frozen=True)
class AnalogObservation:
    """Immutable raw sensor samples and context; never quantized on ingestion."""

    id: str
    values: tuple[complex, ...]
    times_s: tuple[float, ...]
    unit: str
    uncertainty: float | None
    provenance: tuple[str, ...]
    timestamp: str
    status: ScientificStatus
    domain: str
    physical_io: str | None = None
    representation: str = "simulation"

    def __post_init__(self) -> None:
        if not isinstance(self.provenance, tuple) or not all(
            isinstance(p, str) and p for p in self.provenance
        ):
            raise ValueError("immutable nonempty provenance required")
        if (
            not isinstance(self.values, tuple)
            or not isinstance(self.times_s, tuple)
            or not self.values
            or len(self.values) != len(self.times_s)
        ):
            raise ValueError("immutable paired samples required")
        if not all(
            (self.id, self.unit, self.provenance, self.timestamp, self.domain)
        ) or not isinstance(self.status, ScientificStatus):
            raise ValueError("observation context required")
        if self.representation not in ("simulation", "measurement") or (
            self.representation == "measurement" and not self.physical_io
        ):
            raise ValueError("measurement requires a named physical input")
        for v, t in zip(self.values, self.times_s, strict=True):
            finite(v.real, "real sample")
            finite(v.imag, "imaginary sample")
            finite(t, "time")
        if any(a >= b for a, b in zip(self.times_s, self.times_s[1:], strict=False)):
            raise ValueError("sample times must increase")
        if self.uncertainty is not None:
            finite(self.uncertainty, "uncertainty", 0)

    def record(self) -> dict:
        result = asdict(self)
        result["values"] = [{"real": v.real, "imag": v.imag} for v in self.values]
        result["raw_sha256"] = content_hash(result)
        return result


def compare_paths(
    analog: AnalogObservation,
    digital: tuple[complex, ...],
    *,
    tolerance: float,
    bandwidth_hz: float | None = None,
) -> dict:
    finite(tolerance, "comparison tolerance", 0)
    if not isinstance(digital, tuple) or len(digital) != len(analog.values):
        raise ValueError("paired immutable digital samples required")
    for v in digital:
        finite(v.real, "digital real")
        finite(v.imag, "digital imaginary")
    residuals = [abs(a - b) for a, b in zip(analog.values, digital, strict=True)]
    differences = [i for i, e in enumerate(residuals) if e > tolerance]
    sampling = None
    if bandwidth_hz is not None:
        positive(bandwidth_hz, "bandwidth")
        deltas = [b - a for a, b in zip(analog.times_s, analog.times_s[1:], strict=False)]
        sampling = (
            bool(deltas)
            and max(deltas) - min(deltas) < 1e-9 * max(deltas)
            and 1 / max(deltas) > 2 * bandwidth_hz
        )
    result = {
        "status": "DER",
        "verdict": "MISFIT" if differences else "CONSISTENT_AT_SAMPLES",
        "analog": analog.record(),
        "digital": [{"real": v.real, "imag": v.imag} for v in digital],
        "residuals": residuals,
        "misfit_indices": differences,
        "tolerance": tolerance,
        "nyquist_condition_met": sampling,
        "provenance": analog.provenance,
        "test_request": "Inspect phase, timing, bandwidth and calibration on an independent acquisition"
        if differences
        else "Test between samples; sample agreement does not establish path identity",
        "analog_function_required": True,
        "verification_type": "software_test",
    }
    if sampling is not True:
        result["reconstruction_boundary"] = {
            "status": "STOP",
            "stop_reason": "Bandlimited reconstruction conditions are absent or fail",
            "next_observation": "Provide bandwidth, uniform sample times and anti-alias filter response",
        }
    return result


def continuous_signal(t: float, frequency_hz: float, phase: float = 0.0) -> complex:
    finite(t, "time")
    positive(frequency_hz, "frequency")
    finite(phase, "phase")
    return cmath.exp(1j * (2 * math.pi * frequency_hz * t + phase))


def linear_reconstruct(times: tuple[float, ...], samples: tuple[complex, ...], t: float) -> complex:
    """Declared piecewise-linear interpolation, not exact bandlimited reconstruction."""
    if (
        len(times) < 2
        or len(times) != len(samples)
        or any(a >= b for a, b in zip(times, times[1:], strict=False))
    ):
        raise ValueError("increasing paired times required")
    finite(t, "reconstruction time")
    if not times[0] <= t <= times[-1]:
        raise ValueError("no extrapolation")
    for i in range(len(times) - 1):
        if t <= times[i + 1]:
            fraction = (t - times[i]) / (times[i + 1] - times[i])
            return samples[i] * (1 - fraction) + samples[i + 1] * fraction
    raise ValueError("outside interpolation domain")


def fspl(frequency_hz: float, distance_m: float) -> float:
    positive(frequency_hz, "frequency")
    positive(distance_m, "distance")
    if distance_m < C / frequency_hz:
        raise ValueError("distance below wavelength; far-field baseline not applicable")
    return 20 * math.log10(4 * math.pi * distance_m * frequency_hz / C)


def rf_band(
    frequency_hz: float,
    distance_m: float = 1000.0,
    control_hz: float = 8.0,
    modulation_index: float = 0.25,
) -> dict:
    positive(control_hz, "control frequency")
    finite(modulation_index, "modulation index", 0)
    if modulation_index > 1 or frequency_hz <= control_hz:
        raise ValueError("require ordinary AM 0<=m<=1 and carrier>control")
    return {
        "status": "DER",
        "frequency_Hz": frequency_hz,
        "wavelength_m": C / frequency_hz,
        "distance_m": distance_m,
        "midpoint_first_fresnel_radius_m": math.sqrt(C / frequency_hz * distance_m / 4),
        "fspl_dB": fspl(frequency_hz, distance_m),
        "sidebands": [
            {
                "status": "DER",
                "frequency_Hz": frequency_hz - control_hz,
                "relative_amplitude": modulation_index / 2,
            },
            {"status": "DER", "frequency_Hz": frequency_hz, "relative_amplitude": 1.0},
            {
                "status": "DER",
                "frequency_Hz": frequency_hz + control_hz,
                "relative_amplitude": modulation_index / 2,
            },
        ],
        "assumptions": [
            "vacuum free-space far field; antenna far-field distance still requires aperture dimensions",
            "ideal linear AM; common control phase does not imply common carrier phase",
        ],
        "propagation_boundary": {
            "status": "STOP",
            "stop_reason": "Terrain, antenna pattern, polarization, buildings and atmospheric observations absent",
            "next_observation": "Supply path geometry, antenna data and calibrated propagation measurements",
        },
    }


def complex_record(z: complex) -> dict:
    return {"real": z.real, "imag": z.imag}


def gamma_z(z: complex) -> complex:
    finite(z.real, "impedance real")
    finite(z.imag, "impedance imag")
    if abs(z + 1) < 1e-14:
        raise ValueError("reflection pole at z=-1")
    return (z - 1) / (z + 1)


def z_gamma(gamma: complex) -> complex:
    finite(gamma.real, "reflection real")
    finite(gamma.imag, "reflection imag")
    if abs(1 - gamma) < 1e-14:
        raise ValueError("open-circuit inverse is an infinite-impedance limit")
    return (1 + gamma) / (1 - gamma)


def gamma_admittance(y_normalized: complex) -> complex:
    """Physical reflection of the same load: (1-y)/(1+y), not gamma_z(y)."""
    return -gamma_z(y_normalized)


def propagate(gamma: complex, distance_m: float, wavelength_g_m: float) -> complex:
    positive(wavelength_g_m, "guided wavelength")
    finite(distance_m, "line coordinate")
    return gamma * cmath.exp(-4j * math.pi * distance_m / wavelength_g_m)


def propagation_lift(gamma: complex, wavelength_g_m: float) -> dict:
    """Representation dimensions only; no physical torus or extra dimensions."""
    positive(wavelength_g_m, "guided wavelength")
    samples = []
    for i in range(33):
        distance = wavelength_g_m * i / 32
        g = propagate(gamma, distance, wavelength_g_m)
        samples.append(
            {
                "status": "DER",
                "distance_m": distance,
                "Re_Gamma": g.real,
                "Im_Gamma": g.imag,
                "V_plus_V": [1.0, 0.0],
                "V_minus_V": [g.real, g.imag],
            }
        )
    return {
        "status": "DER",
        "coordinates": {
            "1D": "line coordinate z [m]",
            "2D": "complex Gamma [1]",
            "3D": "Re Gamma, Im Gamma, z; geometric helix",
            "4D": "Re/Im V+, Re/Im V- in volts; C^2 representation",
        },
        "samples": samples,
        "assumptions": ["lossless line, Gamma_L supplied, V+=1 V reference"],
        "higher_dimensions": {
            "status": "HYP",
            "state": "OPEN",
            "claim": "physical torus / 5D-11D / M-theory identification",
            "next_observation": "Identify independent physical degrees of freedom and a sourced transformation",
        },
    }


@dataclass(frozen=True)
class StubModel:
    frequency_hz: float = 900e6
    z0_ohm: float = 50.0
    velocity_factor: float = 0.66
    length_m: float = 0.027480975316666666  # nominal guided lambda/8 at 900 MHz
    q: float | None = None
    conductor_np_m: float = 0.0
    dielectric_np_m: float = 0.0
    connector_r_ohm: float = 0.0
    connector_l_h: float = 0.0
    junction_c_f: float = 0.0
    dispersion_per_fraction: float = 0.0
    reference_hz: float = 900e6
    temperature_c: float = 20.0
    length_temp_coefficient: float = 0.0

    def __post_init__(self) -> None:
        for name in ("frequency_hz", "z0_ohm", "velocity_factor", "length_m", "reference_hz"):
            positive(getattr(self, name), name)
        if self.velocity_factor > 1:
            raise ValueError("velocity factor must be <=1 in this model")
        for name in (
            "conductor_np_m",
            "dielectric_np_m",
            "connector_r_ohm",
            "connector_l_h",
            "junction_c_f",
        ):
            finite(getattr(self, name), name, 0)
        for name in ("dispersion_per_fraction", "temperature_c", "length_temp_coefficient"):
            finite(getattr(self, name), name)
        if self.q is not None:
            positive(self.q, "Q")

    def admittance(self) -> complex:
        fraction = self.frequency_hz / self.reference_hz - 1
        vf = self.velocity_factor * (1 + self.dispersion_per_fraction * fraction)
        length = self.length_m * (1 + self.length_temp_coefficient * (self.temperature_c - 20))
        if not 0 < vf <= 1 or length <= 0:
            raise ValueError("dispersion/temperature outside model domain")
        beta = 2 * math.pi * self.frequency_hz / (C * vf)
        attenuation = (
            self.conductor_np_m
            + self.dielectric_np_m
            + (0 if self.q is None else beta / (2 * self.q))
        )
        z = self.z0_ohm * cmath.tanh(complex(attenuation, beta) * length)
        z += self.connector_r_ohm + 2j * math.pi * self.frequency_hz * self.connector_l_h
        if abs(z) < 1e-12:
            raise ValueError("stub admittance pole; use a limit or lossy model")
        return 1 / z + 2j * math.pi * self.frequency_hz * self.junction_c_f


def mirror_experiment(
    model: StubModel,
    alpha: float,
    *,
    load_y_s: complex = 0.02 + 0j,
    amplitude: float = 1.0,
    phase_rad: float = 0.0,
    delta_g_s: float = 0.0,
    delta_b_s: float = 0.0,
) -> dict:
    for name, value in (
        ("alpha", alpha),
        ("amplitude", amplitude),
        ("phase", phase_rad),
        ("delta G", delta_g_s),
        ("delta B", delta_b_s),
    ):
        finite(value, name)
    finite(load_y_s.real, "load G")
    finite(load_y_s.imag, "load B")
    actual = model.admittance()
    # Mirror tracks the ideal design stub; real discrepancies remain observable.
    ideal = StubModel(
        model.frequency_hz, model.z0_ohm, model.velocity_factor, model.length_m
    ).admittance()
    mirror = -alpha * amplitude * ideal * cmath.exp(1j * phase_rad) + complex(delta_g_s, delta_b_s)
    total = load_y_s + actual + mirror
    gamma = gamma_admittance(total * model.z0_ohm)
    magnitude = abs(gamma)
    return {
        "status": "DER",
        "verification_type": "simulation",
        "model": asdict(model),
        "alpha": alpha,
        "stub_Y_S": complex_record(actual),
        "mirror_Y_S": complex_record(mirror),
        "load_Y_S": complex_record(load_y_s),
        "total_Y_S": complex_record(total),
        "Gamma": complex_record(gamma),
        "S11": complex_record(gamma),
        "magnitude": magnitude,
        "phase_rad": cmath.phase(gamma),
        "VSWR": (1 + magnitude) / (1 - magnitude) if magnitude < 1 else None,
        "passive_reflection_domain": magnitude <= 1,
        "hardware_boundary": {
            "status": "STOP",
            "stop_reason": "No measured circuit or active-element stability model",
            "next_observation": "Calibrated complex S11 frequency/alpha sweeps, repeatability, null control and stability characterization",
        },
    }
