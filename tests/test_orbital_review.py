"""verification_type: software_test; repository-claim regression, not observation."""

import json
import runpy
from pathlib import Path

import pytest

from upi.orbital_review import check_signed_periapsis_equation

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def orbit():
    return json.loads((ROOT / "examples/feedback/sources/hyperbolic_orbit.json").read_bytes())


def test_real_repository_case_agrees_algebraically_but_stops_on_physics():
    example = runpy.run_path(str(ROOT / "examples/feedback/review_atlas.py"))
    report = example["run_review"](use_original=True)
    view = report.as_dict()["review_result"]
    assert report.comparison == "AGREE"
    assert report.checks["provenance_integrity"].outcome == "PASS"
    assert report.checks["physics"].outcome == "FAIL"
    assert "-3.14" in report.checks["physics"].detail
    assert "7.14" in report.checks["physics"].detail
    assert report.checks["source_case_schema"].outcome == "FAIL"
    assert view["decision_state"] == "STOP"
    assert view["missing_checks"] == ["canonical", "software_tests"]


@pytest.mark.parametrize("eccentricity", [1.000001, 2, 6.14, 100])
def test_wrong_sign_fails_across_hyperbolic_domain(orbit, eccentricity):
    assert (
        check_signed_periapsis_equation(orbit, eccentricity=eccentricity, periapsis=1).outcome
        == "FAIL"
    )
    orbit["equations"] = [
        equation.replace("2/q + 1/a", "2/q - 1/a") for equation in orbit["equations"]
    ]
    assert (
        check_signed_periapsis_equation(orbit, eccentricity=eccentricity, periapsis=1).outcome
        == "PASS"
    )


@pytest.mark.parametrize("e,q", [(1, 1), (0.9, 1), (2, 0), (float("nan"), 1)])
def test_domain_boundaries_are_unknown(orbit, e, q):
    assert check_signed_periapsis_equation(orbit, eccentricity=e, periapsis=q).outcome == "UNKNOWN"


def test_unrecognized_formula_is_not_executed(orbit):
    orbit["equations"] = ["unrecognized formula"]
    assert check_signed_periapsis_equation(orbit, eccentricity=2, periapsis=1).outcome == "UNKNOWN"


def test_corrected_case_remains_blocked_for_observation_provenance():
    from upi.schema_resources import schema_path
    from upi.validation import validate_node_json

    corrected = json.loads((ROOT / "data/mechanics/hyperbolic_orbit.json").read_bytes())
    valid, errors = validate_node_json(corrected, schema_path("node"))
    assert valid, errors
    assert all(
        "2/q + 1/a" not in text for text in corrected["equations"] + corrected["predictions"]
    )
    example = runpy.run_path(str(ROOT / "examples/feedback/review_atlas.py"))
    report = example["run_review"](use_primary=False)
    assert report.checks["physics"].outcome == "PASS"
    assert report.comparison == "AGREE"
    assert report.checks["observation_binding"].outcome == "UNKNOWN"
    assert report.decision == "STOP"
    assert report.promotion_gate == "BLOCKED"


@pytest.mark.parametrize(
    "e,q,mu", [(1.000001, 1.0, 1.0), (2.0, 7e6, 3.986e14), (6.14, 2e11, 1.327e20)]
)
def test_vis_viva_energy_and_inverse_consistency(e, q, mu):
    a = q / (1 - e)
    vp_squared = mu * (2 / q - 1 / a)
    energy_from_state = vp_squared / 2 - mu / q
    energy_from_elements = -mu / (2 * a)
    assert energy_from_state == pytest.approx(energy_from_elements, rel=1e-8)
    assert vp_squared > 2 * mu / q
    assert 1 + 2 * energy_from_elements * q / mu == pytest.approx(e)
    assert q == pytest.approx(a * (1 - e))
