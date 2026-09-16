"""TF1766→2026 constitutional-axis model.

This module is a formal/model layer. It does not itself determine legal liability,
constitutionality, or whether a concrete EU measure constitutes censorship.
It provides version-aware nodes, a temporal mirror, and a reversible-loop test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


HIST = "HIST"
EST_CURRENT = "EST_CURRENT"
EST_SOURCE = "EST_SOURCE"
HYP = "HYP"
SYM = "SYM"


@dataclass(frozen=True)
class ConstitutionalNode:
    """One dated constitutional/rule-of-law source node."""

    label: str
    year: int
    status: str
    source_type: str
    effective_from: str | None = None
    effective_to: str | None = None

    def applies_at(self, date_iso: str) -> bool:
        """Return whether this version is marked effective at a given ISO date."""
        if self.status != EST_CURRENT:
            return False
        if self.effective_from and date_iso < self.effective_from:
            return False
        if self.effective_to and date_iso >= self.effective_to:
            return False
        return True


DEFAULT_AXIS: tuple[ConstitutionalNode, ...] = (
    ConstitutionalNode("TF1766", 1766, HIST, "historical_constitution"),
    ConstitutionalNode("RF1809", 1809, HIST, "historical_constitution"),
    ConstitutionalNode("TF1949_RF1949", 1949, HIST, "historical_version"),
    ConstitutionalNode("RF1974", 1974, HIST, "historical_version"),
    ConstitutionalNode("TF_YGL1992", 1992, HIST, "historical_version"),
    ConstitutionalNode("KU21_1993_94", 1994, EST_SOURCE, "preparatory_work"),
    ConstitutionalNode("CURRENT", 2026, EST_CURRENT, "current_consolidated_law"),
)


class TFAxis:
    """Versioned constitutional time axis."""

    def __init__(self, nodes: Iterable[ConstitutionalNode] = DEFAULT_AXIS) -> None:
        ordered = tuple(nodes)
        if not ordered:
            raise ValueError("axis must contain at least one node")
        if [n.year for n in ordered] != sorted(n.year for n in ordered):
            raise ValueError("axis nodes must be ordered by year")
        self.nodes = ordered

    def current(self) -> ConstitutionalNode:
        """Return the node designated as current law."""
        current = [n for n in self.nodes if n.status == EST_CURRENT]
        if len(current) != 1:
            raise ValueError("axis must contain exactly one EST_CURRENT node")
        return current[0]

    def mirror_index(self, index: int) -> int:
        """Apply J(i)=n-1-i to the finite axis."""
        n = len(self.nodes)
        if index < 0 or index >= n:
            raise IndexError("axis index out of range")
        return n - 1 - index

    def mirror(self, node: ConstitutionalNode) -> ConstitutionalNode:
        """Return the mirrored node."""
        try:
            index = self.nodes.index(node)
        except ValueError as exc:
            raise ValueError("node is not part of this axis") from exc
        return self.nodes[self.mirror_index(index)]


class MirrorOperator:
    """Finite mirror operator J on the TF axis."""

    def __init__(self, axis: TFAxis) -> None:
        self.axis = axis

    def __call__(self, vector: tuple[object, ...]) -> tuple[object, ...]:
        if len(vector) != len(self.axis.nodes):
            raise ValueError("vector length must match axis length")
        return tuple(vector[self.axis.mirror_index(i)] for i in range(len(vector)))

    def square(self, vector: tuple[object, ...]) -> tuple[object, ...]:
        """Verify J²(v)=v by direct application."""
        return self(self(vector))


@dataclass(frozen=True)
class NormTransform:
    """Declared norm transformation inputs; conclusions are intentionally absent."""

    exact_provision: str
    exact_obligation: str
    actor: str
    relevant_time: str
    action: str
    publication_timing: str
    medium: str
    classification: str = HYP


@dataclass(frozen=True)
class MirrorResult:
    """Output of the abstract mirror-loop consistency check."""

    invariant: bool
    rsym_is_zero: bool
    flag: bool
    note: str


def apply_loop(vector: tuple[object, ...], transform: tuple[object, ...], mirror: MirrorOperator) -> tuple[object, ...]:
    """Apply J M J M using a concrete finite vector representation.

    ``transform`` is represented as a same-length output vector. This is a
    computational test representation, not a legal interpretation of M.
    """
    if len(vector) != len(transform):
        raise ValueError("vector and transform must have equal length")
    sigma1 = transform
    sigma2 = mirror(sigma1)
    sigma3 = mirror(sigma2)
    # J M J M is represented by reapplying the declared transformed state and
    # mirrors; callers should use the explicit residual if a different M model
    # is required.
    return mirror(sigma3)


def compute_residual(
    original: tuple[object, ...],
    transformed_round_trip: tuple[object, ...],
) -> tuple[object, ...]:
    """Compute the componentwise symbolic residual ΦΨ−Ψ."""
    if len(original) != len(transformed_round_trip):
        raise ValueError("residual operands must have equal length")
    residual: list[object] = []
    for a, b in zip(transformed_round_trip, original, strict=True):
        try:
            residual.append(a - b)  # type: ignore[operator]
        except TypeError:
            residual.append((a, b))
    return tuple(residual)


def mirror_involution_holds(axis: TFAxis) -> bool:
    """Check J²=I over all axis basis vectors."""
    mirror = MirrorOperator(axis)
    n = len(axis.nodes)
    for i in range(n):
        basis = tuple(1 if j == i else 0 for j in range(n))
        if mirror.square(basis) != basis:
            return False
    return True
\nPHASE_STEP_DEG = 72.0\nPHASE_COUNT = 5\nPHASE_CLOSURE_INDEX = 5\n\nANALOG = "analog"\nDIGITAL = "digital"\nON = "ON"\nOFF = "OFF"\nFORWARD = 1\nREVERSE = -1\n\n@dataclass(frozen=True)\nclass RNAMotorState:\n    """Pure technical 72-degree control state; never a legal norm."""\n    enabled: bool = False\n    direction: int = FORWARD\n    mode: str = ANALOG\n    phase_index: int = 0\n\n    def __post_init__(self) -> None:\n        if self.direction not in (FORWARD, REVERSE):\n            raise ValueError("direction must be +1 or -1")\n        if self.mode not in (ANALOG, DIGITAL):\n            raise ValueError("mode must be 'analog' or 'digital'")\n        if not 0 <= self.phase_index <= PHASE_CLOSURE_INDEX:\n            raise ValueError("phase_index must be in 0..5")\n\n    @property\n    def phase_deg(self) -> float:\n        return self.phase_index * PHASE_STEP_DEG\n\n    @property\n    def signed_omega(self) -> int:\n        """R_RNA: omega -> +/- omega; OFF gives zero."""\n        return 0 if not self.enabled else self.direction\n\n    def step(self, count: int = 1) -> "RNAMotorState":\n        """Advance by 72-degree steps; 360-degree closure maps to phase 0."""\n        if count < 0:\n            return self.step(-count)\n        if not self.enabled:\n            return self\n        phase = (self.phase_index + self.direction * count) % PHASE_COUNT\n        return RNAMotorState(self.enabled, self.direction, self.mode, phase)\n\n    def switch(self, *, enabled: bool | None = None, direction: int | None = None, mode: str | None = None) -> "RNAMotorState":\n        return RNAMotorState(self.enabled if enabled is None else enabled, self.direction if direction is None else direction, self.mode if mode is None else mode, self.phase_index)\n\n@dataclass(frozen=True)\nclass ShadowEvent:\n    enabled: bool\n    direction: int\n    phase_index: int\n    phase_deg: float\n    rsym_zero: bool\n    rns_zero: bool\n    allowed: bool\n    reason: str\n\nclass RNAFuse:\n    """Fuse the technical 72-degree motor to the TF1766 mirror gate."""\n    def __init__(self, mirror: MirrorOperator) -> None:\n        self.mirror = mirror\n        self.motor = RNAMotorState()\n        self.shadow_log: list[ShadowEvent] = []\n\n    def set_motor(self, *, enabled: bool, direction: int = FORWARD, mode: str = ANALOG) -> RNAMotorState:\n        self.motor = self.motor.switch(enabled=enabled, direction=direction, mode=mode)\n        return self.motor\n\n    def rotate(self, steps: int = 1) -> RNAMotorState:\n        self.motor = self.motor.step(steps)\n        return self.motor\n\n    def gate(self, *, rsym_zero: bool, rns_zero: bool = True) -> bool:\n        """ON requires mirror closure; OFF freezes; direction never bypasses the gate."""\n        if not self.motor.enabled:\n            allowed, reason = True, "motor_off_freeze"\n        elif not rsym_zero:\n            allowed, reason = False, "shadow_stop_nonzero_rsym"\n        else:\n            allowed, reason = True, "mirror_closed"\n        self.shadow_log.append(ShadowEvent(self.motor.enabled, self.motor.direction, self.motor.phase_index, self.motor.phase_deg, rsym_zero, rns_zero, allowed, reason))\n        return allowed\n\n    def apply(self, vector: tuple[object, ...], transform: tuple[object, ...], *, rsym_zero: bool, rns_zero: bool = True) -> tuple[object, ...]:\n        if not self.gate(rsym_zero=rsym_zero, rns_zero=rns_zero):\n            return vector\n        if not self.motor.enabled:\n            return vector\n        return apply_loop(vector, transform, self.mirror)\n