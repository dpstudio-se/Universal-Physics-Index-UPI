"""Physics functions implementing core UPI equations."""

import math
from typing import cast

from .constants import (
    AMPLITUDE_TOLERANCE_DEFAULT,
    EPSILON_Z_DEFAULT,
    N8_DENOMINATOR,
    PHASE_TOLERANCE_DEFAULT,
    C,
    H,
)
from .models import RuntimeMatchResult


def _finite_nonnegative(value: float, name: str) -> float:
    """Return a finite non-negative value or raise a stable input error."""
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def energy_from_frequency(frequency_hz: float) -> float:
    """Calculate energy from frequency using E = h*f.

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Energy in Joules

    Raises:
        ValueError: If frequency is invalid (NaN, zero, negative, infinity)
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz <= 0:
        raise ValueError(f"Frequency must be positive, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return H * frequency_hz


def mass_from_frequency(frequency_hz: float) -> float:
    """Calculate the energy mass equivalent from frequency using m = h*f / c^2.

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Mass equivalent in kilograms

    Raises:
        ValueError: If frequency is invalid
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz <= 0:
        raise ValueError(f"Frequency must be positive, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return (H * frequency_hz) / (C ** 2)


def frequency_from_mass(mass_kg: float) -> float:
    """Calculate the equivalent frequency from mass using f = m*c^2 / h.

    Args:
        mass_kg: Mass equivalent in kilograms

    Returns:
        Equivalent frequency in Hertz

    Raises:
        ValueError: If mass is invalid
    """
    if mass_kg != mass_kg:  # NaN
        raise ValueError("Mass is NaN")
    if mass_kg <= 0:
        raise ValueError(f"Mass must be positive, got {mass_kg}")
    if not (-1e308 < mass_kg < 1e308):
        raise ValueError(f"Mass is infinite or out of bounds: {mass_kg}")
    return (mass_kg * C ** 2) / H


def index8_from_frequency(frequency_hz: float) -> float:
    """Calculate 8 Hz dimensionless index N8 = f / (8 Hz).

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Dimensionless index N8

    Raises:
        ValueError: If frequency is invalid
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz < 0:
        raise ValueError(f"Frequency cannot be negative, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return frequency_hz / N8_DENOMINATOR


def spiral_time_from_frequency(
    frequency_hz: float,
    reference_frequency_hz: float = 0.1,
    reference_time_gyr: float = 10.8,
) -> float:
    """Map frequency to the Spiral Flow model's inverse-frequency time coordinate.

    This is a model transformation, not the physical period T = 1/f and not an
    established cosmological law. It implements t(f) = t_ref * f_ref / f.

    Args:
        frequency_hz: Frequency in Hertz.
        reference_frequency_hz: Model reference frequency in Hertz.
        reference_time_gyr: Model time assigned to the reference frequency, in Gyr.

    Returns:
        Model time coordinate in Gyr.
    """
    if not math.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be finite and positive")
    if not math.isfinite(reference_frequency_hz) or reference_frequency_hz <= 0:
        raise ValueError("reference_frequency_hz must be finite and positive")
    if not math.isfinite(reference_time_gyr) or reference_time_gyr <= 0:
        raise ValueError("reference_time_gyr must be finite and positive")
    result = reference_time_gyr * (reference_frequency_hz / frequency_hz)
    return _positive_finite(result, "model time (floating-point range)")


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def period_from_frequency(frequency_hz: float) -> float:
    """Physical period in seconds; never the Spiral Flow model coordinate."""
    return _positive_finite(1 / _positive_finite(frequency_hz, "frequency"), "period")


def angular_frequency(frequency_hz: float) -> float:
    """Ordinary frequency Hz to angular frequency rad/s."""
    return _positive_finite(math.tau * _positive_finite(frequency_hz, "frequency"), "omega")


def phase_from_frequency(frequency_hz: float, time_s: float, phase0_rad: float = 0) -> float:
    """Unwrapped phase; an absolute phase requires a declared time origin."""
    if not math.isfinite(time_s) or not math.isfinite(phase0_rad):
        raise ValueError("time and phase origin must be finite")
    result = angular_frequency(frequency_hz) * time_s + phase0_rad
    if not math.isfinite(result):
        raise ValueError("phase exceeds floating-point range")
    return result


def frequency_chamber(frequency_hz: float) -> dict[str, float | int | str]:
    """SYM partition: left-closed/right-open, except the final endpoint 8 Hz."""
    _positive_finite(frequency_hz, "frequency")
    edges = (0.1, 0.5, 2.0, 5.0, 7.0, 8.0)
    for index, (lower, upper) in enumerate(zip(edges, edges[1:], strict=False)):
        if lower <= frequency_hz < upper or (index == 4 and frequency_hz == upper):
            return {"chamber": f"C{index + 1}", "index": index,
                    "lower_hz": lower, "upper_hz": upper,
                    "phase_deg": index * (360 / 5), "status": "SYM"}
    raise ValueError("frequency outside declared chamber domain [0.1, 8] Hz")


def reduced_rotation(
    frequency_hz: float, x_m: float, y_m: float, density_kg_m3: float
) -> dict[str, float | str]:
    """REDUCED MODEL: steady rigid rotation v=(-Omega*y, Omega*x, 0).

    Caller explicitly prescribes fluid angular speed Omega=2*pi*f. A cylinder
    of declared radius R must impose rotating-wall velocity Omega*R; pressure
    p-p0=rho*Omega**2*r**2/2 balances centripetal acceleration. Uniform density,
    incompressible Newtonian fluid, steady state, no axial flow or body forcing.
    This analytic local field is not a PDE solver or a TF1766 coupling mechanism.
    """
    omega = angular_frequency(frequency_hz)
    _positive_finite(density_kg_m3, "density")
    if not math.isfinite(x_m) or not math.isfinite(y_m):
        raise ValueError("coordinates must be finite")
    result: dict[str, float | str] = {
        "model": "REDUCED MODEL", "status": "DER",
        "vx_m_s": -omega * y_m, "vy_m_s": omega * x_m,
        "vorticity_z_s_inverse": 2 * omega, "divergence_s_inverse": 0.0,
        "pressure_above_axis_pa": density_kg_m3 * omega**2 * (x_m**2 + y_m**2) / 2,
        "ax_m_s2": -omega**2 * x_m, "ay_m_s2": -omega**2 * y_m,
    }
    if any(not math.isfinite(v) for v in result.values() if isinstance(v, float)):
        raise ValueError("rotation exceeds floating-point range")
    return result


def normalize_value(value: float, reference: float) -> float:
    """Return Z = value/reference for finite values and a non-zero reference."""
    finite_value = _finite_nonnegative(value, "value")
    finite_reference = _finite_nonnegative(reference, "reference")
    if finite_reference == 0:
        raise ZeroDivisionError("reference must not be zero")
    return finite_value / finite_reference


def normalized_match(value: float, reference: float, tolerance: float = 1e-9) -> bool:
    """Compare a normalized value with one; this is not evidence of physical identity."""
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")
    return abs(normalize_value(value, reference) - 1.0) <= tolerance


def propagated_mass_uncertainty(frequency_uncertainty_hz: float) -> float:
    """Propagate frequency standard uncertainty through m = h f / c².

    In SI, h and c are exact; this function assumes frequency is the only uncertain input.
    """
    return mass_from_frequency(frequency_uncertainty_hz)


def index8_from_mass(mass_kg: float) -> float:
    """Calculate 8 Hz dimensionless index N8 = m*c^2 / (8*h).

    Args:
        mass_kg: Mass equivalent in kilograms

    Returns:
        Dimensionless index N8

    Raises:
        ValueError: If mass is invalid
    """
    if mass_kg != mass_kg:  # NaN
        raise ValueError("Mass is NaN")
    if mass_kg < 0:
        raise ValueError(f"Mass cannot be negative, got {mass_kg}")
    if not (-1e308 < mass_kg < 1e308):
        raise ValueError(f"Mass is infinite or out of bounds: {mass_kg}")
    return (mass_kg * C ** 2) / (N8_DENOMINATOR * H)


def relativistic_total_frequency(
    momentum_wavelength_m: float,
    rest_mass_frequency_hz: float
) -> float:
    """Calculate total temporal frequency using nu^2 = (c/lambda)^2 + f^2.

    Args:
        momentum_wavelength_m: Momentum wavelength (de Broglie wavelength) in meters
        rest_mass_frequency_hz: Invariant rest-mass frequency in Hertz

    Returns:
        Total temporal frequency in Hertz

    Raises:
        ValueError: If inputs are invalid
    """
    if momentum_wavelength_m != momentum_wavelength_m:  # NaN
        raise ValueError("Wavelength is NaN")
    if rest_mass_frequency_hz != rest_mass_frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if momentum_wavelength_m <= 0:
        raise ValueError(f"Wavelength must be positive, got {momentum_wavelength_m}")
    if rest_mass_frequency_hz < 0:
        raise ValueError(f"Frequency cannot be negative, got {rest_mass_frequency_hz}")

    c_over_lambda = C / momentum_wavelength_m
    sum_of_squares = (c_over_lambda ** 2) + (rest_mass_frequency_hz ** 2)
    return math.sqrt(sum_of_squares)


class ZeroReferenceError(ZeroDivisionError, ValueError):
    """A zero normalization reference, compatible with legacy callers."""


def normalize_signal(
    observed: float | complex, reference: float | complex
) -> float | complex:
    """Normalize signal Z(t,x) = z(t,x) / z_ref(t,x).

    Args:
        observed: Observed signal value
        reference: Reference signal value

    Returns:
        Normalized signal Z

    Raises:
        ValueError: If reference is zero, NaN, or infinity
    """
    if reference != reference:  # NaN
        raise ValueError("Reference is NaN")
    if reference == 0:
        raise ZeroReferenceError("Reference signal cannot be zero")
    if abs(reference) >= 1e308:
        raise ValueError(f"Reference is infinite or out of bounds: {reference}")
    if observed != observed:  # NaN
        raise ValueError("Observed signal is NaN")

    return observed / reference


def signal_match(
    observed: float,
    reference: float,
    epsilon: float = EPSILON_Z_DEFAULT
) -> RuntimeMatchResult:
    """Check if normalized signal matches reference within tolerance.

    Implements: abs(Z - 1) <= epsilon where Z = z / z_ref

    Args:
        observed: Observed signal value
        reference: Reference signal value
        epsilon: Tolerance for match (unitless)

    Returns:
        RuntimeMatchResult with match outcome
    """
    normalized = cast(float, normalize_signal(observed, reference))
    error = abs(normalized - 1.0)
    matches = error <= epsilon

    return RuntimeMatchResult(
        normalized_value=normalized,
        observed=observed,
        reference=reference,
        epsilon=epsilon,
        matches=matches,
        error=error
    )


def complex_signal_match(
    observed_amplitude: float,
    observed_phase: float,
    reference_amplitude: float,
    reference_phase: float,
    amplitude_tolerance: float = AMPLITUDE_TOLERANCE_DEFAULT,
    phase_tolerance: float = PHASE_TOLERANCE_DEFAULT
) -> RuntimeMatchResult:
    """Check if complex signal (amplitude, phase) matches reference.

    Args:
        observed_amplitude: Magnitude of observed signal
        observed_phase: Phase of observed signal (radians)
        reference_amplitude: Magnitude of reference signal
        reference_phase: Phase of reference signal (radians)
        amplitude_tolerance: Amplitude tolerance (unitless)
        phase_tolerance: Phase tolerance (radians)

    Returns:
        RuntimeMatchResult with match outcome

    Raises:
        ValueError: If amplitudes are invalid
    """
    if reference_amplitude == 0:
        raise ValueError("Reference amplitude cannot be zero")
    if observed_amplitude != observed_amplitude or reference_amplitude != reference_amplitude:
        raise ValueError("Amplitude is NaN")

    # Normalize amplitude
    normalized_amplitude = observed_amplitude / reference_amplitude
    amplitude_error = abs(normalized_amplitude - 1.0)
    amplitude_matches = amplitude_error <= amplitude_tolerance

    # Phase difference (wrap to [-pi, pi])
    phase_diff = observed_phase - reference_phase
    phase_diff = (phase_diff + math.pi) % (2 * math.pi) - math.pi
    phase_matches = abs(phase_diff) <= phase_tolerance

    matches = amplitude_matches and phase_matches

    return RuntimeMatchResult(
        normalized_value=normalized_amplitude,
        observed=observed_amplitude,
        reference=reference_amplitude,
        epsilon=amplitude_tolerance,
        matches=matches,
        error=amplitude_error,
        notes=f"Phase diff: {phase_diff:.6e} rad (tolerance: {phase_tolerance:.6e})"
    )
