"""Canonical merge: live/batch records into a review pack. Does not write data/."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from .contribute.service import ContributionService
from .index import load_graph
from .schema_resources import schema_path
from .validation import validate_bridge_json, validate_node_json, validate_record_boundaries


def _hash(payload: dict[str, Any]) -> str:
    import json

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def check_record(payload: dict[str, Any], record_type: str) -> list[str]:
    """Return validation errors for one untrusted record."""
    if record_type == "bridge":
        ok, errors = validate_bridge_json(payload, schema_path("bridge"))
        return errors if not ok else []
    ok, errors = validate_node_json(payload, schema_path("node"))
    if payload.get("status") == "EST":
        errors = [*errors, "canonical merge rejects EST without maintainer promote"]
    return errors if not ok or errors else validate_record_boundaries(payload)


def build_merge_pack(
    records: list[dict[str, Any]],
    *,
    canonical_root,
    owner: str = "maintainer",
) -> dict[str, Any]:
    """Build a durable merge pack. Never mutates the canonical tree."""
    graph = load_graph(canonical_root)
    existing = set(graph.get_all_nodes())
    items = []
    for record in records:
        payload = record.get("payload") if "payload" in record else record
        record_type = record.get("record_type") or (
            "bridge" if {"source", "target", "relation"} <= payload.keys() else "node"
        )
        address = str(payload.get("address") or f"{payload.get('source')}->{payload.get('target')}")
        if address in existing:
            errors = []
            decision = "duplicate"
        else:
            errors = check_record(payload, record_type)
            decision = "reject" if errors else "approve_candidate"
        items.append(
            {
                "address": address,
                "record_type": record_type,
                "status": payload.get("status"),
                "content_hash": _hash(payload),
                "decision": decision,
                "errors": errors,
            }
        )
    approved = [item for item in items if item["decision"] == "approve_candidate"]
    pack_decision = "escalate" if any(item["errors"] for item in items) else "advance"
    if not approved and pack_decision == "advance":
        pack_decision = "advance"
    return {
        "format": "upi-merge-pack",
        "version": "1.0.0",
        "owner": owner,
        "state": "CHECKED",
        "decision": pack_decision,
        "approval_required": True,
        "candidates": items,
        "approved_count": len(approved),
        "canonical_node_count": graph.get_node_count(),
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "confusion_guard": "A merge pack is a review artifact. It does not write data/ until a maintainer merges.",
    }


def merge_from_live(service: ContributionService, canonical_root) -> dict[str, Any]:
    """Check every live contribution against the canonical graph."""
    records = [
        {"record_type": item["record_type"], "payload": item["payload"]}
        for item in service.list_nodes(limit=1000)
    ]
    return build_merge_pack(records, canonical_root=canonical_root)
