"""Visible weighted aggregation. Assumptions stay in the result."""

from __future__ import annotations


def weighted_mean(values: list[float], weights: list[float]) -> dict[str, float | str]:
    """W = Σ(w_i x_i) / Σ w_i with documented equal-default weights.

    This is a software aggregation helper, not independent scientific evidence.
    """
    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    if not values:
        raise ValueError("values must not be empty")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be non-negative")
    total = sum(weights)
    if total == 0:
        raise ValueError("weight sum must be positive")
    estimate = sum(value * weight for value, weight in zip(values, weights, strict=True)) / total
    return {
        "estimate": estimate,
        "weight_sum": total,
        "n": float(len(values)),
        "model": "W = sum(w_i x_i) / sum(w_i)",
        "verification_type": "software_test",
    }
