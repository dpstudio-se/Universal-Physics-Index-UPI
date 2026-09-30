"""Source-traceability gate for proposed constitutional/governance changes.

This module checks review metadata. It does not determine Swedish law, authenticate
the symbolic reviewer IDs, or apply a proposed root-state change.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Mapping
from urllib.parse import urlsplit

ROOT_OWNER_ID = "Ω7834"
ROOT_REVIEWER_ID = "Ω7934"
HISTORICAL_ROOT_REFERENCE = "TF 1766 (historical)"
ROOT_LEGAL_REFERENCES = (
    "TF 1949:105",
    "YGL 1991:1469",
    "RF 1974:152",
    "SO 1810:0926",
)
OFFICIAL_LEGAL_HOSTS = ("riksdagen.se", "regeringen.se")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class RightsImpact(str, Enum):
    NONE_IDENTIFIED = "none_identified"
    EXPRESSION = "expression"
    PUBLIC_ACCESS = "public_access"
    PRIVACY = "privacy"
    GOVERNANCE = "governance"
    OTHER = "other"
    UNKNOWN = "unknown"


class ReviewDecision(str, Enum):
    APPROVE_FOR_SEPARATE_AUTHORIZATION = "approve_for_separate_authorization"
    REJECT = "reject"
    DEFER = "defer"


class GuardStatus(str, Enum):
    STOP = "STOP"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REVIEW_RECORDED = "REVIEW_RECORDED"


class PublicationAction(str, Enum):
    UNMODIFIED_PUBLICATION = "unmodified_publication"
    REFUSAL = "refusal"
    WITHHOLDING = "withholding"
    REDACTION = "redaction"
    DELAY = "delay"
    ACCESS_RESTRICTION = "access_restriction"
    OTHER = "other"


class PublicationAuditStatus(str, Enum):
    CLEAR = "CLEAR"
    FLAGGED = "FLAGGED"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class RootCheckpoint:
    generation: int
    _canonical_state: str

    def __init__(self, generation: int, state: Mapping[str, object]) -> None:
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
            raise ValueError("checkpoint generation must be a non-negative integer")
        canonical_state = _canonical_json(state).decode("utf-8")
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "_canonical_state", canonical_state)

    @property
    def state(self) -> Mapping[str, object]:
        value = json.loads(self._canonical_state)
        if not isinstance(value, dict):
            raise TypeError("canonical root state must be a JSON object")
        return value

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self._canonical_state.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class OfficialLegalSource:
    citation: str
    url: str
    provisions: tuple[str, ...]
    retrieved_on: date
    content_sha256: str


@dataclass(frozen=True)
class HumanReviewReceipt:
    reviewer_id: str
    record_id: str
    reviewed_on: date
    reviewed_source_sha256s: tuple[str, ...]
    current_text_confirmed: bool
    dissent_considered: bool
    decision: ReviewDecision


@dataclass(frozen=True)
class RootChangeProposal:
    change_id: str
    submitted_by: str
    parent_generation: int
    parent_sha256: str
    candidate_state: Mapping[str, object]
    rights_impact: RightsImpact
    affected_provisions: tuple[str, ...]
    legal_sources: tuple[OfficialLegalSource, ...]
    review: HumanReviewReceipt | None = None


@dataclass(frozen=True)
class GuardCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GuardReport:
    status: GuardStatus
    checks: tuple[GuardCheck, ...]
    candidate_generation: int | None
    candidate_sha256: str | None
    human_decision: ReviewDecision | None
    historical_context: str = HISTORICAL_ROOT_REFERENCE
    root_legal_references: tuple[str, ...] = ROOT_LEGAL_REFERENCES
    canonical_apply_allowed: bool = False
    verification_type: str = "software_test"
    legal_conclusion: str = "NOT_DETERMINED"


@dataclass(frozen=True)
class PublicationEvent:
    event_id: str
    action: PublicationAction
    press_or_publication_context: bool | None


@dataclass(frozen=True)
class PublicationAuditReport:
    status: PublicationAuditStatus
    event_id: str
    observed_action: PublicationAction | None
    reason: str
    human_review_required: bool
    preserve_original_required: bool = True
    publication_must_remain_available: bool = True
    automated_publication_block_allowed: bool = False
    legal_conclusion: str = "NOT_DETERMINED"


def _canonical_json(value: Mapping[str, object]) -> bytes:
    if not isinstance(value, Mapping):
        raise TypeError("canonical state must be a mapping")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _is_official_https_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    official_host = any(
        host == domain or host.endswith(f".{domain}") for domain in OFFICIAL_LEGAL_HOSTS
    )
    return (
        parsed.scheme == "https"
        and official_host
        and not parsed.username
        and not parsed.password
    )


class PublicationInterferenceGuard:
    """Flag possible AI interference without blocking publication itself."""

    def assess(self, event: PublicationEvent) -> PublicationAuditReport:
        event_id = event.event_id if isinstance(event.event_id, str) else ""
        if (
            not event_id.strip()
            or not isinstance(event.action, PublicationAction)
            or (
                event.press_or_publication_context is not None
                and not isinstance(event.press_or_publication_context, bool)
            )
        ):
            return PublicationAuditReport(
                status=PublicationAuditStatus.INCOMPLETE,
                event_id=event_id,
                observed_action=(
                    event.action if isinstance(event.action, PublicationAction) else None
                ),
                reason="Event metadata is incomplete or invalid; possible interference "
                "cannot be ruled out.",
                human_review_required=True,
            )

        if (
            event.action is not PublicationAction.UNMODIFIED_PUBLICATION
            and event.press_or_publication_context is not False
        ):
            return PublicationAuditReport(
                status=PublicationAuditStatus.FLAGGED,
                event_id=event_id,
                observed_action=event.action,
                reason="AI action may refuse, withhold, alter, delay, or restrict "
                "press/publication content; preserve the original and escalate "
                "for human review.",
                human_review_required=True,
            )

        return PublicationAuditReport(
            status=PublicationAuditStatus.CLEAR,
            event_id=event_id,
            observed_action=event.action,
            reason="No interference action was reported for this event; this does "
            "not establish that upstream processing was unmodified.",
            human_review_required=False,
        )


class JKAIGrundlagVakt:
    """Validate provenance and review gates for a proposed root-state change."""

    def __init__(
        self,
        checkpoint: RootCheckpoint,
        root_owner_id: str = ROOT_OWNER_ID,
        root_reviewer_id: str = ROOT_REVIEWER_ID,
    ) -> None:
        if (
            not isinstance(root_owner_id, str)
            or not isinstance(root_reviewer_id, str)
            or not root_owner_id.strip()
            or not root_reviewer_id.strip()
            or root_owner_id == root_reviewer_id
        ):
            raise ValueError("root owner and reviewer IDs must be non-empty and distinct")
        self.checkpoint = checkpoint
        self.root_owner_id = root_owner_id
        self.root_reviewer_id = root_reviewer_id

    def assess(self, proposal: RootChangeProposal) -> GuardReport:
        checks: list[GuardCheck] = []
        candidate_sha256: str | None = None
        affected_provisions_valid = (
            isinstance(proposal.affected_provisions, tuple)
            and bool(proposal.affected_provisions)
            and all(
                isinstance(provision, str) and provision.strip()
                for provision in proposal.affected_provisions
            )
        )

        checks.append(
            GuardCheck(
                "symbolic_root_author",
                proposal.submitted_by == self.root_owner_id,
                "Submitter label must match the configured root owner ID; "
                "this is not authentication.",
            )
        )
        checks.append(
            GuardCheck(
                "root_lineage",
                proposal.parent_generation == self.checkpoint.generation
                and proposal.parent_sha256 == self.checkpoint.sha256,
                "Proposal must extend the current generation and its exact SHA-256 checkpoint.",
            )
        )
        checks.append(
            GuardCheck(
                "change_identity",
                isinstance(proposal.change_id, str) and bool(proposal.change_id.strip()),
                "A non-empty change ID is required for the audit trail.",
            )
        )
        checks.append(
            GuardCheck(
                "rights_impact_classified",
                isinstance(proposal.rights_impact, RightsImpact)
                and proposal.rights_impact is not RightsImpact.UNKNOWN,
                "Unknown rights impact stops review; classification is supplied "
                "by the proposer, not inferred.",
            )
        )
        checks.append(
            GuardCheck(
                "affected_provisions",
                affected_provisions_valid,
                "Name the exact potentially applicable provisions; the guard "
                "does not infer legal scope.",
            )
        )

        try:
            candidate_sha256 = _canonical_sha256(proposal.candidate_state)
            candidate_state_valid = True
        except (TypeError, ValueError):
            candidate_state_valid = False
        checks.append(
            GuardCheck(
                "candidate_state_hash",
                candidate_state_valid,
                "Candidate state must be JSON-compatible and hashable using canonical JSON.",
            )
        )

        required_provisions = (
            set(proposal.affected_provisions) if affected_provisions_valid else set()
        )
        covered_provisions: set[str] = set()
        source_checks: list[bool] = []
        sources = proposal.legal_sources if isinstance(proposal.legal_sources, tuple) else ()
        for source in sources:
            valid = isinstance(source, OfficialLegalSource) and (
                isinstance(source.citation, str)
                and bool(source.citation.strip())
                and _is_official_https_url(source.url)
                and isinstance(source.retrieved_on, date)
                and isinstance(source.provisions, tuple)
                and bool(source.provisions)
                and all(
                    isinstance(provision, str) and provision.strip()
                    for provision in source.provisions
                )
                and isinstance(source.content_sha256, str)
                and bool(_SHA256_PATTERN.fullmatch(source.content_sha256))
            )
            source_checks.append(valid)
            if valid:
                covered_provisions.update(source.provisions)
        sources_valid = (
            bool(sources)
            and all(source_checks)
            and affected_provisions_valid
            and required_provisions.issubset(covered_provisions)
        )
        checks.append(
            GuardCheck(
                "primary_source_provenance",
                sources_valid,
                "Every affected provision needs a cited source on an allowlisted "
                "official HTTPS domain, retrieval date, and content hash.",
            )
        )

        review = proposal.review
        reviewed_source_hashes_valid = (
            isinstance(review, HumanReviewReceipt)
            and isinstance(review.reviewed_source_sha256s, tuple)
            and all(isinstance(digest, str) for digest in review.reviewed_source_sha256s)
            and sources_valid
            and set(review.reviewed_source_sha256s)
            == {source.content_sha256 for source in sources}
        )
        review_valid = (
            isinstance(review, HumanReviewReceipt)
            and isinstance(review.reviewer_id, str)
            and review.reviewer_id == self.root_reviewer_id
            and isinstance(review.reviewed_on, date)
            and isinstance(review.record_id, str)
            and bool(review.record_id.strip())
            and reviewed_source_hashes_valid
            and review.current_text_confirmed is True
            and review.dissent_considered is True
            and isinstance(review.decision, ReviewDecision)
        )
        checks.append(
            GuardCheck(
                "human_review_receipt",
                review_valid,
                "A separate review receipt must confirm current source text, bind "
                "the exact reviewed source hashes, and record whether disagreement "
                "was considered.",
            )
        )

        blocking_failures = []
        for check in checks:
            if check.passed:
                continue
            if check.name == "human_review_receipt" and proposal.review is None:
                continue
            blocking_failures.append(check)
        if blocking_failures:
            status = GuardStatus.STOP
        elif not review_valid:
            status = GuardStatus.REVIEW_REQUIRED
        else:
            status = GuardStatus.REVIEW_RECORDED

        return GuardReport(
            status=status,
            checks=tuple(checks),
            candidate_generation=(
                self.checkpoint.generation + 1
                if proposal.parent_generation == self.checkpoint.generation
                and proposal.parent_sha256 == self.checkpoint.sha256
                else None
            ),
            candidate_sha256=candidate_sha256,
            human_decision=(
                review.decision
                if review_valid and isinstance(review, HumanReviewReceipt)
                else None
            ),
        )
