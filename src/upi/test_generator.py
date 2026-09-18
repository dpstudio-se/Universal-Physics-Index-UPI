"""UPI test generation primitives.

Generates deterministic test cases from declared hypotheses without promoting
them to established physics. This is a model/software layer.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    name: str
    hypothesis: str
    control: str
    expected_guard: str


def generate_frequency_controls(
    anchor_hz: float = 7.834125,
    reference_hz: float = 8.0,
) -> list[TestCase]:
    """Create neighboring-frequency and sham controls around declared anchors."""
    if anchor_hz <= 0 or reference_hz <= 0:
        raise ValueError("frequencies must be positive")
    delta = abs(reference_hz - anchor_hz)
    return [
        TestCase("anchor", f"f={anchor_hz} Hz", "none", "effect must be measured"),
        TestCase("reference", f"f={reference_hz} Hz", "none", "effect must be measured"),
        TestCase("neighbor_low", f"f={reference_hz-delta} Hz", "frequency offset", "no privileged effect assumed"),
        TestCase("neighbor_high", f"f={reference_hz+delta} Hz", "frequency offset", "no privileged effect assumed"),
        TestCase("sham", "no active frequency hypothesis", "sham input", "no hypothesis-specific effect expected"),
    ]
