from upi.evidence_lens import ROBUSTNESS_LENS, status_through_lens

ROBUST_LOOP = {
    "status": "HYP",
    "linked_robustness_evidence": {
        "sample_size": 1_000_000,
        "failure_count": 0,
        "independence_documented": True,
        "criterion_predeclared": True,
        "tested_domain": "Declared mirror round trips",
        "test_links": [
            {
                "source_record": "UPI<mirror,1,loop,A>",
                "target_record": "UPI<experiment,1,external,T1>",
                "relation": "MEASURED_BY",
                "test_source": "archive:test-1",
                "tested_claim": "M(M(x)) returns x within tolerance",
            }
        ],
    },
}


def test_lens_off_preserves_canonical_status() -> None:
    result = status_through_lens(ROBUST_LOOP)
    assert result["display_status"] == "HYP"
    assert result["promoted"] is False


def test_lens_on_exposes_scoped_linked_robustness() -> None:
    result = status_through_lens(ROBUST_LOOP, ROBUSTNESS_LENS)
    assert result["display_status"] == "EST-LINKED-ROBUSTNESS"
    assert result["canonical_status"] == "HYP"
    assert result["test_link_count"] == 1


def test_failure_prevents_robustness_promotion() -> None:
    evidence = {**ROBUST_LOOP["linked_robustness_evidence"], "failure_count": 1}
    payload = {**ROBUST_LOOP, "linked_robustness_evidence": evidence}
    assert status_through_lens(payload, ROBUSTNESS_LENS)["promoted"] is False


def test_untyped_external_test_link_does_not_transfer_support() -> None:
    evidence = {**ROBUST_LOOP["linked_robustness_evidence"], "test_links": [{}]}
    payload = {**ROBUST_LOOP, "linked_robustness_evidence": evidence}
    assert status_through_lens(payload, ROBUSTNESS_LENS)["promoted"] is False
