"""Executable, fail-closed node review; never writes or promotes canonical data.

Trusted application code supplies domain checks and an evidence-only derivation.
Callbacks are not sandboxed. Source digests prove byte identity, not scientific truth.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from .schema_resources import schema_path
from .validation import validate_node_json


@dataclass(frozen=True)
class EvidenceArtifact:
    source: str
    content: bytes
    expected_sha256: str


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    domain: str


@dataclass(frozen=True)
class CheckResult:
    outcome: str  # PASS, FAIL or UNKNOWN; not a scientific claim status
    detail: str
    next_observation: str = ""
    verification_type: str = "software_test"


@dataclass(frozen=True)
class ArtifactReview:
    """Source identity and byte-integrity result; never embeds source contents."""

    source: str | None
    expected_sha256: str | None
    actual_sha256: str | None
    outcome: str


@dataclass(frozen=True)
class FeedbackReport:
    proposal_sha256: str
    human_intent: str
    human_direction: str
    comparison: str
    decision: str
    promotion_gate: str
    checks: dict[str, CheckResult]
    expected: Quantity
    derived: Quantity | None
    stop_reasons: tuple[str, ...]
    next_actions: tuple[str, ...]
    proposed_status: str
    absolute_tolerance: float
    required_checks: tuple[str, ...]
    missing_checks: tuple[str, ...]
    artifacts: tuple[ArtifactReview, ...]
    independence: str = "separate_execution_shared_process; evidence_independence_not_established"
    verification_type: str = "software_test"

    def as_dict(self) -> dict[str, Any]:
        """Keep the original fields and add a structured human-facing review.

        UNKNOWN is distinct from disagreement. Missing checks are absent callbacks;
        an executed check can also return UNKNOWN without being absent.
        """
        report = asdict(self)
        check_records = report["checks"]
        report["review_result"] = {
            "decision_state": (
                "AWAITING_HUMAN_REVIEW"
                if self.promotion_gate == "AWAITING_HUMAN_REVIEW"
                else "STOP"
            ),
            "human_intent": self.human_intent,
            "human_direction": self.human_direction,
            "human_review": {
                "state": "PENDING" if self.promotion_gate == "AWAITING_HUMAN_REVIEW" else "BLOCKED",
                "decision_recorded": False,
                "next_actions": list(self.next_actions),
            },
            "proposal": {
                "sha256": self.proposal_sha256,
                "proposed_status": self.proposed_status,
                "status_promoted": False,
            },
            "astra_result": {
                "role": "implementation_expectation",
                "quantity": asdict(self.expected),
            },
            "upi_result": {
                "role": "evidence_based_derivation_and_checks",
                "quantity": asdict(self.derived) if self.derived is not None else None,
                "checks": {
                    name: value
                    for name, value in check_records.items()
                    if name not in {"provenance_integrity", "mirror"}
                },
            },
            "evidence_result": {
                "integrity_check": check_records["provenance_integrity"],
                "artifacts": [asdict(artifact) for artifact in self.artifacts],
                "scope": "Reference resolution and byte integrity only; source truth and relevance require domain checks.",
                "independence": self.independence,
            },
            "mirror": {
                "comparison": self.comparison,
                "absolute_tolerance": self.absolute_tolerance,
                "unit": self.expected.unit,
                "domain": self.expected.domain,
                "check": check_records["mirror"],
            },
            "disagreements": [
                {"check": name, **value}
                for name, value in check_records.items()
                if value["outcome"] == "FAIL"
            ],
            "missing_checks": list(self.missing_checks),
            "unknown_checks": [
                {"check": name, **value}
                for name, value in check_records.items()
                if value["outcome"] == "UNKNOWN"
            ],
            "required_checks": list(self.required_checks),
            "stop_reasons": list(self.stop_reasons),
            "required_next_observation": [
                {"check": name, "observation": value["next_observation"]}
                for name, value in check_records.items()
                if value["outcome"] != "PASS"
            ],
            "verification": {
                "verification_type": self.verification_type,
                "claims_experimental_verification": False,
                "scope": "Executed software review under the declared policy; not general physical verification.",
            },
        }
        return report


DomainCheck = Callable[[dict[str, Any], tuple[EvidenceArtifact, ...]], CheckResult]
EvidenceDerivation = Callable[[tuple[EvidenceArtifact, ...]], Quantity]


def _quantity_valid(value: Quantity) -> bool:
    return (
        isinstance(value, Quantity)
        and type(value.value) in (int, float)
        and math.isfinite(value.value)
        and isinstance(value.unit, str)
        and bool(value.unit.strip())
        and isinstance(value.domain, str)
        and bool(value.domain.strip())
    )


def _run_check(
    check: DomainCheck, node: dict[str, Any], evidence: tuple[EvidenceArtifact, ...]
) -> CheckResult:
    try:
        result = check(deepcopy(node), evidence)
        if (
            not isinstance(result, CheckResult)
            or result.outcome not in {"PASS", "FAIL", "UNKNOWN"}
            or not isinstance(result.detail, str)
            or not result.detail.strip()
            or not isinstance(result.verification_type, str)
            or not result.verification_type.strip()
            or (
                result.outcome != "PASS"
                and (
                    not isinstance(result.next_observation, str)
                    or not result.next_observation.strip()
                )
            )
        ):
            raise ValueError("invalid check result")
        return result
    except Exception as exc:
        # Do not expose callback exception text, which may contain private source content.
        return CheckResult(
            "UNKNOWN",
            f"Check failed to execute ({type(exc).__name__}).",
            "Repair the check and rerun it on this proposal.",
        )


def review_node(
    node: dict[str, Any],
    *,
    human_intent: str,
    expected: Quantity,
    evidence: tuple[EvidenceArtifact, ...],
    derive_from_evidence: EvidenceDerivation,
    checks: Mapping[str, DomainCheck],
    required_checks: tuple[str, ...] = ("physics", "canonical", "software_tests"),
    absolute_tolerance: float = 0.0,
    human_direction: str = "continue",
) -> FeedbackReport:
    """Run schema, provenance integrity, mirror and caller-required domain checks.

    The caller owns the review policy and must bind ``expected`` to the proposal in
    its domain check. The derivation receives evidence bytes, not the expected answer.
    This API records human intent/direction, not authenticated human approval. Even a
    passing report waits for human review and cannot perform canonical promotion.
    """
    if not isinstance(human_intent, str) or not human_intent.strip():
        raise ValueError("human_intent is required")
    if human_direction not in {"continue", "revise", "defer"}:
        raise ValueError("human_direction must be continue, revise or defer")
    if (
        type(absolute_tolerance) not in (float, int)
        or not math.isfinite(absolute_tolerance)
        or absolute_tolerance < 0
    ):
        raise ValueError("absolute_tolerance must be finite and non-negative")
    if not _quantity_valid(expected):
        raise ValueError("expected must be a finite quantity with unit and domain")
    if not required_checks or any(
        not isinstance(name, str) or not name.strip() for name in required_checks
    ):
        raise ValueError("at least one named domain check is required")
    reserved = {"schema_status", "provenance_integrity", "mirror"}
    if reserved.intersection(checks) or reserved.intersection(required_checks):
        raise ValueError("domain checks cannot replace built-in checks")

    snapshot = deepcopy(node)
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    artifacts = tuple(evidence)
    results: dict[str, CheckResult] = {}
    valid, errors = validate_node_json(snapshot, schema_path("node"))
    results["schema_status"] = CheckResult(
        "PASS" if valid else "FAIL",
        "Node schema and status boundaries passed." if valid else "\n".join(errors),
        "" if valid else "Correct the reported node schema/status violations.",
    )

    sources: set[str] = set()
    artifact_reviews: list[ArtifactReview] = []
    integrity_ok = bool(artifacts)
    for artifact in artifacts:
        source = artifact.source if isinstance(artifact, EvidenceArtifact) else None
        expected_digest = (
            artifact.expected_sha256 if isinstance(artifact, EvidenceArtifact) else None
        )
        actual_digest = (
            hashlib.sha256(artifact.content).hexdigest()
            if isinstance(artifact, EvidenceArtifact) and isinstance(artifact.content, bytes)
            else None
        )
        artifact_reviews.append(
            ArtifactReview(
                source if isinstance(source, str) else None,
                expected_digest if isinstance(expected_digest, str) else None,
                actual_digest,
                (
                    "PASS"
                    if (
                        isinstance(source, str)
                        and bool(source.strip())
                        and source not in sources
                        and actual_digest is not None
                        and actual_digest == expected_digest
                    )
                    else "UNKNOWN"
                ),
            )
        )
        if (
            not isinstance(artifact, EvidenceArtifact)
            or not isinstance(artifact.source, str)
            or not artifact.source.strip()
            or not isinstance(artifact.content, bytes)
            or artifact.source in sources
        ):
            integrity_ok = False
            continue
        sources.add(artifact.source)
        integrity_ok &= hashlib.sha256(artifact.content).hexdigest() == artifact.expected_sha256
    references = snapshot.get("evidence", [])
    references_ok = (
        isinstance(references, list)
        and bool(references)
        and all(
            isinstance(ref, dict)
            and isinstance(ref.get("source"), str)
            and ref["source"] in sources
            for ref in references
        )
    )
    integrity_ok = integrity_ok and references_ok
    results["provenance_integrity"] = CheckResult(
        "PASS" if integrity_ok else "UNKNOWN",
        (
            "Evidence references resolve to digest-matched bytes; source truth is not established."
            if integrity_ok
            else "Required evidence is absent, ambiguous, unbound or digest-mismatched."
        ),
        (
            ""
            if integrity_ok
            else "Supply uniquely identified, digest-matched artifacts for each evidence reference."
        ),
    )

    derived = None
    comparison = "UNKNOWN"
    if integrity_ok:
        try:
            derived = derive_from_evidence(artifacts)
            if not _quantity_valid(derived):
                raise ValueError("invalid derived quantity")
            comparison = (
                "AGREE"
                if (
                    expected.unit == derived.unit
                    and expected.domain == derived.domain
                    and abs(expected.value - derived.value) <= absolute_tolerance
                )
                else "CONFLICT"
            )
        except Exception:
            derived = None
    results["mirror"] = CheckResult(
        {"AGREE": "PASS", "CONFLICT": "FAIL", "UNKNOWN": "UNKNOWN"}[comparison],
        f"Mirror comparison: {comparison}; absolute tolerance={absolute_tolerance} {expected.unit}.",
        (
            ""
            if comparison == "AGREE"
            else "Inspect the evidence derivation, units, domain and expected quantity; rerun the mirror."
        ),
    )
    for name in sorted(set(required_checks) | set(checks)):
        results[name] = (
            _run_check(checks[name], snapshot, artifacts)
            if name in checks
            else CheckResult(
                "UNKNOWN",
                f"Required check '{name}' is unavailable.",
                f"Implement and run the '{name}' check against this proposal and evidence.",
            )
        )

    blockers = tuple(
        f"{name}: {result.detail}" for name, result in results.items() if result.outcome != "PASS"
    )
    actions = tuple(
        result.next_observation for result in results.values() if result.outcome != "PASS"
    )
    if human_direction != "continue":
        blockers += (f"Human direction: {human_direction}.",)
        actions += ("Return the review to the human for the next direction.",)
    return FeedbackReport(
        digest,
        human_intent,
        human_direction,
        comparison,
        "STOP" if blockers else "VERIFY",
        "BLOCKED" if blockers else "AWAITING_HUMAN_REVIEW",
        results,
        expected,
        derived,
        blockers,
        actions or ("Present this report and its scoped evidence to the human for review.",),
        str(snapshot.get("status", "")),
        absolute_tolerance,
        tuple(sorted(reserved | set(required_checks))),
        tuple(sorted(set(required_checks) - set(checks))),
        tuple(artifact_reviews),
    )
