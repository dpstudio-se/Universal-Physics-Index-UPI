"""Quantum-correlation analysis primitives for UPI.

This module provides statistical building blocks for pairwise outcome data.
It does not infer quantum entanglement from generic correlation.

A CHSH value is implemented for four binary measurement settings. A
statistically significant Bell/CHSH violation can serve as an entanglement
witness under the assumptions of the measurement model, locality test,
sampling, and loophole controls. The module itself does not establish those
experimental assumptions.

Classification: DER / software_test. Experimental promotion is disabled.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Sequence


def _validate_binary(values: Sequence[int], name: str) -> None:
    if not values:
        raise ValueError(f"{name} must not be empty")
    if any(value not in (-1, 1) for value in values):
        raise ValueError(f"{name} must contain only -1 or +1")


def joint_distribution(
    x: Sequence[int], y: Sequence[int]
) -> dict[tuple[int, int], float]:
    """Return empirical P(x,y) for binary outcomes."""
    if len(x) != len(y):
        raise ValueError("x and y must have equal length")
    _validate_binary(x, "x")
    _validate_binary(y, "y")
    n = len(x)
    counts = Counter(zip(x, y))
    return {(a, b): counts[(a, b)] / n for a in (-1, 1) for b in (-1, 1)}


def marginals(
    x: Sequence[int], y: Sequence[int]
) -> tuple[dict[int, float], dict[int, float]]:
    """Return empirical marginal distributions P(x) and P(y)."""
    pxy = joint_distribution(x, y)
    px = {a: sum(pxy[(a, b)] for b in (-1, 1)) for a in (-1, 1)}
    py = {b: sum(pxy[(a, b)] for a in (-1, 1)) for b in (-1, 1)}
    return px, py


def independence_expected(
    x: Sequence[int], y: Sequence[int]
) -> dict[tuple[int, int], float]:
    """Return P_independent(x,y)=P(x)P(y) from the observed marginals."""
    px, py = marginals(x, y)
    return {(a, b): px[a] * py[b] for a in (-1, 1) for b in (-1, 1)}


def binary_correlation(x: Sequence[int], y: Sequence[int]) -> float:
    """Return E[XY] for binary +/-1 outcomes, in [-1, 1]."""
    if len(x) != len(y):
        raise ValueError("x and y must have equal length")
    _validate_binary(x, "x")
    _validate_binary(y, "y")
    return sum(a * b for a, b in zip(x, y)) / len(x)


def chsh_value(
    e00: float, e01: float, e10: float, e11: float
) -> float:
    """Return S = E00 + E01 + E10 - E11."""
    values = (e00, e01, e10, e11)
    if any(not math.isfinite(v) or not -1.0 <= v <= 1.0 for v in values):
        raise ValueError("each correlation must be finite and in [-1, 1]")
    return e00 + e01 + e10 - e11


def chsh_entanglement_witness(
    e00: float, e01: float, e10: float, e11: float
) -> dict[str, float | bool | str]:
    """Evaluate a CHSH/Bell witness without claiming experimental verification.

    |S| > 2 is the algebraic criterion for a CHSH violation. In an actual
    experiment, statistical uncertainty and measurement assumptions must also
    be evaluated before treating the result as evidence of entanglement.
    """
    s = chsh_value(e00, e01, e10, e11)
    return {
        "S": s,
        "abs_S": abs(s),
        "local_bound": 2.0,
        "quantum_tsirelson_bound": 2.0 * math.sqrt(2.0),
        "violation": abs(s) > 2.0,
        "status": "DER",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
    }


def correlation_report(
    x: Sequence[int], y: Sequence[int]
) -> dict[str, object]:
    """Create a UPI-safe pairwise correlation report."""
    pxy = joint_distribution(x, y)
    pind = independence_expected(x, y)
    return {
        "model": "upi_binary_pair_correlation",
        "status": "DER",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "sample_count": len(x),
        "joint_distribution": pxy,
        "independence_null": pind,
        "correlation_E_xy": binary_correlation(x, y),
        "interpretation_guard": (
            "Correlation is not by itself evidence of quantum entanglement. "
            "A CHSH/Bell analysis requires four compatible measurement-setting "
            "correlations plus statistical and experimental controls."
        ),
    }
