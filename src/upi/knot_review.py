"""Append evidence-backed candidate decisions without erasing measured disagreements."""

from copy import deepcopy
from typing import Any

from .knot_model import Resolution


def record_decision(report: dict[str, Any], knot_id: str, decision: Resolution, *,
                    actor: str, timestamp: str, reason: str, evidence: str) -> dict[str, Any]:
    if not all(isinstance(v, str) and v.strip() for v in (actor, timestamp, reason, evidence)):
        raise ValueError("actor, timestamp, reason and evidence are required")
    result = deepcopy(report)
    knot = next((k for k in result["knots"] if k["id"] == knot_id), None)
    if knot is None:
        raise ValueError("unknown knot")
    if decision == Resolution.CLOSED and knot["state"] != "CLOSED":
        raise ValueError("closure requires a new analysis of the corrected paths")
    if len(knot["red_tests"]) < 14:
        raise ValueError("RED analysis required before a decision")
    knot["history"].append({"previous_decision": knot["decision"], "decision": decision.value,
                            "actor": actor, "timestamp": timestamp, "reason": reason,
                            "evidence": evidence, "status": "HYP",
                            "scope": "reviewer decision about candidate bridge; evidence unverified"})
    knot["decision"] = decision.value
    return result
