from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi.test_generator import generate_frequency_controls


def test_frequency_controls_include_sham_and_neighbors():
    cases = generate_frequency_controls()
    names = [case.name for case in cases]
    assert names == ["anchor", "reference", "neighbor_low", "neighbor_high", "sham"]


def test_invalid_frequency_rejected():
    with pytest.raises(ValueError):
        generate_frequency_controls(0, 8)
