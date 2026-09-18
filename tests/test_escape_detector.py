from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi.escape_detector import detect_escape


def test_escape_detector_flags_large_residual():
    result = detect_escape(1.2, 1.0, 0.1)
    assert result["escape"] is True
    assert result["action"] == "falsification_review"


def test_escape_detector_requests_retest_within_tolerance():
    result = detect_escape(1.05, 1.0, 0.1)
    assert result["escape"] is False
    assert result["action"] == "retest"
