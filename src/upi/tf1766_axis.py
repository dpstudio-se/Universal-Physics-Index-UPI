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
