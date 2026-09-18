"""Validation gate for governed UPI model promotion."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationResult:
    reproducible: bool
    dimensional_consistency: bool
    no_escape: bool
    falsification_survived: bool

    @property
    def passed(self) -> bool:
        return all((self.reproducible,self.dimensional_consistency,self.no_escape,self.falsification_survived))

    @property
    def decision(self) -> str:
        return "PROPOSAL" if self.passed else "STOP"

def validate(*, reproducible: bool, dimensional_consistency: bool, no_escape: bool, falsification_survived: bool) -> ValidationResult:
    return ValidationResult(reproducible, dimensional_consistency, no_escape, falsification_survived)

def dna_update_proposal(result: ValidationResult, claim: str) -> dict[str, object]:
    if not claim.strip():
        raise ValueError("claim must not be empty")
    if not result.passed:
        return {"decision":"STOP","status":"ERR","claim":claim,"reason":"validation_gate_failed","writes_dna":False}
    return {"decision":"PROPOSAL","status":"HYP","claim":claim,"writes_dna":False,"requires_human_or_external_validation":True}
