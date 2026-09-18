from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi.tempest import TempestObservation, run_tempest


def test_tempest_requires_three_channels():
    shadow = TempestObservation("shadow", 1.0, {})
    mirror = TempestObservation("mirror", 1.0, {})
    noise = TempestObservation("noise", 1.1, {})
    result = run_tempest(shadow, mirror, noise)
    assert result["mirror_delta"] == pytest.approx(0.0)
    assert result["noise_delta"] == pytest.approx(0.1)
