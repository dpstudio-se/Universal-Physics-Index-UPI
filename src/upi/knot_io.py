"""Versioned, deterministic JSON boundary. Imported text is never executed."""

from __future__ import annotations

import json
from typing import Any

from .knot import analyze
from .knot_model import Observation, PathTrace, Step, Tolerance
from .models import ScientificStatus


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def analyze_document(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != "upi-oden-paths" or document.get("version") != "1.0":
        raise ValueError("expected upi-oden-paths version 1.0")
    allowed = {"format", "version", "paths", "tolerances", "cross_domain_support", "persistence"}
    if set(document) - allowed:
        raise ValueError("unknown analysis fields")
    if not isinstance(document.get("paths"), list) or not 2 <= len(document["paths"]) <= 20:
        raise ValueError("provide 2–20 paths")
    if sum(len(p["steps"]) for p in document["paths"]) > 500:
        raise ValueError("maximum 500 steps")
    paths = []
    for path in document["paths"]:
        if set(path) != {"id", "steps"}:
            raise ValueError("path requires only id and steps")
        steps = []
        for raw_step in path["steps"]:
            raw = dict(raw_step["observation"])
            if not isinstance(raw.get("provenance"), list):
                raise ValueError("provenance must be a list")
            raw["provenance"] = tuple(raw["provenance"])
            raw["status"] = ScientificStatus(raw.get("status", "HYP"))
            step = {**raw_step, "observation": Observation(**raw)}
            for flag in ("invertible", "inverse_domain_valid", "mirror_valid"):
                if step.get(flag) is not None and not isinstance(step[flag], bool):
                    raise ValueError(f"{flag} must be boolean or null")
            steps.append(Step(**step))
        paths.append(PathTrace(path["id"], tuple(steps)))
    tolerances = {key: Tolerance(**value) for key, value in document["tolerances"].items()}
    return analyze(tuple(paths), tolerances,
                   cross_domain_support=document.get("cross_domain_support", 0.0),
                   persistence=document.get("persistence", 0.0))
