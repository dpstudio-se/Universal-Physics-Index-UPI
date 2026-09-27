"""Route canonical DNA records to existing RNA presentation surfaces."""

from __future__ import annotations

from typing import Any


def classify_rna_surface(record: dict[str, Any]) -> tuple[str, str]:
    """Return an existing presentation surface or request human review."""
    if {"source", "target", "relation"} <= record.keys():
        return "Graph/Catalog (auto)", "Typed bridge; Graph and Catalog can transcribe it"
    if {"address", "title", "description", "status"} <= record.keys():
        if record["status"] == "STOP":
            return "Catalog + STOP desk (auto)", "Typed STOP node; existing correction desk applies"
        return "Catalog/Graph (auto)", "Typed node; existing generic surfaces apply"
    if str(record.get("operation") or "").startswith("upi_external_source"):
        return (
            "Provenance docs (auto)",
            "External-source metadata; use existing provenance/index documentation",
        )
    return "needs-surface", "Unrecognized record shape; review RNA UI inbox"
