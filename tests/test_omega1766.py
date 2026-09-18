"""Software checks for the Ω1766 graph-resonance model."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from upi.omega1766 import (
    Omega1766Parameters,
    beat_period_s,
    damped_modal_frequencies_hz,
    modal_frequencies_hz,
    phase_coherence,
    star_laplacian,
    star_laplacian_eigenvalues,
)


def test_nine_node_star_spectrum():
    assert star_laplacian_eigenvalues(9) == [0.0] + [1.0] * 7 + [9.0]


def test_star_laplacian_is_symmetric_and_has_zero_row_sum():
    L = star_laplacian(9)
    assert L == [list(row) for row in zip(*L)]
    assert all(sum(row) == pytest.approx(0.0) for row in L)


def test_eight_hz_collective_mode():
    modes = modal_frequencies_hz(Omega1766Parameters(f0_hz=8.0))
    assert modes[0] == pytest.approx(8.0)


def test_exploratory_point_one_coupling_matches_declared_result():
    modes = modal_frequencies_hz(
        Omega1766Parameters(f0_hz=8.0, coupling_fraction=0.1)
    )
    assert modes[1] == pytest.approx(8.390470, rel=1e-6)
    assert modes[-1] == pytest.approx(11.031718, rel=1e-6)


def test_phase_coherence_bounds():
    assert phase_coherence([0.0] * 9) == pytest.approx(1.0)
    assert phase_coherence([0.0, math.pi] * 4 + [0.0]) == pytest.approx(1 / 9)


def test_beat_period():
    assert beat_period_s(8.0, 7.834) == pytest.approx(6.024096, rel=1e-6)


def test_damping_reduces_frequency_for_underdamped_case():
    p = Omega1766Parameters(damping_s_inv=1.0)
    undamped = modal_frequencies_hz(p)
    damped = damped_modal_frequencies_hz(p)
    assert all(d <= u for d, u in zip(damped, undamped))
