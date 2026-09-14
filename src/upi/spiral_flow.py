"""Dynamic spiral-flow helpers for reproducible UPI simulations.

This module keeps the declared frequency signal separate from any fluid-model
assumptions. It provides exact kinematic relations and a rigid-vortex control
field, plus a mode switch for velocity, vorticity, and a Navier-Stokes
residual. It does not claim to solve the full 3-D Navier-Stokes existence
problem.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from .constants import C, H


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
    period = 1.0 / frequency_hz
    angular = 2.0 * math.pi * frequency_hz
    energy = H * frequency_hz
    mass = energy / (C * C)
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
        phase.append(phase[-1] + 2.0 * math.pi * frequency * dt_s)
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


def rigid_vortex_velocity(
    x: float, y: float, frequency_hz: float
) -> tuple[float, float, float]:
    """Rigid rotation control field v=(-omega*y, omega*x, 0)."""
    state = frequency_state(frequency_hz)
    return (-state.angular_frequency_rad_s * y, state.angular_frequency_rad_s * x, 0.0)


def rigid_vortex_curl(frequency_hz: float) -> tuple[float, float, float]:
    """Exact curl of the rigid-vortex control field."""
    state = frequency_state(frequency_hz)
    return (0.0, 0.0, 2.0 * state.angular_frequency_rad_s)


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
    residual = tuple(
        dt_velocity[i]
        + convective[i]
        + pressure_gradient[i] / density
        - viscosity * laplacian_velocity[i]
        - force[i]
        for i in range(3)
    )
    return residual[0], residual[1], residual[2]


def select_mode(step: int, cycle: tuple[NavierMode, ...] | None = None) -> NavierMode:
    """Cycle analysis modes without resetting the shared simulation state."""
    modes = cycle or tuple(NavierMode)
    if not modes:
        raise ValueError("cycle must contain at least one mode")
    if step < 0:
        raise ValueError("step must be non-negative")
    return modes[step % len(modes)]
