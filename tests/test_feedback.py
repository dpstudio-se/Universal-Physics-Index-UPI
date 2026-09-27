"""verification_type: software_test; synthetic inputs, no astronomical observations."""

import hashlib
from dataclasses import replace

import pytest

from upi.feedback import CheckResult, EvidenceArtifact, Quantity, review_node


@pytest.fixture
def case():
    content = b"2.0"
    return {
        "node": {
            "address": "UPI<mathematics,1,test,feedback_fixture>",
            "title": "Synthetic feedback fixture",
            "description": "A software control, not physical evidence.",
            "status": "DER",
            "evidence": [{"type": "calculation", "source": "fixture:scalar"}],
        },
        "human_intent": "Check the synthetic scalar and return the decision to me.",
        "expected": Quantity(2.0, "1", "synthetic scalar"),
        "evidence": (
            EvidenceArtifact("fixture:scalar", content, hashlib.sha256(content).hexdigest()),
        ),
        "derive_from_evidence": lambda artifacts: Quantity(
            float(artifacts[0].content), "1", "synthetic scalar"
        ),
        "checks": {
            "fixture_control": lambda node, artifacts: CheckResult(
                "PASS", "Synthetic control only."
            )
        },
        "required_checks": ("fixture_control",),
    }


def test_agreement_returns_to_human_without_promotion(case):
    report = review_node(**case)
    assert (report.comparison, report.decision, report.promotion_gate) == (
        "AGREE",
        "VERIFY",
        "AWAITING_HUMAN_REVIEW",
    )
    assert report.human_intent == case["human_intent"]
    assert "independence_not_established" in report.independence
    assert report.as_dict()["verification_type"] == "software_test"


@pytest.mark.parametrize(
    "quantity",
    [
        Quantity(3, "1", "synthetic scalar"),
        Quantity(2, "m", "synthetic scalar"),
        Quantity(2, "1", "physical observation"),
    ],
)
def test_mirror_conflict_blocks(case, quantity):
    case["expected"] = quantity
    report = review_node(**case)
    assert report.comparison == "CONFLICT"
    assert report.promotion_gate == "BLOCKED"
    assert report.stop_reasons and report.next_actions


@pytest.mark.parametrize("mode", ["absent", "tampered", "unbound", "duplicate"])
def test_provenance_cannot_be_replaced_by_agreement(case, mode):
    original = case["evidence"][0]
    case["evidence"] = {
        "absent": (),
        "tampered": (replace(original, content=b"3.0"),),
        "unbound": (replace(original, source="fixture:other"),),
        "duplicate": (original, original),
    }[mode]
    report = review_node(**case)
    assert report.comparison == "UNKNOWN"
    assert report.decision == "STOP"
    assert report.derived is None


def test_missing_domain_check_is_unknown_even_when_mirror_agrees(case):
    case["required_checks"] = ("physics",)
    report = review_node(**case)
    assert report.comparison == "AGREE"
    assert report.checks["physics"].outcome == "UNKNOWN"
    assert report.promotion_gate == "BLOCKED"


@pytest.mark.parametrize("outcome", ["FAIL", "UNKNOWN", "unrecognized"])
def test_check_failure_or_invalid_result_blocks(case, outcome):
    case["checks"]["fixture_control"] = lambda node, artifacts: CheckResult(
        outcome, "Control did not pass.", "Inspect the control input."
    )
    assert review_node(**case).decision == "STOP"


def test_exception_is_unknown_without_leaking_source_text(case):
    def broken(node, artifacts):
        raise RuntimeError("PRIVATE SOURCE CONTENT")

    case["checks"]["fixture_control"] = broken
    report = review_node(**case)
    assert report.checks["fixture_control"].outcome == "UNKNOWN"
    assert "PRIVATE" not in str(report.as_dict())


@pytest.mark.parametrize("direction", ["revise", "defer"])
def test_human_can_change_direction_even_after_agreement(case, direction):
    case["human_direction"] = direction
    report = review_node(**case)
    assert report.comparison == "AGREE"
    assert report.promotion_gate == "BLOCKED"


def test_schema_and_evidence_boundaries_execute(case):
    case["node"].update(verification_type="software_test", claims_experimental_verification=True)
    report = review_node(**case)
    assert "UPI-E014" in report.checks["schema_status"].detail
    assert report.decision == "STOP"


def test_checks_cannot_mutate_other_checks_or_original(case):
    def mutate(node, artifacts):
        node["title"] = "changed"
        return CheckResult("PASS", "Changed private copy.")

    def inspect(node, artifacts):
        assert node["title"] == "Synthetic feedback fixture"
        return CheckResult("PASS", "Original snapshot preserved.")

    case["checks"] = {"a_mutate": mutate, "fixture_control": inspect}
    first = review_node(**case)
    assert first.decision == "VERIFY"
    assert case["node"]["title"] == "Synthetic feedback fixture"
    case["node"]["title"] = "New proposal"
    assert review_node(**case).proposal_sha256 != first.proposal_sha256


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_invalid_tolerance_rejected(case, value):
    with pytest.raises(ValueError, match="tolerance"):
        review_node(**case, absolute_tolerance=value)


def test_nonfinite_derivation_is_unknown(case):
    case["derive_from_evidence"] = lambda artifacts: Quantity(float("nan"), "1", "synthetic scalar")
    assert review_node(**case).comparison == "UNKNOWN"


def test_cannot_override_builtin_gate(case):
    case["checks"]["schema_status"] = case["checks"]["fixture_control"]
    with pytest.raises(ValueError, match="built-in"):
        review_node(**case)


def test_empty_domain_policy_rejected(case):
    case["required_checks"] = ()
    with pytest.raises(ValueError, match="domain check"):
        review_node(**case)


def test_human_review_has_separate_results_and_no_source_contents(case):
    import json

    report = review_node(**case).as_dict()
    view = report["review_result"]
    assert view["decision_state"] == "AWAITING_HUMAN_REVIEW"
    assert view["astra_result"]["quantity"]["value"] == 2
    assert view["upi_result"]["quantity"]["value"] == 2
    assert view["evidence_result"]["artifacts"][0]["outcome"] == "PASS"
    assert view["human_review"]["decision_recorded"] is False
    assert view["proposal"]["status_promoted"] is False
    assert view["verification"]["claims_experimental_verification"] is False
    assert view["disagreements"] == view["missing_checks"] == view["unknown_checks"] == []
    assert "content" not in view["evidence_result"]["artifacts"][0]
    json.dumps(report, allow_nan=False)


def test_missing_and_executed_unknown_checks_are_distinct(case):
    case["required_checks"] = ("absent", "fixture_control")
    case["checks"]["fixture_control"] = lambda node, artifacts: CheckResult(
        "UNKNOWN", "Source relevance unresolved.", "Identify the source model."
    )
    view = review_node(**case).as_dict()["review_result"]
    assert view["missing_checks"] == ["absent"]
    assert {item["check"] for item in view["unknown_checks"]} == {"absent", "fixture_control"}
    assert view["disagreements"] == []
    assert len(view["required_next_observation"]) == 2


def test_report_exposes_conflict_and_tolerance(case):
    case["expected"] = Quantity(3, "1", "synthetic scalar")
    view = review_node(**case, absolute_tolerance=0.1).as_dict()["review_result"]
    assert view["decision_state"] == "STOP"
    assert view["disagreements"][0]["check"] == "mirror"
    assert view["mirror"]["absolute_tolerance"] == 0.1
    assert view["astra_result"]["quantity"] != view["upi_result"]["quantity"]


def test_report_records_tampered_digest_without_claiming_conflict(case):
    case["evidence"] = (replace(case["evidence"][0], content=b"changed"),)
    view = review_node(**case).as_dict()["review_result"]
    artifact = view["evidence_result"]["artifacts"][0]
    assert artifact["actual_sha256"] != artifact["expected_sha256"]
    assert artifact["outcome"] == "UNKNOWN"
    assert view["upi_result"]["quantity"] is None
    assert view["disagreements"] == []
