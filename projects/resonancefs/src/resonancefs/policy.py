"""Versioned Phi1766 policy; a software profile, not a physical constant."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .errors import PolicyError
from .hashing import digest_json


@dataclass(frozen=True)
class Phi1766Policy:
    policy_id: str = "Phi1766"
    version: str = "1.0.0"
    chunk_size: int = 65_536
    spectral_bins: int = 24
    max_samples: int = 4096
    inspect_below: float = 0.98
    quarantine_below: float = 0.82
    amplitude_weight: float = 0.50
    histogram_weight: float = 0.30
    phase_weight: float = 0.20

    def __post_init__(self) -> None:
        if self.policy_id != "Phi1766":
            raise PolicyError("policy_id must remain Phi1766 for this profile")
        if self.chunk_size < 1024:
            raise PolicyError("chunk_size must be at least 1024 bytes")
        if not 1 <= self.spectral_bins <= 128:
            raise PolicyError("spectral_bins must be between 1 and 128")
        if not 32 <= self.max_samples <= 65_536:
            raise PolicyError("max_samples must be between 32 and 65536")
        if not 0 <= self.quarantine_below < self.inspect_below <= 1:
            raise PolicyError("thresholds must satisfy 0 <= quarantine < inspect <= 1")
        total = self.amplitude_weight + self.histogram_weight + self.phase_weight
        if any(
            weight < 0
            for weight in (
                self.amplitude_weight,
                self.histogram_weight,
                self.phase_weight,
            )
        ) or abs(total - 1.0) > 1e-12:
            raise PolicyError("coherence weights must be nonnegative and sum to 1")

    @property
    def policy_hash(self) -> str:
        return digest_json(self.to_dict())

    def classify(self, score: float) -> str:
        if not 0 <= score <= 1:
            raise PolicyError("coherence score must be between 0 and 1")
        if score < self.quarantine_below:
            return "QUARANTINE"
        if score < self.inspect_below:
            return "INSPECT"
        return "NORMAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Phi1766Policy:
        try:
            return cls(**value)
        except TypeError as exc:
            raise PolicyError(f"invalid Phi1766 policy: {exc}") from exc

    @classmethod
    def load(cls, path: Path) -> Phi1766Policy:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise PolicyError("Phi1766 policy must be a JSON object")
        return cls.from_dict(value)
