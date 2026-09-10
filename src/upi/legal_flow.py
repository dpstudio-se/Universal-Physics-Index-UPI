"""Six-loop legal workflow controls over declared facts; no autonomous legal judgments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .resilience import RecoveryChain

SNAPSHOT_DATE = "2026-09-10"


def stop(reason: str, next_observation: str) -> dict[str, Any]:
    return {"status": "STOP", "stop_reason": reason, "next_observation": next_observation}


class LegalFlow:
    """Carry the latest state and reject stale/root writes; reuse UPI's immutable ledger."""

    def __init__(self, case_id: str, facts: dict[str, Any], as_of: str = SNAPSHOT_DATE):
        if not case_id:
            raise ValueError("case_id required")
        self.clock = datetime(2026, 9, 10, tzinfo=timezone.utc)
        self.chain = RecoveryChain({"case_id": case_id, "as_of": as_of, "raw_input": facts,
                                    "assessments": {}, "reviews": [], "corrections": [],
                                    "root_scope": "TF1766 is a software anchor, not legal continuity"},
                                   recorded_at=self.clock)

    @property
    def token(self) -> str:
        return self.chain.active.checkpoint_hash

    def apply(self, rule: str, assessment: dict[str, Any], *, expected: str) -> str:
        if expected != self.token:
            raise ValueError("stale state: carry S_n forward, never reset to S_0")
        if not rule or not assessment.get("provenance"):
            raise ValueError("rule and assessment provenance required")
        state = self.chain.active.state
        if state["as_of"] != SNAPSHOT_DATE:
            raise ValueError("temporal mismatch: obtain a statute snapshot for the case date")
        # Original facts remain in their own immutable snapshot; assessments carry forward.
        state["assessments"][rule] = assessment
        self.clock += timedelta(seconds=1)
        self.chain.append(state, recorded_at=self.clock)
        return self.token

    def feedback(self, body: str, decision_ref: str, outcome: str, *, expected: str) -> str:
        if expected != self.token:
            raise ValueError("review must attach to the current case state")
        if body not in {"JO", "KU", "JK", "DOMSTOL"} or not decision_ref or not outcome:
            raise ValueError("review body, decision reference and outcome required")
        state = self.chain.active.state
        state["reviews"].append({"body": body, "source": decision_ref, "outcome": outcome,
                                  "status": "HYP", "effect": "recorded; implementation unverified"})
        self.clock += timedelta(seconds=1)
        self.chain.append(state, recorded_at=self.clock)
        return self.token

    def verify_correction(self, decision_ref: str, observation_ref: str,
                          expected_value: str, observed_value: str, *, expected: str) -> str:
        if expected != self.token:
            raise ValueError("correction must attach to current state")
        state = self.chain.active.state
        if not observation_ref or not any(r["source"] == decision_ref for r in state["reviews"]):
            raise ValueError("correction requires an existing review and implementation observation")
        state["corrections"].append({"review": decision_ref, "observation": observation_ref,
                                      "expected": expected_value, "observed": observed_value,
                                      "closed": expected_value == observed_value, "status": "DER",
                                      "scope": "declared outcome equality; evidence not authenticated"})
        self.clock += timedelta(seconds=1)
        self.chain.append(state, recorded_at=self.clock)
        return self.token


@dataclass(frozen=True)
class DocumentFacts:
    """Facts are supplied legal assessments, with unknown represented by None."""

    authority: bool | None = None
    document: bool | None = None
    stored: bool | None = None
    received: bool | None = None
    drawn_up: bool | None = None
    digital: bool = False
    compilation: bool = False
    accessible: bool | None = None
    routine_actions: bool | None = None
    personal_data: bool | None = None
    compilation_permitted: bool | None = None
    exception: str = "unknown"
    archived: bool | None = None
    dispatched: bool | None = None
    adds_facts: bool | None = None
    secrecy: str = "unknown"
    secrecy_basis: str = ""
    provenance: tuple[str, ...] = ()
    as_of: str = SNAPSHOT_DATE

    def __post_init__(self) -> None:
        for field, value in asdict(self).items():
            if field not in {"exception", "secrecy", "secrecy_basis", "provenance", "as_of"}:
                if value is not None and not isinstance(value, bool):
                    raise ValueError(f"{field} must be a boolean or None")
        if self.exception not in {"unknown", "none", "memo", "draft", "technical_only",
                                 "backup_only", "other_2_14"}:
            raise ValueError("unknown document exception")
        if self.secrecy not in {"unknown", "none", "partial", "full"}:
            raise ValueError("unknown secrecy assessment")


def classify_document(facts: DocumentFacts) -> dict[str, Any]:
    """Loop D. Secrecy applies to information; allmän does not imply fully public."""
    flow = LegalFlow("document", asdict(facts), facts.as_of)

    def result(outcome: str, public: bool | None, reason: str,
               missing: str = "") -> dict[str, Any]:
        return {"outcome": outcome, "allman": public,
                **(stop(reason, missing) if missing else {"status": "DER", "reason": reason}),
                "ledger": flow.chain.to_dict(), "verification_type": "software_test",
                "scope": "conditional result from supplied assessments"}

    def record(rule: str, value: Any) -> None:
        flow.apply(rule, {"value": value, "provenance": list(facts.provenance)}, expected=flow.token)

    if facts.as_of != SNAPSHOT_DATE:
        return result("UNRESOLVED", None, "Snapshot does not establish law at the requested date",
                      "Provide the applicable historical statute version")
    if not facts.provenance:
        return result("UNRESOLVED", None, "Document assessments have no provenance",
                      "Provide source references for the assessed facts")
    for rule, value, label in (("TF 2:5", facts.authority, "authority scope"),
                                ("TF 2:3", facts.document, "document type")):
        record(rule, value)
        if value is None:
            return result("UNRESOLVED", None, f"Unknown {label}", f"Assess {label} under {rule}")
        if not value:
            return result("OUTSIDE_PROFILE", False, f"Declared {label} is outside this TF 2 profile")
    stored = facts.stored
    if facts.digital:
        stored = facts.accessible
        if facts.compilation:
            if stored is False or facts.routine_actions is False:
                stored = False
            elif stored is None or facts.routine_actions is None:
                stored = None
            if facts.personal_data is None and stored is not False:
                stored = None
            if facts.personal_data and facts.compilation_permitted is not True:
                stored = False if facts.compilation_permitted is False else None
    record("TF 2:6–7", stored)
    if stored is None:
        return result("UNRESOLVED", None, "Storage/accessibility not established",
                      "Assess technical accessibility, routine measures and compilation authority")
    if not stored:
        return result("NOT_ALLMAN", False, "Not stored under the supplied TF 2:6–7 assessment")
    record("TF 2:12–14", facts.exception)
    if facts.exception == "unknown":
        return result("UNRESOLVED", None, "Exceptions have not been assessed",
                      "Review TF 2:8–14 including archives, drafts and technical copies")
    if facts.exception in {"technical_only", "backup_only", "other_2_14"}:
        return result("NOT_ALLMAN", False, "Declared exception excludes allmän status")
    drawn_up = facts.drawn_up
    if facts.exception in {"memo", "draft"}:
        if facts.archived:
            drawn_up = True
        elif facts.dispatched:
            drawn_up = True
        elif facts.archived is None or facts.dispatched is None:
            return result("UNRESOLVED", None, "Archive/dispatch status unknown",
                          "Determine whether the note or draft was archived or dispatched")
        elif facts.exception == "draft" or facts.adds_facts is False:
            return result("NOT_ALLMAN", False, "Unarchived, undispatched draft or true memo")
        elif facts.adds_facts is None:
            return result("UNRESOLVED", None, "Memo may contain substantive facts",
                          "Assess the factual portions separately under TF 2:12")
        else:
            return result("PORTION_REVIEW", None, "Substantive facts and memo-only content must be separated",
                          "Assess each portion under TF 2:10 and 2:12; do not exclude or release the whole memo")
    arrived = facts.received is True or drawn_up is True
    record("TF 2:9–11", {"received": facts.received, "drawn_up": drawn_up})
    if not arrived:
        if facts.received is None or drawn_up is None:
            return result("UNRESOLVED", None, "Arrival/completion unknown",
                          "Assess dispatch, completion and special cases in TF 2:9–11")
        return result("NOT_ALLMAN", False, "Neither received nor drawn up")
    record("TF 2:4", True)
    record("TF 2:2", {"secrecy": facts.secrecy, "basis": facts.secrecy_basis})
    if facts.secrecy == "unknown" or facts.secrecy != "none" and not facts.secrecy_basis:
        return result("SECRECY_REVIEW", True, "Applicable secrecy assessment or legal basis missing",
                      "Identify applicable OSL provision and assess each protected piece of information")
    if facts.secrecy == "full":
        return result("REFUSAL_REVIEW", True, "All information assessed secret; review formal decision")
    record("TF 2:15–16", facts.secrecy)
    return result("PARTIAL_ACCESS" if facts.secrecy == "partial" else "ACCESS",
                  True, "Access to non-secret portions; form, timing and copy exceptions still apply")


def review_routes(actor: str, *, issue: str, decision_level: str = "formal",
                  court_activity: str = "unknown", as_of: str = SNAPSHOT_DATE) -> dict[str, Any]:
    """Loop E: routes are a set, not mutually exclusive actor labels."""
    if as_of != SNAPSHOT_DATE:
        return {"routes": [], **stop("Temporal mismatch", "Supply law applicable at the case date")}
    actors = {"government", "minister", "authority", "official", "district_court", "appeal_court",
              "administrative_appeal_court", "supreme_court", "supreme_administrative_court",
              "parliament", "parliament_agency", "jk", "municipal_assembly", "unknown"}
    if actor not in actors or issue not in {"disclosure", "oversight", "tf_offence", "minister_offence"}:
        raise ValueError("unknown actor or issue")
    routes: list[dict[str, str]] = []
    gaps: list[dict[str, Any]] = []

    def add(target: str, lane: str, basis: str, effect: str) -> None:
        routes.append({"target": target, "lane": lane, "basis": basis, "effect": effect})

    if actor in {"government", "minister"}:
        add("KU", "oversight", "RF 13:1–2; JO 15", "Parliamentary scrutiny, not disclosure appeal")
    elif actor in {"authority", "official", "district_court", "appeal_court",
                   "administrative_appeal_court", "supreme_court", "supreme_administrative_court",
                   "parliament_agency"}:
        add("JO", "oversight", "RF 13:6; JO 11–17,20", "Subject to JO scope exceptions; no automatic reversal")
    else:
        gaps.append(stop("Actor not covered by this oversight profile",
                         "Check JO 14–16 and the actor's exact statutory capacity"))
    if issue == "disclosure":
        if decision_level == "employee_refusal":
            add("AUTHORITY_DECISION", "remedy", "OSL 6:3",
                "Request authority review and written decision before ordinary appeal")
        elif decision_level != "formal":
            gaps.append(stop("Decision level unknown", "Obtain the written decision and decision-maker"))
        elif actor in {"government", "parliament", "supreme_court", "supreme_administrative_court"}:
            add("NO_ORDINARY_APPEAL", "remedy", "TF 2:19; OSL 6:7", "Ordinary appeal excluded")
        elif actor == "minister":
            add("GOVERNMENT", "remedy", "TF 2:19; OSL 6:8", "Ministerial disclosure decision")
        elif actor == "parliament_agency":
            gaps.append(stop("Special parliamentary-agency appeal provisions",
                             "Identify the agency and its special appeal statute"))
        elif actor in {"district_court", "appeal_court"}:
            if court_activity == "unknown":
                gaps.append(stop("Court activity not classified", "Is the decision judicial or administrative?"))
            elif court_activity == "judicial":
                add("APPEAL_COURT" if actor == "district_court" else "SUPREME_COURT",
                    "remedy", "OSL 6:8–10", "Judicial/court-care activity; individual requester")
            elif court_activity == "administrative":
                add("ADMINISTRATIVE_APPEAL_COURT", "remedy", "OSL 6:8", "Administrative disclosure decision")
            else:
                raise ValueError("unknown court activity")
        elif actor == "administrative_appeal_court":
            add("SUPREME_ADMINISTRATIVE_COURT", "remedy", "OSL 6:8–9", "Individual requester")
        elif actor in {"authority", "jk", "municipal_assembly"}:
            add("ADMINISTRATIVE_APPEAL_COURT", "remedy", "OSL 6:7–8", "Ordinary individual-requester route")
        else:
            gaps.append(stop("Decision-maker unresolved", "Identify the authority that made the formal decision"))
    if issue == "tf_offence":
        add("JK", "prosecution", "TF 9:1–3,7; 12:1",
            "TF applicability required; preserve private-prosecution and JO statutory exceptions")
    if issue == "minister_offence":
        if actor == "minister":
            add("KU_THEN_SUPREME_COURT", "prosecution", "RF 13:3",
                "Official-capacity offence and gross breach of duty are required")
        else:
            gaps.append(stop("RF 13:3 scope not established", "Identify minister and official-capacity conduct"))
    return {**(stop("One or more route conditions are unresolved", "Resolve the named gaps")
               if gaps else {"status": "DER"}), "routes": routes, "gaps": gaps,
            "scope": "conditional route map for individuals; no complaint sent"}


def publication_boundary(*, tf_applies: bool | None, public_actor: bool | None,
                         pre_review: bool | None, content_obstruction: bool | None) -> dict[str, Any]:
    """Loop C keeps scope and exceptions upstream of a possible interference finding."""
    values = (tf_applies, public_actor, pre_review, content_obstruction)
    if any(v is not None and not isinstance(v, bool) for v in values):
        raise ValueError("boundary facts must be boolean or unknown")
    if tf_applies is None:
        return stop("TF applicability is unknown", "Assess medium, publication and TF 1:2–6,11–14")
    if not tf_applies:
        return {"status": "DER", "outcome": "OTHER_FRAMEWORK", "basis": "TF 1:2–6,11–14"}
    if public_actor is None:
        return stop("Actor capacity unknown", "Identify whether the action is by a public body")
    if not public_actor:
        return {"status": "DER", "outcome": "OUTSIDE_PUBLIC_PREBLOCK_GATE", "basis": "TF 1:8"}
    if pre_review is True or content_obstruction is True:
        return {"status": "HYP", "outcome": "INTERFERENCE_REVIEW", "basis": "TF 1:8–10",
                "falsification_condition": "No public pre-review/content interference, or applicable TF authority",
                "next_observation": "Verify action, timing, publication purpose and any TF-authorized restriction"}
    if pre_review is None or content_obstruction is None:
        return stop("Interference facts unknown", "Obtain the action and its content-based grounds")
    return {"status": "DER", "outcome": "NO_PREBLOCK_DETECTED", "basis": "TF 1:8",
            "scope": "does not decide secrecy, acquisition methods or other TF exceptions"}
