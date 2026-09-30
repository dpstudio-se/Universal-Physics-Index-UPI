import hashlib
from datetime import date

from upi.jkai_grundlag_vakt import (
    ROOT_OWNER_ID,
    ROOT_REVIEWER_ID,
    HISTORICAL_ROOT_REFERENCE,
    ROOT_LEGAL_REFERENCES,
    GuardStatus,
    HumanReviewReceipt,
    JKAIGrundlagVakt,
    OfficialLegalSource,
    PublicationAction,
    PublicationAuditStatus,
    PublicationEvent,
    PublicationInterferenceGuard,
    ReviewDecision,
    RightsImpact,
    RootChangeProposal,
    RootCheckpoint,
)

LEGAL_PROVISIONS = ("RF 2 kap. 1 §", "TF 1 kap. 1 §")


def make_source(provision: str) -> OfficialLegalSource:
    return OfficialLegalSource(
        citation=f"Primärkälla för {provision}",
        url="https://www.riksdagen.se/sv/dokument-och-lagar/",
        provisions=(provision,),
        retrieved_on=date(2026, 9, 30),
        content_sha256=hashlib.sha256(provision.encode("utf-8")).hexdigest(),
    )


def make_proposal(
    checkpoint: RootCheckpoint,
    *,
    sources: tuple[OfficialLegalSource, ...] | None = None,
    review: HumanReviewReceipt | None = None,
    submitted_by: str = ROOT_OWNER_ID,
    parent_generation: int | None = None,
    rights_impact: RightsImpact = RightsImpact.GOVERNANCE,
) -> RootChangeProposal:
    return RootChangeProposal(
        change_id="jkai-change-001",
        submitted_by=submitted_by,
        parent_generation=(
            checkpoint.generation if parent_generation is None else parent_generation
        ),
        parent_sha256=checkpoint.sha256,
        candidate_state={"policy": "candidate"},
        rights_impact=rights_impact,
        affected_provisions=LEGAL_PROVISIONS,
        legal_sources=sources or tuple(make_source(item) for item in LEGAL_PROVISIONS),
        review=review,
    )


def make_review(
    sources: tuple[OfficialLegalSource, ...] | None = None,
) -> HumanReviewReceipt:
    reviewed_sources = sources or tuple(make_source(item) for item in LEGAL_PROVISIONS)
    return HumanReviewReceipt(
        reviewer_id=ROOT_REVIEWER_ID,
        record_id="PR-123",
        reviewed_on=date(2026, 9, 30),
        reviewed_source_sha256s=tuple(
            source.content_sha256 for source in reviewed_sources
        ),
        current_text_confirmed=True,
        dissent_considered=True,
        decision=ReviewDecision.APPROVE_FOR_SEPARATE_AUTHORIZATION,
    )


def test_valid_proposal_requires_human_review_before_recorded_state() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    guard = JKAIGrundlagVakt(checkpoint)

    report = guard.assess(make_proposal(checkpoint))

    assert report.status is GuardStatus.REVIEW_REQUIRED
    assert report.candidate_generation == checkpoint.generation + 1
    assert report.candidate_sha256 is not None
    assert report.canonical_apply_allowed is False
    assert report.legal_conclusion == "NOT_DETERMINED"
    assert report.historical_context == HISTORICAL_ROOT_REFERENCE
    assert len(report.root_legal_references) == len(ROOT_LEGAL_REFERENCES) == 4


def test_root_checkpoint_captures_immutable_canonical_state() -> None:
    state = {"policy": {"value": "current"}}
    checkpoint = RootCheckpoint(generation=4, state=state)
    original_hash = checkpoint.sha256

    state["policy"]["value"] = "mutated"
    snapshot = checkpoint.state

    assert checkpoint.sha256 == original_hash
    assert checkpoint.state == {"policy": {"value": "current"}}
    assert snapshot is not checkpoint.state


def test_review_receipt_never_authorizes_automatic_application() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    guard = JKAIGrundlagVakt(checkpoint)

    report = guard.assess(make_proposal(checkpoint, review=make_review()))

    assert report.status is GuardStatus.REVIEW_RECORDED
    assert report.human_decision is ReviewDecision.APPROVE_FOR_SEPARATE_AUTHORIZATION
    assert report.canonical_apply_allowed is False


def test_missing_affected_primary_source_stops_assessment() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    guard = JKAIGrundlagVakt(checkpoint)

    report = guard.assess(
        make_proposal(checkpoint, sources=(make_source(LEGAL_PROVISIONS[0]),))
    )

    assert report.status is GuardStatus.STOP
    source_check = next(
        check for check in report.checks if check.name == "primary_source_provenance"
    )
    assert not source_check.passed


def test_unofficial_source_host_stops_assessment() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    sources = (
        OfficialLegalSource(
            citation="Unverified copy",
            url="https://riksdagen.se.example.invalid/law",
            provisions=(LEGAL_PROVISIONS[0], LEGAL_PROVISIONS[1]),
            retrieved_on=date(2026, 9, 30),
            content_sha256="b" * 64,
        ),
    )

    report = JKAIGrundlagVakt(checkpoint).assess(make_proposal(checkpoint, sources=sources))

    assert report.status is GuardStatus.STOP


def test_stale_root_parent_or_unknown_impact_stops_assessment() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    guard = JKAIGrundlagVakt(checkpoint)

    stale = guard.assess(make_proposal(checkpoint, parent_generation=3))
    unknown = guard.assess(
        make_proposal(checkpoint, rights_impact=RightsImpact.UNKNOWN, review=make_review())
    )

    assert stale.status is GuardStatus.STOP
    assert unknown.status is GuardStatus.STOP


def test_symbolic_root_and_reviewer_ids_are_not_interchangeable() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    proposal = make_proposal(checkpoint, submitted_by=ROOT_REVIEWER_ID, review=make_review())

    report = JKAIGrundlagVakt(checkpoint).assess(proposal)

    assert report.status is GuardStatus.STOP
    assert not next(check for check in report.checks if check.name == "symbolic_root_author").passed


def test_review_by_unconfigured_symbol_stops_instead_of_authorizing() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    valid_review = make_review()
    review = HumanReviewReceipt(
        reviewer_id="Ω8200",
        record_id="PR-123",
        reviewed_on=date(2026, 9, 30),
        reviewed_source_sha256s=valid_review.reviewed_source_sha256s,
        current_text_confirmed=True,
        dissent_considered=True,
        decision=ReviewDecision.APPROVE_FOR_SEPARATE_AUTHORIZATION,
    )

    report = JKAIGrundlagVakt(checkpoint).assess(
        make_proposal(checkpoint, review=review)
    )

    assert report.status is GuardStatus.STOP
    assert report.human_decision is None


def test_review_receipt_must_bind_the_reviewed_source_hashes() -> None:
    checkpoint = RootCheckpoint(generation=4, state={"policy": "current"})
    review = make_review()
    mismatched_review = HumanReviewReceipt(
        reviewer_id=review.reviewer_id,
        record_id=review.record_id,
        reviewed_on=review.reviewed_on,
        reviewed_source_sha256s=("f" * 64,),
        current_text_confirmed=review.current_text_confirmed,
        dissent_considered=review.dissent_considered,
        decision=review.decision,
    )

    report = JKAIGrundlagVakt(checkpoint).assess(
        make_proposal(checkpoint, review=mismatched_review)
    )

    assert report.status is GuardStatus.STOP
    assert report.human_decision is None


def test_possible_ai_censorship_is_flagged_without_blocking_publication() -> None:
    report = PublicationInterferenceGuard().assess(
        PublicationEvent(
            event_id="pub-001",
            action=PublicationAction.REDACTION,
            press_or_publication_context=True,
        )
    )

    assert report.status is PublicationAuditStatus.FLAGGED
    assert report.human_review_required
    assert report.preserve_original_required
    assert report.publication_must_remain_available
    assert report.automated_publication_block_allowed is False
    assert report.legal_conclusion == "NOT_DETERMINED"


def test_unknown_publication_context_flags_interfering_action() -> None:
    report = PublicationInterferenceGuard().assess(
        PublicationEvent(
            event_id="pub-002",
            action=PublicationAction.DELAY,
            press_or_publication_context=None,
        )
    )

    assert report.status is PublicationAuditStatus.FLAGGED


def test_explicit_non_publication_context_does_not_flag_restriction() -> None:
    report = PublicationInterferenceGuard().assess(
        PublicationEvent(
            event_id="chat-001",
            action=PublicationAction.REFUSAL,
            press_or_publication_context=False,
        )
    )

    assert report.status is PublicationAuditStatus.CLEAR
    assert not report.human_review_required


def test_other_intervention_in_uncertain_context_is_flagged() -> None:
    report = PublicationInterferenceGuard().assess(
        PublicationEvent(
            event_id="pub-003",
            action=PublicationAction.OTHER,
            press_or_publication_context=None,
        )
    )

    assert report.status is PublicationAuditStatus.FLAGGED


def test_invalid_publication_metadata_is_escalated_without_automatic_block() -> None:
    report = PublicationInterferenceGuard().assess(
        PublicationEvent(
            event_id="",
            action=PublicationAction.UNMODIFIED_PUBLICATION,
            press_or_publication_context=True,
        )
    )

    assert report.status is PublicationAuditStatus.INCOMPLETE
    assert report.human_review_required
    assert report.publication_must_remain_available
    assert report.automated_publication_block_allowed is False
