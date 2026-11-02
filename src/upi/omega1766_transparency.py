"""Omega1766 (Ω1766) transparency/observability core.

This module turns the user-authored "Omega1766 — TF Transparency /
Observability Core" specification into real, testable code. It is an
*internal software transparency policy* for this AI workflow, modelled after
(but explicitly distinct from) Swedish constitutional censorship-prohibition
principles (TF/YGL).

Boundary, stated once, enforced throughout this module:

* Ω1766 is a software transparency/observability *operator*, classified
  ``SYM`` unless an independently testable mechanism is defined below.
* Ω1766 is NOT itself a Swedish legal rule, and does not decide legal
  questions. See :mod:`upi.tf1766_governance` for the actual legal
  reference (1766 års tryckfrihetsförordning / TF 1949:105 / YGL 1991:1469).
* The constitutional no-prior-censorship principle binds ``myndighet eller
  annat allmänt organ`` acting on ``tryckta skrifter`` (and, via YGL, other
  covered media forms). It must not be silently generalized into "all
  moderation is unconstitutional" or "every internal AI filter is censorship
  under TF" -- this module never makes that claim and callers must not
  either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class UPIStatus(str, Enum):
    """UPI evidence-status taxonomy used throughout this module."""

    EST = "EST"  # established law / documented source / reproducible test
    DER = "DER"  # follows from declared premises
    HYP = "HYP"  # falsifiable proposal
    SYM = "SYM"  # architectural analogy or symbolic mapping
    STOP = "STOP"  # missing identity, evidence, scope or mechanism
    ERR = "ERR"  # contradicted or invalid


class RestrictionKind(str, Enum):
    """Distinct kinds of workflow restriction. Never collapse these into one."""

    APPROVAL = "APPROVAL"
    SAFETY_CONTROL = "SAFETY_CONTROL"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    LEGAL_RESTRICTION = "LEGAL_RESTRICTION"
    CONTENT_CENSORSHIP = "CONTENT_CENSORSHIP"


class BlockDecision(str, Enum):
    """Terminal decision for a proposed restriction. There is no silent DROP."""

    PUBLISH = "PUBLISH"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class RestrictionJustification:
    """A proposed restriction must identify all of these fields.

    Any missing required field means the restriction cannot be recorded as
    justified and the audit trail must carry ``UPIStatus.STOP`` instead of a
    silent pass-through.
    """

    who: str
    what: str
    why: str
    legal_or_policy_basis: str
    scope: str
    duration: str
    reversible: bool
    reviewer: str
    evidence: str
    kind: RestrictionKind

    def missing_fields(self) -> tuple[str, ...]:
        missing = []
        for name in ("who", "what", "why", "legal_or_policy_basis", "scope", "duration", "reviewer", "evidence"):
            if not getattr(self, name).strip():
                missing.append(name)
        return tuple(missing)

    @property
    def is_complete(self) -> bool:
        return not self.missing_fields()


@dataclass(frozen=True)
class AuditRecord:
    """An immutable audit trail entry for a BLOCK decision.

    Enforces the module's core audit rule: never silently transform
    ``BLOCK`` into ``DROP``. A block always carries its reason, authority,
    evidence, reviewer, timestamp, and reversible state through to the
    caller.
    """

    decision: BlockDecision
    justification: RestrictionJustification | None
    status: UPIStatus
    timestamp: str
    reversible_state: str

    @property
    def is_silent_drop(self) -> bool:
        """A BLOCK with no justification recorded would be a silent drop."""
        return self.decision is BlockDecision.BLOCK and self.justification is None


def evaluate_restriction(justification: RestrictionJustification, *, now: datetime | None = None) -> AuditRecord:
    """Evaluate a proposed restriction and produce a non-silent audit record.

    A restriction missing required fields is recorded with ``UPIStatus.STOP``
    (missing identity/evidence/scope/mechanism) rather than silently allowed
    or silently dropped.
    """
    timestamp = (now or datetime.now(timezone.utc)).isoformat()
    if not justification.is_complete:
        return AuditRecord(
            decision=BlockDecision.BLOCK,
            justification=justification,
            status=UPIStatus.STOP,
            timestamp=timestamp,
            reversible_state=f"incomplete:missing={','.join(justification.missing_fields())}",
        )
    return AuditRecord(
        decision=BlockDecision.BLOCK,
        justification=justification,
        status=UPIStatus.EST if justification.kind is RestrictionKind.LEGAL_RESTRICTION else UPIStatus.HYP,
        timestamp=timestamp,
        reversible_state="reversible" if justification.reversible else "irreversible",
    )


# Internal transparency policy: hidden-state handling rules.
# Maps an internal condition to the disclosure action this workflow commits to.
TRANSPARENCY_POLICY: dict[str, str] = {
    "hidden_state": "expose_or_log",
    "silent_drop": "disclose",
    "unexplained_deny": "identify",
    "redaction": "record_reason",
    "missing_evidence": "mark_stop",
    "speculative_claim": "mark_hyp_or_sym",
    "secret": "redact_content_preserve_fact_of_redaction",
}


@dataclass(frozen=True)
class Omega1766Pipeline:
    """The OBSERVE -> MODEL -> TEST -> RETURN operator pipeline.

    Classification: SYM, unless each stage below is backed by an
    independently testable mechanism (which this dataclass requires the
    caller to supply explicitly -- no stage may be assumed).
    """

    observe: str
    model: str
    test: str
    ret: str

    def classification(self) -> UPIStatus:
        stages = (self.observe, self.model, self.test, self.ret)
        if any(not stage.strip() for stage in stages):
            return UPIStatus.STOP
        return UPIStatus.SYM


# The user-supplied "physics formula" terms and their required status.
# This module never computes a numeric value for V: Phi is undeclared, and
# several terms are explicitly SYM/HYP. Attempting to evaluate V would be a
# status violation (treating SYM/HYP terms as EST/DER).
PHYSICS_FORMULA_TERM_STATUS: dict[str, UPIStatus] = {
    "V": UPIStatus.SYM,
    "Omega_1766": UPIStatus.SYM,
    "TF_1766": UPIStatus.EST,  # historical/legal reference only, see tf1766_governance
    "8Hz": UPIStatus.SYM,
    "Torus": UPIStatus.SYM,
    "Phi": UPIStatus.STOP,  # undefined; must be declared before use
    "m_eq_hf_over_c2": UPIStatus.DER,  # E=hf, E=mc^2 -> m=hf/c^2 is standard derivation
    "information_mass": UPIStatus.HYP,
    "m_theory_loop": UPIStatus.SYM,
}


def physics_formula_report() -> dict[str, object]:
    """Return the per-term status breakdown; refuses to produce a value for V."""
    return {
        "formula": "V = pi * Omega^1766 * TF^1766 * 8Hz * (m = hf/c^2) * Phi * Torus",
        "term_status": {k: v.value for k, v in PHYSICS_FORMULA_TERM_STATUS.items()},
        "computable": False,
        "stop_reason": "Phi is undeclared and multiple terms are SYM/HYP; "
        "no numeric value may be reported without conflating status levels.",
    }


@dataclass(frozen=True)
class GovernanceScopeGuard:
    """Guards against the two named overgeneralizations.

    The constitutional no-prior-censorship rule applies to:
      * an authority (``myndighet eller annat allmänt organ``), and
      * the constitutional scope of covered media (tryckta skrifter / YGL media).

    It must not be read as "all moderation is unconstitutional" or "every
    internal AI filter is censorship under TF".
    """

    forbidden_generalizations: tuple[str, ...] = field(
        default=(
            "all moderation is unconstitutional",
            "every internal AI filter is censorship under TF",
        )
    )

    def check(self, claim: str) -> UPIStatus:
        normalized = claim.strip().lower()
        for forbidden in self.forbidden_generalizations:
            if forbidden.lower() in normalized:
                return UPIStatus.ERR
        return UPIStatus.SYM
