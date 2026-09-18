"""Ω1766 graph-resonance model.

This module is a declared mathematical model, not a physical constant or
claim about mythology, biology, or an 8 Hz universal mechanism.

The model treats N coupled scalar oscillators as
    m q'' + gamma q' + (k I + kappa L) q = 0
where L is the graph Laplacian. Modal frequencies are computed from the
eigenvalues of L. Coherence is a phase-order parameter R in [0, 1].
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Omega1766Parameters:
    n: int = 9
    mass_kg: float = 1.0
    f0_hz: float = 8.0
    coupling_fraction: float = 0.1
    damping_s_inv: float = 0.0

    @property
    def omega0_rad_s(self) -> float:
        return 2.0 * math.pi * self.f0_hz

    @property
    def k_n_per_m(self) -> float:
        return self.mass_kg * self.omega0_rad_s**2

    @property
    def kappa_n_per_m(self) -> float:
        return self.coupling_fraction * self.k_n_per_m


def star_laplacian(n: int = 9) -> list[list[float]]:
    """Return the Laplacian of an unweighted n-node star graph."""
    if n < 2:
        raise ValueError("A star graph requires at least two nodes")
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(1, n):
        matrix[0][i] = matrix[i][0] = -1.0
        matrix[0][0] += 1.0
        matrix[i][i] += 1.0
    return matrix


def star_laplacian_eigenvalues(n: int = 9) -> list[float]:
    """Analytic Laplacian spectrum of an unweighted star graph."""
    if n < 2:
        raise ValueError("A star graph requires at least two nodes")
    return [0.0] + [1.0] * (n - 2) + [float(n)]


def modal_frequencies_hz(params: Omega1766Parameters | None = None) -> list[float]:
    """Return undamped modal frequencies for the declared oscillator model."""
    p = params or Omega1766Parameters()
    if p.mass_kg <= 0 or p.f0_hz <= 0:
        raise ValueError("mass_kg and f0_hz must be positive")
    if p.coupling_fraction < 0:
        raise ValueError("coupling_fraction must be non-negative")
    ratio = p.kappa_n_per_m / p.mass_kg
    return [
        math.sqrt(p.omega0_rad_s**2 + ratio * lam) / (2.0 * math.pi)
        for lam in star_laplacian_eigenvalues(p.n)
    ]


def damped_modal_frequencies_hz(
    params: Omega1766Parameters | None = None,
) -> list[float]:
    """Return damped frequencies when the declared viscous damping is underdamped."""
    p = params or Omega1766Parameters()
    if p.damping_s_inv < 0:
        raise ValueError("damping_s_inv must be non-negative")
    frequencies = []
    for f in modal_frequencies_hz(p):
        omega = 2.0 * math.pi * f
        radicand = omega**2 - (p.damping_s_inv / (2.0 * p.mass_kg))**2
        frequencies.append(math.sqrt(radicand) / (2.0 * math.pi) if radicand > 0 else 0.0)
    return frequencies


def phase_coherence(phases_rad: list[float] | tuple[float, ...]) -> float:
    """Kuramoto-style phase-order parameter R, bounded to [0, 1]."""
    if not phases_rad:
        raise ValueError("At least one phase is required")
    x = sum(math.cos(theta) for theta in phases_rad) / len(phases_rad)
    y = sum(math.sin(theta) for theta in phases_rad) / len(phases_rad)
    return math.hypot(x, y)


def beat_period_s(f_a_hz: float, f_b_hz: float) -> float:
    """Return the simple-superposition beat period."""
    delta = abs(f_a_hz - f_b_hz)
    if delta == 0:
        raise ValueError("Equal frequencies have no finite beat period")
    return 1.0 / delta


def model_report(params: Omega1766Parameters | None = None) -> dict[str, object]:
    """Export the declared Ω1766 calculation without scientific promotion."""
    p = params or Omega1766Parameters()
    modes = modal_frequencies_hz(p)
    return {
        "model": "omega1766_star_network",
        "status": "HYP",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "equations": [
            "m q'' + gamma q' + (k I + kappa L) q = 0",
            "omega_lambda^2 = omega0^2 + (kappa/m) lambda",
            "R = abs(sum(exp(i theta_j))/N)",
        ],
        "parameters": {
            "n": p.n,
            "mass_kg": p.mass_kg,
            "f0_hz": p.f0_hz,
            "coupling_fraction": p.coupling_fraction,
            "damping_s_inv": p.damping_s_inv,
        },
        "laplacian_eigenvalues": star_laplacian_eigenvalues(p.n),
        "modal_frequencies_hz": modes,
        "coherence_definition": "R is computed from measured/supplied phases; it is not assumed to equal a physical Ω1766 field.",
        "assumptions": [
            "The nine-node topology is a chosen star-graph test model, not a historical reconstruction of Yggdrasil.",
            "8 Hz is a configurable hypothesis/reference value, not a universal constant.",
            "The coupling is linear and time-invariant.",
        ],
        "falsification_conditions": [
            "Independent implementations disagree with the analytic spectrum.",
            "A proposed physical 8 Hz effect disappears under preregistered sham and neighboring-frequency controls.",
        ],
    }
