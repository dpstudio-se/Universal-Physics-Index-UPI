"""Escape detector for UPI model testing.

Looks for model/data divergence and flags it for falsification review.
"""
from __future__ import annotations


def detect_escape(
    observed: float,
    predicted: float,
    tolerance: float,
) -> dict[str, float | bool | str]:
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    residual = observed - predicted
    escaped = abs(residual) > tolerance
    return {
        "observed": observed,
        "predicted": predicted,
        "residual": residual,
        "tolerance": tolerance,
        "escape": escaped,
        "status": "DER",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "action": "falsification_review" if escaped else "retest",
    }
