"""Load the canonical UPI index from JSON files into a graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .graph import UPIGraph
from .models import (
    Address,
    Bridge,
    EdgeType,
    EvidenceRecord,
    InformationLayer,
    PhysicsNode,
    Quantity,
    ScientificStatus,
    VerificationType,
)


def iter_records(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Yield JSON objects under *root*, skipping invalid and source manifests."""
    records: list[tuple[Path, dict[str, Any]]] = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*.json")):
        if path.name.startswith("invalid_"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if str(data.get("operation") or "").startswith("upi_external_source"):
            continue
        records.append((path, data))
    return records


def classify(data: dict[str, Any]) -> str | None:
    """Return node, bridge, or theory."""
    if {"source", "target", "relation"} <= data.keys():
        return "bridge"
    if {"address", "title", "status"} <= data.keys():
        if {"domain", "scope"} <= data.keys() and "key_concepts" in data:
            return "theory"
        return "node"
    return None


def node_from_json(data: dict[str, Any]) -> PhysicsNode:
    """Build a PhysicsNode from a JSON record (nodes and theories)."""
    quantities = []
    for item in data.get("quantities") or []:
        if isinstance(item, dict) and {"name", "value", "unit"} <= item.keys():
            quantities.append(
                Quantity(
                    name=str(item["name"]),
                    value=float(item["value"]),
                    unit=str(item["unit"]),
                    uncertainty=item.get("uncertainty"),
                    reference=item.get("reference"),
                )
            )
    evidence = []
    for item in data.get("evidence") or []:
        if isinstance(item, dict) and {"type", "source"} <= item.keys():
            evidence.append(
                EvidenceRecord(
                    type=str(item["type"]),
                    source=str(item["source"]),
                    confidence=item.get("confidence"),
                )
            )
    layer = data.get("information_layer")
    vtype = data.get("verification_type")
    return PhysicsNode(
        address=Address.from_string(str(data["address"])),
        title=str(data["title"]),
        description=str(data["description"]),
        status=ScientificStatus(str(data["status"])),
        quantities=quantities,
        definitions=list(data.get("definitions") or []),
        equations=list(data.get("equations") or data.get("fundamental_equations") or []),
        assumptions=list(data.get("assumptions") or []),
        evidence=evidence,
        primary_sources=list(data.get("primary_sources") or []),
        predictions=list(data.get("predictions") or []),
        falsification_conditions=list(data.get("falsification_conditions") or []),
        information_layer=InformationLayer(layer) if layer else InformationLayer.PUBLIC,
        verification_type=VerificationType(vtype) if vtype else VerificationType.NONE,
        claims_experimental_verification=bool(data.get("claims_experimental_verification")),
        confusion_guard=data.get("confusion_guard"),
        stop_reason=data.get("stop_reason"),
        tags=list(data.get("tags") or []),
        version=str(data.get("version") or "0.1.0"),
    )


def bridge_from_json(data: dict[str, Any]) -> Bridge:
    """Build a Bridge from JSON."""
    evidence = []
    for item in data.get("evidence") or []:
        if isinstance(item, dict) and {"type", "source"} <= item.keys():
            evidence.append(EvidenceRecord(type=str(item["type"]), source=str(item["source"])))
    return Bridge(
        source=Address.from_string(str(data["source"])),
        target=Address.from_string(str(data["target"])),
        relation=EdgeType(str(data["relation"])),
        equations=list(data.get("equations") or []),
        assumptions=list(data.get("assumptions") or []),
        evidence=evidence,
        status=ScientificStatus(str(data["status"])),
        confusion_guard=data.get("confusion_guard"),
        stop_reason=data.get("stop_reason"),
        version=str(data.get("version") or "0.1.0"),
    )


def load_graph(root: Path) -> UPIGraph:
    """Load every classifiable record under *root* into a graph."""
    graph = UPIGraph()
    bridges: list[dict[str, Any]] = []
    for _path, data in iter_records(root):
        kind = classify(data)
        if kind in {"node", "theory"}:
            node = node_from_json(data)
            if str(node.address) not in graph.get_all_nodes():
                graph.add_node(node)
        elif kind == "bridge":
            bridges.append(data)
    for data in bridges:
        graph.add_bridge(bridge_from_json(data))
    return graph


def hypothesis_registry(root: Path) -> list[dict[str, Any]]:
    """Return HYP records with falsification metadata."""
    rows = []
    for path, data in iter_records(root):
        if data.get("status") != "HYP":
            continue
        rows.append(
            {
                "address": data.get("address"),
                "title": data.get("title"),
                "path": path.as_posix(),
                "falsification_conditions": data.get("falsification_conditions") or [],
                "predictions": data.get("predictions") or [],
                "verification_type": data.get("verification_type") or "none",
            }
        )
    return rows


def export_graph(graph: UPIGraph) -> dict[str, Any]:
    """Full-field export used for round-trip software tests."""
    nodes = {}
    for address, node in graph.get_all_nodes().items():
        nodes[address] = {
            "address": address,
            "title": node.title,
            "description": node.description,
            "status": node.status.value,
            "equations": list(node.equations),
            "assumptions": list(node.assumptions),
            "confusion_guard": node.confusion_guard,
            "version": node.version,
        }
    bridges = [
        {
            "source": str(bridge.source),
            "target": str(bridge.target),
            "relation": bridge.relation.value,
            "status": bridge.status.value,
        }
        for bridge in graph.get_all_bridges()
    ]
    return {
        "nodes": nodes,
        "bridges": bridges,
        "stats": {
            "node_count": graph.get_node_count(),
            "bridge_count": graph.get_bridge_count(),
        },
        "verification_type": "software_test",
    }
