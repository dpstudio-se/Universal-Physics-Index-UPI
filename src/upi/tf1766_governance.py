"""TF1766 governance reference for AI↔UPI Taurus.

Legal status is represented as provenance metadata, not as an automated legal
decision engine. Current Swedish law must be checked separately when applicable.
"""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TF1766Governance:
    historical_reference: str = "1766 års tryckfrihetsförordning"
    current_tf: str = "Tryckfrihetsförordning (1949:105)"
    current_ygl: str = "Yttrandefrihetsgrundlag (1991:1469)"
    preserve_provenance: bool = True
    preserve_disagreement: bool = True
    prohibit_silent_ai_suppression: bool = True
    legal_restrictions_require_basis: bool = True

    def policy_record(self) -> dict[str, object]:
        return {
            "historical_reference": self.historical_reference,
            "current_law_references": [self.current_tf, self.current_ygl],
            "principles": [
                "source_and_provenance",
                "free_exchange_and_all_sided_information",
                "traceable_transformations",
                "preserve_disagreement",
                "no_silent_ai_suppression",
                "lawful_restrictions_with_recorded_basis",
                "human_agency",
            ],
            "note": "Governance reference; not an automated legal ruling.",
        }