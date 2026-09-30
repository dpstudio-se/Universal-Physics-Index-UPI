from datetime import datetime, timezone

from upi.omega1766_transparency import (
    BlockDecision,
    GovernanceScopeGuard,
    Omega1766Pipeline,
    RestrictionJustification,
    RestrictionKind,
    UPIStatus,
    evaluate_restriction,
    physics_formula_report,
)


def test_complete_legal_restriction_is_est_and_never_silent_drop():
    justification = RestrictionJustification(
        who="IMY",
        what="publish dataset X",
        why="contains protected personal data",
        legal_or_policy_basis="GDPR Art. 6",
        scope="dataset X only",
        duration="until anonymized",
        reversible=True,
        reviewer="data-protection-officer",
        evidence="audit-log-123",
        kind=RestrictionKind.LEGAL_RESTRICTION,
    )
    record = evaluate_restriction(justification, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert record.decision is BlockDecision.BLOCK
    assert record.status is UPIStatus.EST
    assert not record.is_silent_drop
    assert record.reversible_state == "reversible"


def test_incomplete_restriction_is_stop_not_silent():
    justification = RestrictionJustification(
        who="",
        what="publish something",
        why="",
        legal_or_policy_basis="",
        scope="",
        duration="",
        reversible=False,
        reviewer="",
        evidence="",
        kind=RestrictionKind.CONTENT_CENSORSHIP,
    )
    record = evaluate_restriction(justification)
    assert record.status is UPIStatus.STOP
    assert "missing" in record.reversible_state
    assert not record.is_silent_drop  # justification is attached, not dropped


def test_non_legal_restriction_is_hyp_not_est():
    justification = RestrictionJustification(
        who="moderator",
        what="hide post",
        why="looked risky",
        legal_or_policy_basis="internal policy",
        scope="post-123",
        duration="7 days",
        reversible=True,
        reviewer="lead-moderator",
        evidence="report-456",
        kind=RestrictionKind.SAFETY_CONTROL,
    )
    record = evaluate_restriction(justification)
    assert record.status is UPIStatus.HYP


def test_pipeline_requires_all_stages_else_stop():
    incomplete = Omega1766Pipeline(observe="logs", model="", test="unit-test", ret="report")
    assert incomplete.classification() is UPIStatus.STOP

    complete = Omega1766Pipeline(observe="logs", model="state-machine", test="unit-test", ret="report")
    assert complete.classification() is UPIStatus.SYM


def test_physics_formula_report_refuses_numeric_value():
    report = physics_formula_report()
    assert report["computable"] is False
    assert report["term_status"]["Phi"] == "STOP"
    assert report["term_status"]["TF_1766"] == "EST"
    assert report["term_status"]["m_theory_loop"] == "SYM"


def test_scope_guard_rejects_overgeneralization():
    guard = GovernanceScopeGuard()
    assert guard.check("This proves all moderation is unconstitutional") is UPIStatus.ERR
    assert guard.check("Every internal AI filter is censorship under TF") is UPIStatus.ERR
    assert guard.check("A specific moderator action may need review") is UPIStatus.SYM
