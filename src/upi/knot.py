"""Locate disagreements at aligned typed checkpoints without rewriting either path."""

from __future__ import annotations

import math
from dataclasses import asdict
from itertools import combinations
from typing import Any

from .knot_model import PATCH_NOT_ERASE, Cause, PathTrace, Resolution, Step, Tolerance
from .knot_score import score_components
from .models import EdgeType


def compare_steps(a: Step, b: Step, tolerance: Tolerance) -> dict[str, Any]:
    left, right = a.observation, b.observation
    checks: list[dict[str, Any]] = []
    causes: list[str] = []

    def check(name: str, detected: bool | None, cause: Cause, evidence: str) -> None:
        checks.append({"check": name, "result": "UNKNOWN" if detected is None else
                       "DETECTED" if detected else "CLEAR", "evidence": evidence,
                       "status": "STOP" if detected is None else "DER",
                       "stop_reason": "Required independent evidence missing" if detected is None
                       else None,
                       "next_observation": evidence if detected is None else None})
        if detected and cause.value not in causes:
            causes.append(cause.value)

    check("wrong timestamp", left.time != right.time if left.time and right.time else None,
          Cause.TEMPORAL_MISMATCH, "Compare observation times; no backward propagation")
    unit_bad = left.units != right.units or left.units != tolerance.units
    check("unit mismatch", unit_bad, Cause.BAD_MIRROR, "Exact declared units; no conversion")
    check("coordinate mismatch", left.coordinate != right.coordinate or left.location != right.location
          if "unspecified" not in (left.coordinate, right.coordinate) and left.location and right.location
          else None, Cause.BAD_MIRROR, "Provide location and coordinate system for both branches")
    check("alias/name variant", left.name != right.name, Cause.SEMANTIC_MISMATCH,
          "Distinct raw names retained; supply an evidenced alias relation")
    check("same name different function", left.name == right.name and left.function != right.function,
          Cause.SEMANTIC_MISMATCH, "Compare typed function independently of name")
    check("different name same function", left.name != right.name and left.function == right.function,
          Cause.SEMANTIC_MISMATCH, "Shared function does not establish entity identity")
    dependent = left.source == right.source or bool(set(left.provenance) & set(right.provenance))
    if left.source_group and right.source_group:
        dependent |= left.source_group == right.source_group
    check("dependent sources", dependent if dependent or
          (left.source_group and right.source_group) else None,
          Cause.DEPENDENT_SOURCES, "Inspect source lineage, including shared upstream references")
    compatible = (not unit_bad and left.domain == right.domain and
                  left.function == right.function and left.entity == right.entity and
                  isinstance(left.raw_value, str) == isinstance(right.raw_value, str))
    epsilon: float | None = None
    if compatible:
        if isinstance(left.raw_value, str):
            epsilon = float(left.raw_value != right.raw_value)
        else:
            epsilon = abs(float(left.raw_value) - float(right.raw_value))
        if not math.isfinite(epsilon):
            raise ValueError("residual overflow; rescale through an explicit typed transformation")
    check("rounding/floating-point residue", epsilon is not None and
          0 < epsilon <= tolerance.numerical, Cause.NUMERICAL_NOISE,
          "Compare against separately declared numerical bound")
    check("information lost by inverse", bool(a.information_lost or b.information_lost),
          Cause.INFORMATION_LOSS, a.information_lost or b.information_lost or "No loss declared")
    check("non-invertible transform", True if False in (a.invertible, b.invertible)
          else False if a.invertible and b.invertible else None,
          Cause.NON_INVERTIBLE_TRANSFORM, "Inspect declared injectivity")
    check("invalid inverse domain", True if False in (a.inverse_domain_valid, b.inverse_domain_valid)
          else False if a.inverse_domain_valid and b.inverse_domain_valid else None,
          Cause.BAD_MIRROR, "Provide inverse domain and branch validation")
    check("wrong mirror operator", True if not compatible or False in (a.mirror_valid, b.mirror_valid)
          else False if a.mirror_valid and b.mirror_valid else None,
          Cause.BAD_MIRROR, "Validate entity, domain, function and mirror operator")
    check("perspective mismatch", left.perspective != right.perspective
          if left.perspective and right.perspective else None,
          Cause.SEMANTIC_MISMATCH, "Compare perspectives in a declared common frame")
    check("provenance conflict", None if not left.provenance or not right.provenance else
          left.id == right.id and left != right, Cause.PROVENANCE_CONFLICT,
          "Inspect source references and conflicting observation identifiers")
    check("genuine asymmetry", None, Cause.REAL_ASYMMETRY,
          "Independent observation distinguishing genuine asymmetry from measurement bias")
    check("model itself wrong", None, Cause.MODEL_FAILURE,
          "Falsifiable competing-model prediction and independent comparison")
    blockers = set(causes) - {Cause.NUMERICAL_NOISE.value, Cause.DEPENDENT_SOURCES.value}
    missing_context = any(c["result"] == "UNKNOWN" for c in checks if c["check"] in
                          {"wrong timestamp", "coordinate mismatch", "invalid inverse domain",
                           "wrong mirror operator", "perspective mismatch", "provenance conflict"})
    closed = epsilon is not None and epsilon <= tolerance.absolute and not blockers and not missing_context
    if closed and epsilon and Cause.NUMERICAL_NOISE.value not in causes:
        causes.append(Cause.TOLERANCE_EFFECT.value)
    state = Resolution.CLOSED if closed else Resolution.REMAP if Cause.BAD_MIRROR.value in causes else Resolution.OPEN
    if not closed and not blockers:
        causes.append(Cause.UNKNOWN.value)
    return {"epsilon": epsilon, "metric": "discrete equality" if isinstance(left.raw_value, str)
            else "absolute difference", "units": tolerance.units, "tolerance": asdict(tolerance),
            "uncertainty": {"a": left.uncertainty, "b": right.uncertainty,
                            "combination": "not combined; covariance unspecified"},
            "state": state.value, "causes": causes, "red_tests": checks,
            "status": "DER", "closure_scope": "declared checkpoint consistency only"}


def analyze(paths: tuple[PathTrace, ...], tolerances: dict[str, Tolerance], *,
            cross_domain_support: float = 0.0, persistence: float = 0.0) -> dict[str, Any]:
    if not 2 <= len(paths) <= 20 or len({p.id for p in paths}) != len(paths):
        raise ValueError("provide 2–20 paths with distinct IDs")
    if sum(len(p.steps) for p in paths) > 500:
        raise ValueError("maximum 500 steps per analysis")
    knots: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for path_a, path_b in combinations(paths, 2):
        steps_b = {s.checkpoint: s for s in path_b.steps}
        common = [s.checkpoint for s in path_a.steps if s.checkpoint in steps_b]
        if common != [s.checkpoint for s in path_b.steps if s.checkpoint in common]:
            raise ValueError("aligned checkpoints must have the same causal order")
        missing = sorted({s.checkpoint for s in path_a.steps} ^ set(steps_b))
        if missing or not common:
            gaps.append({"paths": [path_a.id, path_b.id], "status": "STOP",
                         "stop_reason": "Unaligned checkpoints cannot establish closure",
                         "next_observation": "Supply explicit checkpoint correspondence",
                         "checkpoints": missing})
        first_failed = None
        failed_bridge = None
        safe = None
        for a in path_a.steps:
            if a.checkpoint not in steps_b:
                continue
            if a.checkpoint not in tolerances:
                raise ValueError(f"missing tolerance for {a.checkpoint}")
            b = steps_b[a.checkpoint]
            result = compare_steps(a, b, tolerances[a.checkpoint])
            failed = result["state"] != "CLOSED"
            if failed and first_failed is None:
                first_failed = a.checkpoint
                failed_bridge = {"path_a": a.relation, "path_b": b.relation}
            epsilon = result["epsilon"]
            strength = 1.0 if epsilon is None else (
                min(1.0, epsilon / tolerances[a.checkpoint].absolute)
                if tolerances[a.checkpoint].absolute else float(epsilon > 0))
            if failed and not strength:
                strength = 1.0  # typed contradiction even if raw numbers match
            scores = score_components(a.observation, b.observation, strength,
                                      cross_domain_support, persistence)
            knots.append({**result, "id": f"knot-{len(knots) + 1:04d}",
                          "checkpoint": a.checkpoint, "path_a": path_a.id, "path_b": path_b.id,
                          "a": asdict(a), "b": asdict(b), "score_components": scores,
                          "confidence": min(a.observation.confidence, b.observation.confidence),
                          "first_failed_relation": first_failed, "last_safe_node": safe,
                          "first_failed_bridge": failed_bridge,
                          "quarantined": [{"relation": EdgeType.CANDIDATE_BRIDGE.value,
                                           "source": a.observation.id,
                                           "target": b.observation.id,
                                           "checkpoint": a.checkpoint}] if failed else [],
                          "decision": result["state"],
                          "stop_reason": "Causal explanation or typed bridge remains unverified"
                          if failed else None,
                          "next_observation": "Resolve detected RED checks; compare independent data"
                          if failed else "Repeat with independent observations",
                          "history": []})
            if not failed and first_failed is None:
                safe = a.observation.id
    return {"format": "upi-oden-knots", "version": "1.0", "status": "DER",
            "verification_type": "software_test", "claims_experimental_verification": False,
            "patch_not_erase": PATCH_NOT_ERASE, "paths": [asdict(p) for p in paths],
            "knots": knots, "alignment_gaps": gaps}
