"""Durable append-only checkpoints for verified mirror-loop runs.

Checkpoints are audit/workload records, not canonical DNA promotion.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def save_mirror_checkpoint(
    root: Path,
    report: dict[str, Any],
    *,
    path: Path | None = None,
) -> dict[str, Any]:
    """Append one verified mirror-loop checkpoint and return its receipt.

    Every completed loop is persisted, including STOP/CONFLICT outcomes.
    The file is append-only JSONL and each record links to the previous
    checkpoint hash. This does not promote anything to canonical DNA.
    """
    destination = path or (root / "research" / "mirror_loop_checkpoints.jsonl")
    destination.parent.mkdir(parents=True, exist_ok=True)

    trace = report.get("trace", [])
    passed = [step for step in trace if step.get("state") == "PASS"]
    mirror_failures = []
    for step in passed:
        inverse = step.get("inverse")
        input_name = step.get("inverse_input")
        original = step.get("input_values", {}).get(input_name, {}).get("value")
        if original is None or inverse is None:
            mirror_failures.append({
                "address": step.get("address"),
                "reason": "missing inverse comparison value",
            })
            continue
        delta = inverse - original
        scale = max(abs(original), 1.0)
        mirror_failures.append({
            "address": step.get("address"),
            "inverse_input": input_name,
            "original": original,
            "mirror_back": inverse,
            "residual": delta,
            "relative_residual": abs(delta) / scale,
        })

    mirror_ok = bool(passed) and not mirror_failures
    if mirror_failures:
        mirror_ok = all(item.get("relative_residual", 1.0) <= 1e-12 for item in mirror_failures)

    body = {
        "schema_version": "1.0.0",
        "operation": "mirror_loop_checkpoint",
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "loop_state": report.get("state", "UNKNOWN"),
        "promotion": report.get("promotion", "BLOCKED"),
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "mirror": {
            "checked_steps": len(passed),
            "ok": mirror_ok,
            "results": mirror_failures,
        },
        "trace_sha256": hashlib.sha256(_canonical({"trace": trace})).hexdigest(),
        "report_sha256": hashlib.sha256(_canonical(report)).hexdigest(),
    }

    previous_hash = None
    if destination.exists():
        with destination.open("rb") as stream:
            for line in stream:
                if line.strip():
                    previous_hash = hashlib.sha256(line.rstrip(b"\n") + b"\n").hexdigest()
    body["previous_checkpoint_sha256"] = previous_hash
    line = _canonical(body)
    checkpoint_sha256 = hashlib.sha256(line).hexdigest()
    body["checkpoint_sha256"] = checkpoint_sha256
    serialized = _canonical(body) + b"\n"

    with destination.open("ab") as stream:
        stream.write(serialized)
        stream.flush()

    return body
