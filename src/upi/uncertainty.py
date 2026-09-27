"""Uncertainty helpers. Software checks, not laboratory analysis."""

from __future__ import annotations

from .constants import C, H
from .physics import mass_from_frequency


def mass_uncertainty_from_frequency(frequency_hz: float, u_frequency_hz: float) -> dict[str, float]:
    """Propagate frequency uncertainty through m = h f / c^2 when h and c are exact.

    u(m) = h u(f) / c^2
    """
    mass = mass_from_frequency(frequency_hz)
    if u_frequency_hz < 0:
        raise ValueError("uncertainty must be non-negative")
    u_mass = H * u_frequency_hz / (C**2)
    return {
        "mass_kg": mass,
        "u_mass_kg": u_mass,
        "frequency_hz": frequency_hz,
        "u_frequency_hz": u_frequency_hz,
    }
