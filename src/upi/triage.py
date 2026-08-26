"""Compare a debug-index report to a known-finding catalog.

This is a software-test approval gate. It does not close scientific provenance
gaps and does not mutate index records.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def finding_key(finding: dict[str, Any]) -> tuple[str, str, str]:
    """Return the stable identity of one finding."""
    return (
        str(finding.get("code", "")),
        str(finding.get("status", "")),
        str(finding.get("path", "")),
    )


def catalog_keys(catalog: dict[str, Any]) -> set[tuple[str, str, str]]:
    """Return known finding identities from a catalog document."""
    return {finding_key(item) for item in catalog.get("findings", [])}


def compare_report(
    report: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, Any]:
    """Diff observed findings against the known catalog.

    Unexpected findings require approval. Missing catalog entries mean the
    baseline changed and also require review.
    """
    observed = [finding_key(item) for item in report.get("findings", [])]
    observed_set = set(observed)
    known = catalog_keys(catalog)
    unexpected = [
        item
        for item in report.get("findings", [])
        if finding_key(item) not in known
    ]
    missing = [
        {"code": code, "status": status, "path": path}
        for code, status, path in sorted(known - observed_set)
    ]
    decision = "advance"
    if unexpected or missing:
        decision = "escalate"
    return {
        "operation": "upi_index_triage",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "decision": decision,
        "approval_required": decision != "advance",
        "observed_findings": len(observed),
        "known_findings": len(known),
        "unexpected": unexpected,
        "missing": missing,
        "heartbeat": not unexpected and not missing,
    }


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from *path*."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data
