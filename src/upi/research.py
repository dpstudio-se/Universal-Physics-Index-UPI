"""Permissive research-mode mapping for UPI.

Research mode is an exploration layer, not a promotion path. It preserves the
whole proposal, validates any embedded UPI node/bridge records, maps the
validated subset in a shadow report, and leaves unresolved or disconnected
material explicitly open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema_resources import schema_path
from .validation import validate_bridge_json, validate_node_json


def _record_validation(record: dict[str, Any]) -> tuple[str, list[str]]:
    """Validate an embedded UPI record without promoting it."""
    record_type = record.get("record_type")
    payload = record.get("payload")
    if record_type not in {"node", "bridge"} or not isinstance(payload, dict):
        return "OPEN", ["Research item has no valid node/bridge record envelope."]

    if record_type == "node":
        ok, errors = validate_node_json(payload, schema_path("node"))
    else:
        ok, errors = validate_bridge_json(payload, schema_path("bridge"))
    return ("PASS" if ok else "OPEN"), errors


def build_research_report(session: dict[str, Any]) -> dict[str, Any]:
    """Build a non-blocking research/shadow map from one session."""
    items = session.get("items", [])
    if not isinstance(items, list):
        items = []

    by_id: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    passed_ids: set[str] = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            results.append({
                "id": f"item-{index}",
                "state": "OPEN",
                "reason": "Research item is not an object.",
                "errors": ["invalid_item"],
            })
            continue

        item_id = str(item.get("id") or f"item-{index}")
        by_id[item_id] = item
        state, errors = _record_validation(item.get("record", {}))
        results.append({
            "id": item_id,
            "state": state,
            "title": item.get("title"),
            "kind": item.get("kind", "claim"),
            "links": item.get("links", []),
            "function": item.get("function"),
            "errors": errors,
        })
        if state == "PASS":
            passed_ids.add(item_id)

    edges: list[dict[str, Any]] = []
    degree: dict[str, int] = {item_id: 0 for item_id in by_id}

    for result in results:
        source = result["id"]
        links = result.get("links") or []
        if not isinstance(links, list):
            links = []
        for target in links:
            target_id = str(target)
            if target_id not in by_id:
                edges.append({
                    "source": source,
                    "target": target_id,
                    "state": "OPEN",
                    "reason": "Target is not present in this research session.",
                })
                continue
            edge_state = "PASS" if source in passed_ids and target_id in passed_ids else "OPEN"
            edges.append({
                "source": source,
                "target": target_id,
                "state": edge_state,
                "reason": (
                    "Both endpoints contain records that pass UPI validation."
                    if edge_state == "PASS"
                    else "Connection remains open until both endpoints validate."
                ),
            })
            degree[source] += 1
            degree[target_id] += 1

    connected_passed = {
        item_id for item_id, count in degree.items()
        if item_id in passed_ids and count > 0
    }

    adjacency: dict[str, set[str]] = {item_id: set() for item_id in by_id}
    for edge in edges:
        if edge["state"] == "PASS":
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])

    closed_subchains: list[list[str]] = []
    visited: set[str] = set()
    for start in sorted(connected_passed):
        if start in visited:
            continue
        stack = [start]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current] - visited))
        if len(component) >= 2:
            closed_subchains.append(sorted(component))

    open_threads = []
    for result in results:
        item_id = result["id"]
        if result["state"] != "PASS" or item_id not in connected_passed:
            reason = (
                "No validated connection in the current session."
                if result["state"] == "PASS"
                else "Validation or mapping is incomplete; keep this branch open."
            )
            open_threads.append({"id": item_id, "reason": reason})

    return {
        "schema_version": "0.1.0",
        "operation": "upi_research_mode",
        "mode": "research",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "input_trust": "untrusted",
        "promotion": "none",
        "session": {
            "id": session.get("session_id"),
            "intent": session.get("intent"),
            "source": session.get("source"),
        },
        "policy": {
            "exploration_is_non_blocking": True,
            "unknown_material_is_preserved": True,
            "validated_records_are_candidates_only": True,
            "unconnected_material_remains_open": True,
            "closed_loop_is_not_required": True,
            "status_promotion_is_disabled": True,
        },
        "items": results,
        "edges": edges,
        "shadow": {
            "validated_candidate_ids": sorted(passed_ids),
            "connected_validated_ids": sorted(connected_passed),
            "closed_subchains": closed_subchains,
            "open_threads": open_threads,
        },
        "confusion_guard": (
            "A passing software/schema validation establishes only that the "
            "record is internally valid for its declared UPI contract. It does "
            "not establish the physical claim."
        ),
    }


def load_research_session(path: Path) -> dict[str, Any]:
    """Load a JSON research session as untrusted data."""
    return json.loads(path.read_text(encoding="utf-8"))


def render_research_markdown(report: dict[str, Any]) -> str:
    """Render a compact research-mode report."""
    shadow = report["shadow"]
    lines = [
        "# UPI Research Mode",
        "",
        "Session: " + str(report["session"].get("id")),
        "Promotion: " + str(report["promotion"]),
        "Items: " + str(len(report["items"])),
        "Validated candidates: " + str(len(shadow["validated_candidate_ids"])),
        "Closed subchains: " + str(len(shadow["closed_subchains"])),
        "Open threads: " + str(len(shadow["open_threads"])),
        "",
        "## Principle",
        "",
        "Explore without requiring closure. Keep the validated subset visible in the shadow map,",
        "and leave disconnected, incomplete, or unresolved branches open for later work.",
        "",
        "## Validated candidates",
        "",
    ]
    for item_id in shadow["validated_candidate_ids"]:
        lines.append("- " + str(item_id))
    if not shadow["validated_candidate_ids"]:
        lines.append("- None yet.")
    lines.extend(["", "## Open threads", ""])
    for item in shadow["open_threads"]:
        lines.append("- " + str(item["id"]) + " — " + str(item["reason"]))
    if not shadow["open_threads"]:
        lines.append("- None.")
    lines.extend(["", "## Guard", "", report["confusion_guard"], ""])
    return "\n".join(lines)
