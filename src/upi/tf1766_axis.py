"""TF1766→2026 constitutional-axis model.

This module is a formal/model layer. It does not itself determine legal liability,
constitutionality, or whether a concrete EU measure constitutes censorship.
It provides version-aware nodes, a temporal mirror, a reversible-loop test,
and a technical RNA/72-degree control fuse.
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
    """Apply the declared finite J-M-J-M representation."""
    if len(vector) != len(transform):
        raise ValueError("vector and transform must have equal length")
    sigma1 = transform
    sigma2 = mirror(sigma1)
    sigma3 = mirror(sigma2)
    return mirror(sigma3)


def compute_residual(
    original: tuple[object, ...],
    transformed_round_trip: tuple[object, ...],
) -> tuple[object, ...]:
    """Compute the componentwise symbolic residual Phi(Psi)-Psi."""
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


PHASE_STEP_DEG = 72.0
PHASE_COUNT = 5
ANALOG = "analog"
DIGITAL = "digital"
ON = "ON"
OFF = "OFF"
FORWARD = 1
REVERSE = -1


@dataclass(frozen=True)
class RNAMotorState:
    """Pure technical 72-degree control state; never a legal norm."""

    enabled: bool = False
    direction: int | None = FORWARD
    mode: str = ANALOG
    phase_index: int = 0
    frequency_hz: float | None = None
    genpol: float | None = None

    def __post_init__(self) -> None:
        if self.enabled and self.direction not in (FORWARD, REVERSE):
            raise ValueError("enabled motor direction must be +1 or -1")
        if not self.enabled and self.direction not in (FORWARD, REVERSE, None):
            raise ValueError("disabled motor direction must be +1, -1, or None")
        if self.mode not in (ANALOG, DIGITAL):
            raise ValueError("mode must be 'analog' or 'digital'")
        if not 0 <= self.phase_index < PHASE_COUNT:
            raise ValueError("phase_index must be in 0..4")

    @property
    def phase_deg(self) -> float:
        return self.phase_index * PHASE_STEP_DEG

    @property
    def signed_omega(self) -> int:
        """R_RNA: omega -> +/- omega; OFF gives zero."""
        if not self.enabled or self.direction is None:
            return 0
        return self.direction

    def step(self, count: int = 1) -> "RNAMotorState":
        """Advance by 72-degree steps; OFF is a hard freeze."""
        if count < 0:
            return self.step(-count)
        if not self.enabled or self.direction is None:
            return self
        phase = (self.phase_index + self.direction * count) % PHASE_COUNT
        return RNAMotorState(
            enabled=self.enabled,
            direction=self.direction,
            mode=self.mode,
            phase_index=phase,
            frequency_hz=self.frequency_hz,
            genpol=self.genpol,
        )

    def switch(
        self,
        *,
        enabled: bool | None = None,
        direction: int | None = None,
        mode: str | None = None,
        frequency_hz: float | None = None,
        genpol: float | None = None,
    ) -> "RNAMotorState":
        return RNAMotorState(
            enabled=self.enabled if enabled is None else enabled,
            direction=self.direction if direction is None else direction,
            mode=self.mode if mode is None else mode,
            phase_index=self.phase_index,
            frequency_hz=self.frequency_hz if frequency_hz is None else frequency_hz,
            genpol=self.genpol if genpol is None else genpol,
        )


@dataclass(frozen=True)
class ShadowEvent:
    enabled: bool
    direction: int | None
    phase_index: int
    phase_deg: float
    frequency_hz: float | None
    genpol: float | None
    rsym_zero: bool
    rns_zero: bool
    allowed: bool
    reason: str


class RNAFuse:
    """Technical ON/OFF, direction, frequency and genpol fuse."""

    def __init__(
        self,
        mirror: MirrorOperator,
        *,
        analog_frequency_hz: float = 7.834,
        digital_frequency_threshold_hz: float = 82000.0,
        genpol_reference: float = 0.136,
        genpol_tolerance: float = 1e-12,
        frequency_tolerance_hz: float = 1e-9,
    ) -> None:
        self.mirror = mirror
        self.analog_frequency_hz = analog_frequency_hz
        self.digital_frequency_threshold_hz = digital_frequency_threshold_hz
        self.genpol_reference = genpol_reference
        self.genpol_tolerance = genpol_tolerance
        self.frequency_tolerance_hz = frequency_tolerance_hz
        self.motor = RNAMotorState(enabled=False, direction=None)
        self.shadow_log: list[ShadowEvent] = []

    def configure(self, *, mode: str, freq: float, genpol: float) -> RNAMotorState:
        """Derive ON/OFF from mode, direction from frequency, with genpol hard gate."""
        if mode not in (ANALOG, DIGITAL):
            raise ValueError("mode must be 'analog' or 'digital'")

        if abs(genpol - self.genpol_reference) > self.genpol_tolerance:
            self.motor = RNAMotorState(
                enabled=False,
                direction=None,
                mode=mode,
                phase_index=self.motor.phase_index,
                frequency_hz=freq,
                genpol=genpol,
            )
            return self.motor

        enabled = mode == DIGITAL
        if abs(freq - self.analog_frequency_hz) <= self.frequency_tolerance_hz:
            direction: int | None = REVERSE
        elif freq >= self.digital_frequency_threshold_hz:
            direction = FORWARD
        else:
            direction = None

        if enabled and direction is None:
            enabled = False

        self.motor = RNAMotorState(
            enabled=enabled,
            direction=direction,
            mode=mode,
            phase_index=self.motor.phase_index,
            frequency_hz=freq,
            genpol=genpol,
        )
        return self.motor

    def set_motor(
        self,
        *,
        enabled: bool,
        direction: int | None = None,
        mode: str = ANALOG,
    ) -> RNAMotorState:
        self.motor = self.motor.switch(enabled=enabled, direction=direction, mode=mode)
        return self.motor

    def rotate(self, steps: int = 1) -> RNAMotorState:
        self.motor = self.motor.step(steps)
        return self.motor

    def gate(self, *, rsym_zero: bool, rns_zero: bool = True) -> bool:
        """Run the shadow gate; ON requires mirror closure, OFF freezes."""
        if not self.motor.enabled:
            allowed, reason = True, "motor_off_freeze"
        elif not rsym_zero:
            allowed, reason = False, "shadow_stop_nonzero_rsym"
        else:
            allowed, reason = True, "mirror_closed"
        self.shadow_log.append(
            ShadowEvent(
                self.motor.enabled,
                self.motor.direction,
                self.motor.phase_index,
                self.motor.phase_deg,
                self.motor.frequency_hz,
                self.motor.genpol,
                rsym_zero,
                rns_zero,
                allowed,
                reason,
            )
        )
        return allowed

    def apply(
        self,
        vector: tuple[object, ...],
        transform: tuple[object, ...],
        *,
        rsym_zero: bool,
        rns_zero: bool = True,
    ) -> tuple[object, ...]:
        if not self.gate(rsym_zero=rsym_zero, rns_zero=rns_zero):
            return vector
        if not self.motor.enabled:
            return vector
        return apply_loop(vector, transform, self.mirror)
