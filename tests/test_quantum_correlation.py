"""Tests for UPI quantum-correlation primitives."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from upi.quantum_correlation import (
    binary_correlation,
    chsh_entanglement_witness,
    chsh_value,
    independence_expected,
    joint_distribution,
)


def test_perfect_positive_binary_correlation():
    assert binary_correlation([1, 1, -1, -1], [1, 1, -1, -1]) == pytest.approx(1.0)


def test_joint_distribution_sums_to_one():
    p = joint_distribution([1, 1, -1, -1], [1, -1, 1, -1])
    assert sum(p.values()) == pytest.approx(1.0)
    assert p[(1, 1)] == pytest.approx(0.25)


def test_independence_null_uses_marginals():
    x = [1, 1, -1, -1]
    y = [1, -1, 1, -1]
    p = independence_expected(x, y)
    assert all(value == pytest.approx(0.25) for value in p.values())


def test_chsh_local_bound_example():
    assert chsh_value(1.0, 1.0, 1.0, 1.0) == pytest.approx(2.0)
    assert chsh_entanglement_witness(1.0, 1.0, 1.0, 1.0)["violation"] is False


def test_chsh_quantum_example_crosses_local_bound():
    # Idealized correlations giving 2*sqrt(2), used only as a software fixture.
    s = 1.0 / math.sqrt(2.0)
    result = chsh_entanglement_witness(s, s, s, -s)
    assert result["S"] == pytest.approx(2.0 * math.sqrt(2.0))
    assert result["violation"] is True
    assert result["claims_experimental_verification"] is False


def test_binary_validation():
    with pytest.raises(ValueError):
        binary_correlation([0, 1], [1, -1])


def test_length_validation():
    with pytest.raises(ValueError):
        joint_distribution([1], [1, -1])
