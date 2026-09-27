"""Optional evidence views that never mutate canonical scientific status."""

from __future__ import annotations

from typing import Any

ROBUSTNESS_LENS = "linked-robustness"


def status_through_lens(payload: dict[str, Any], lens: str | None = None) -> dict[str, Any]:
    """Assess linked tests for display while preserving the canonical record."""
    canonical = str(payload.get("status", "STOP"))
    view: dict[str, Any] = {
        "canonical_status": canonical,
        "display_status": canonical,
        "lens": "canonical",
        "promoted": False,
    }
    if lens != ROBUSTNESS_LENS:
        return view
    view["lens"] = ROBUSTNESS_LENS
    evidence = payload.get("linked_robustness_evidence")
    if not isinstance(evidence, dict):
        view["reason"] = "No structured linked robustness evidence"
        return view
    links = evidence.get("test_links")
    qualified = (
        isinstance(evidence.get("sample_size"), int)
        and evidence["sample_size"] > 0
        and evidence.get("failure_count") == 0
        and evidence.get("independence_documented") is True
        and evidence.get("criterion_predeclared") is True
        and bool(evidence.get("tested_domain"))
        and isinstance(links, list)
        and bool(links)
        and all(_valid_test_link(link) for link in links)
    )
    if canonical in {"HYP", "DER"} and qualified and isinstance(links, list):
        view.update(
            {
                "display_status": "EST-LINKED-ROBUSTNESS",
                "promoted": True,
                "reason": "Independent external tests support every declared link",
                "scope": evidence["tested_domain"],
                "test_link_count": len(links),
            }
        )
    else:
        view["reason"] = "Linked robustness criteria not satisfied"
    return view


def _valid_test_link(link: object) -> bool:
    if not isinstance(link, dict):
        return False
    return (
        bool(link.get("source_record"))
        and bool(link.get("target_record"))
        and link.get("relation") in {"MEASURED_BY", "SUPPORTED_BY", "REPLICATED_BY"}
        and bool(link.get("test_source"))
        and bool(link.get("tested_claim"))
    )
