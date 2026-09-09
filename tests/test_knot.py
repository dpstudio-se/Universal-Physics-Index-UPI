"""verification_type: software_test. These fixtures establish no physical novelty."""

import copy
import json
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

import pytest

from upi.knot import analyze, compare_steps
from upi.knot_examples import example_document, example_paths, example_report
from upi.knot_io import analyze_document, dumps
from upi.knot_model import PathTrace, Resolution, Tolerance
from upi.knot_review import record_decision
from upi.knot_score import score_components
from upi.knot_site import build


def test_regression_controls():
    report = example_report()
    knots = {k["checkpoint"]: k for k in report["knots"]}
    exact = knots["lorentz-time"]
    assert exact["state"] == "CLOSED"
    assert exact["epsilon"] < 1e-18
    assert "NUMERICAL_NOISE" in exact["causes"]
    assert knots["observer-offset"]["epsilon"] == pytest.approx(0.7621886869999344)
    assert knots["observer-offset"]["state"] == "OPEN"
    assert "TEMPORAL_MISMATCH" in knots["historical-territory"]["causes"]
    assert "SEMANTIC_MISMATCH" in knots["name-function"]["causes"]
    assert "SEMANTIC_MISMATCH" in knots["spelling"]["causes"]
    assert knots["false-mirror"]["state"] == "REMAP"
    assert knots["false-mirror"]["epsilon"] is None
    assert "INFORMATION_LOSS" in knots["lost-sign"]["causes"]
    assert not report["claims_experimental_verification"]
    assert report["patch_not_erase"]
    assert all(len(k["red_tests"]) >= 14 for k in report["knots"])


def test_serialization_is_stable_and_inputs_preserved():
    document = json.loads(dumps(example_document()))
    before = copy.deepcopy(document)
    first = analyze_document(document)
    assert document == before
    assert dumps(first) == dumps(analyze_document(document))
    assert json.loads(dumps(first))["paths"] == document["paths"]


def test_locates_first_failure_and_continues_without_erasing():
    paths, tolerances = example_paths()
    result = analyze(paths, tolerances)
    assert result["knots"][1]["first_failed_relation"] == "observer-offset"
    assert result["knots"][1]["last_safe_node"] == "lorentz-time-a"
    assert len(result["knots"]) == 7
    assert result["knots"][-1]["first_failed_relation"] == "observer-offset"
    assert paths[0].steps[0].observation.raw_value == 2e-6
    assert result["knots"][1]["quarantined"][0]["relation"] == "CANDIDATE_BRIDGE"


def test_ranking_penalizes_weak_or_dependent_provenance():
    a = example_paths()[0][0].steps[0].observation
    b = replace(a, source="independent", source_group="second", provenance=("independent",))
    weak = score_components(replace(a, source_quality=0.01), b, 1, 1, 1)
    modest = score_components(a, b, 0.2, 1, 1)
    assert weak["score"] < modest["score"]
    assert score_components(a, a, 1, 1, 1)["score"] == 0
    assert score_components(a, replace(b, provenance=a.provenance), 1, 1, 1)["score"] == 0


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True])
def test_invalid_tolerances(value):
    with pytest.raises(ValueError):
        Tolerance(value, "m")


def test_equal_values_do_not_close_wrong_time_or_missing_context():
    step = example_paths()[0][0].steps[0]
    b = replace(step, observation=replace(step.observation, time="1690"))
    assert compare_steps(step, b, Tolerance(0, "s"))["state"] == "OPEN"


def test_invalid_inverse_and_location_cannot_close_equal_values():
    step = example_paths()[0][0].steps[0]
    for other in (replace(step, inverse_domain_valid=False),
                  replace(step, observation=replace(step.observation, location="elsewhere"))):
        result = compare_steps(step, other, Tolerance(0, "s"))
        assert result["state"] == "REMAP"
        assert result["epsilon"] == 0
    b = replace(step, observation=replace(step.observation, time=""))
    assert compare_steps(step, b, Tolerance(0, "s"))["state"] == "OPEN"


def test_unaligned_and_reversed_paths():
    paths, tolerance = example_paths()
    short = PathTrace("short", paths[1].steps[:1])
    result = analyze((paths[0], short), tolerance)
    assert result["alignment_gaps"][0]["status"] == "STOP"
    with pytest.raises(ValueError):
        PathTrace("broken", (paths[0].steps[0], paths[0].steps[-1]))


def test_three_paths_compare_all_pairs():
    paths, tolerance = example_paths()
    a = PathTrace("a", paths[0].steps[:1])
    b = PathTrace("b", paths[1].steps[:1])
    c = replace(b, id="c")
    assert len(analyze((a, b, c), tolerance)["knots"]) == 3


def test_malicious_input_is_data_and_flags_are_strict():
    document = json.loads(dumps(example_document()))
    document["paths"][0]["steps"][0]["observation"]["name"] = "<script>alert(1)</script>"
    assert "<script>" in dumps(analyze_document(document))
    document["paths"][0]["steps"][0]["mirror_valid"] = "false"
    with pytest.raises(ValueError):
        analyze_document(document)


def test_static_bundle_is_allowlisted_and_complete(tmp_path: Path):
    archive = build(tmp_path / "oden")
    with ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == {"oden/" + name for name in
            ("index.html", "oden.css", "oden.js", "knots.json", "paths.example.json", "manifest.json")}
        assert b"ODEN KNOT MAP" in bundle.read("oden/index.html")
        assert json.loads(bundle.read("oden/knots.json"))["patch_not_erase"] is True


def test_review_preserves_residual_and_requires_evidence():
    original = example_report()
    knot = original["knots"][1]
    revised = record_decision(original, knot["id"], Resolution.FALSIFIED,
                              actor="fixture reviewer", timestamp="2026-09-09",
                              reason="Injected offset explains candidate anomaly", evidence="fixture offset")
    assert original["knots"][1]["history"] == []
    assert revised["knots"][1]["epsilon"] == knot["epsilon"]
    assert revised["knots"][1]["decision"] == "FALSIFIED"
    assert revised["knots"][1]["state"] == "OPEN"
    with pytest.raises(ValueError, match="closure requires"):
        record_decision(original, knot["id"], Resolution.CLOSED,
                        actor="reviewer", timestamp="2026", reason="wish", evidence="none")
