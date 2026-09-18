"""T3MP3ST sandbox primitives for UPI.

T3MP3ST is a controlled perturbation layer. It records Shadow, Mirror and
Noise observations and returns a structured evidence packet. It does not
declare scientific truth or write directly to DNA.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class TempestObservation:
    channel: str
    value: float
    metadata: Mapping[str, Any]


def run_tempest(
    shadow: TempestObservation,
    mirror: TempestObservation,
    noise: TempestObservation,
) -> dict[str, Any]:
    """Compare three controlled observation channels."""
    channels = (shadow, mirror, noise)
    if {item.channel for item in channels} != {"shadow", "mirror", "noise"}:
        raise ValueError("channels must be shadow, mirror and noise")
    mirror_delta = abs(shadow.value - mirror.value)
    noise_delta = abs(shadow.value - noise.value)
    return {
        "status": "DER",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "observations": [item.__dict__ for item in channels],
        "mirror_delta": mirror_delta,
        "noise_delta": noise_delta,
        "reproducible_within_tolerance": mirror_delta,
        "interpretation_guard": "A small mirror delta is necessary but not sufficient for experimental verification.",
    }
