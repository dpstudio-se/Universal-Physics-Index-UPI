"""Immutable ODEN audit inputs; canonical UPI scientific records remain untouched."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from .models import ScientificStatus

PATCH_NOT_ERASE = True


class Resolution(str, Enum):
    CLOSED = "CLOSED"
    PATCH = "PATCH"
    REMAP = "REMAP"
    FLIP = "FLIP"
    OPEN = "OPEN"
    FALSIFIED = "FALSIFIED"


class Cause(str, Enum):
    NUMERICAL_NOISE = "NUMERICAL_NOISE"
    TOLERANCE_EFFECT = "TOLERANCE_EFFECT"
    INFORMATION_LOSS = "INFORMATION_LOSS"
    NON_INVERTIBLE_TRANSFORM = "NON_INVERTIBLE_TRANSFORM"
    BAD_MIRROR = "BAD_MIRROR"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    SEMANTIC_MISMATCH = "SEMANTIC_MISMATCH"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"
    DEPENDENT_SOURCES = "DEPENDENT_SOURCES"
    REAL_ASYMMETRY = "REAL_ASYMMETRY"
    MODEL_FAILURE = "MODEL_FAILURE"
    UNKNOWN = "UNKNOWN"


def bounded(value: float, name: str, upper: float = 1.0) -> None:
    if isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= upper:
        raise ValueError(f"{name} must be finite in [0, {upper}]")


@dataclass(frozen=True)
class Observation:
    id: str
    entity: str
    domain: str
    time: str
    location: str
    perspective: str
    name: str
    function: str
    source: str
    confidence: float
    raw_value: float | str
    units: str
    provenance: tuple[str, ...]
    uncertainty: float | None = None
    coordinate: str = "unspecified"
    source_group: str = ""
    source_quality: float = 0.0
    status: ScientificStatus = ScientificStatus.HYP

    def __post_init__(self) -> None:
        for field in (self.time, self.location, self.perspective, self.name, self.coordinate,
                      self.source_group):
            if not isinstance(field, str):
                raise ValueError("observation context fields must be strings")
        if not all(isinstance(v, str) and v for v in
                   (self.id, self.entity, self.domain, self.units, self.function, self.source)):
            raise ValueError("observation identity, type, units and source are required")
        if not isinstance(self.provenance, tuple) or not all(
            isinstance(v, str) for v in self.provenance
        ):
            raise ValueError("provenance must be an immutable tuple of source references")
        bounded(self.confidence, "confidence")
        bounded(self.source_quality, "source_quality")
        if isinstance(self.raw_value, bool) or not isinstance(self.raw_value, (int, float, str)):
            raise ValueError("raw_value must be a finite number or unnormalized string")
        if isinstance(self.raw_value, (int, float)) and not math.isfinite(self.raw_value):
            raise ValueError("raw_value must be finite")
        if self.uncertainty is not None:
            bounded(self.uncertainty, "uncertainty", float("inf"))


@dataclass(frozen=True)
class Step:
    checkpoint: str
    observation: Observation
    relation: str
    mirror: str
    input_id: str
    invertible: bool | None = None
    inverse_domain_valid: bool | None = None
    information_lost: str = ""
    mirror_valid: bool | None = None

    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v for v in
                   (self.checkpoint, self.relation, self.mirror, self.input_id)):
            raise ValueError("step requires checkpoint, relation, mirror and input ID")
        if not isinstance(self.information_lost, str):
            raise ValueError("information_lost must describe discarded information")
        for flag in (self.invertible, self.inverse_domain_valid, self.mirror_valid):
            if flag is not None and not isinstance(flag, bool):
                raise ValueError("transformation validity flags must be boolean or unknown")


@dataclass(frozen=True)
class PathTrace:
    id: str
    steps: tuple[Step, ...]

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.steps, tuple) or not self.steps:
            raise ValueError("path requires an ID and immutable nonempty steps")
        keys = [s.checkpoint for s in self.steps]
        if len(set(keys)) != len(keys) or any(not k for k in keys):
            raise ValueError("checkpoint keys must be unique and nonempty within a path")
        for previous, current in zip(self.steps, self.steps[1:], strict=False):
            if current.input_id != previous.observation.id:
                raise ValueError("each step must identify its preceding observation")


@dataclass(frozen=True)
class Tolerance:
    absolute: float
    units: str
    numerical: float = 0.0

    def __post_init__(self) -> None:
        bounded(self.absolute, "absolute tolerance", float("inf"))
        bounded(self.numerical, "numerical tolerance", self.absolute)
        if not self.units:
            raise ValueError("tolerance units required")
