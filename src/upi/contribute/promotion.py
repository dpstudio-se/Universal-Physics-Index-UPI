"""Server-owned promotion policy inputs. No policy means no promotion."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from upi.feedback import DomainCheck, EvidenceArtifact, EvidenceDerivation, Quantity

REQUIRED_PROMOTION_CHECKS = (
    "physics",
    "canonical",
    "software_tests",
    "status_promotion",
    "chamber_integrity",
    "chamber_isolation",
)


@dataclass(frozen=True)
class PromotionInputs:
    expected: Quantity
    evidence: tuple[EvidenceArtifact, ...]
    derive_from_evidence: EvidenceDerivation
    checks: Mapping[str, DomainCheck]
    absolute_tolerance: float = 0.0


@dataclass(frozen=True)
class PromotionPolicy:
    # Version must identify deployed code and policy, not a client-controlled string.
    version: str
    prepare: Callable[[dict[str, Any]], PromotionInputs]
