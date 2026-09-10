"""Bounded executable projection of UPI relations, never execution of graph text.

Reference Dijkstra, two-sided search and basic customizable contraction hierarchy.
Each shortcut retains its ordered original edge IDs. Costs are optimization costs,
not scientific confidence. Unsupported scientific bridges remain impassable.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import asdict, dataclass

from .constants import C, H
from .models import ScientificStatus
from .resilience import content_hash


@dataclass(frozen=True)
class Transform:
    id: str
    source: str
    target: str
    input_unit: str
    output_unit: str
    equation: str
    factor: float
    reciprocal: bool
    status: ScientificStatus
    provenance: tuple[str, ...]
    assumptions: tuple[str, ...]
    inverse: str | None = None
    cost: float = 1.0

    def __post_init__(self) -> None:
        if (
            not self.provenance
            or not self.assumptions
            or not isinstance(self.status, ScientificStatus)
        ):
            raise ValueError("typed status, provenance and assumptions required")
        if (
            not math.isfinite(self.cost)
            or self.cost <= 0
            or not math.isfinite(self.factor)
            or self.factor <= 0
        ):
            raise ValueError("finite positive factors and routing costs required")

    @property
    def executable(self) -> bool:
        return self.status in (ScientificStatus.EST, ScientificStatus.DER)

    def apply(self, value: float) -> float:
        if not self.executable:
            raise ValueError("unsupported physical bridge")
        if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            raise ValueError("declared positive finite quantum-energy domain required")
        result = self.factor / value if self.reciprocal else self.factor * value
        if not math.isfinite(result) or result <= 0:
            raise ValueError("output outside representable domain")
        return result


# An arc is (cost, expanded ordered original edge IDs).
Arc = tuple[float, tuple[str, ...]]


def walk(arcs: dict[tuple[str, str], Arc], start: str) -> dict[str, Arc]:
    adjacency: dict[str, list[tuple[str, Arc]]] = {}
    for (u, v), arc in arcs.items():
        adjacency.setdefault(u, []).append((v, arc))
    found: dict[str, Arc] = {start: (0.0, ())}
    pending = [(0.0, start)]
    while pending:
        distance, u = heapq.heappop(pending)
        if distance != found[u][0]:
            continue
        for v, (weight, path) in adjacency.get(u, []):
            candidate = distance + weight
            if candidate < found.get(v, (math.inf, ()))[0]:
                found[v] = (candidate, found[u][1] + path)
                heapq.heappush(pending, (candidate, v))
    return found


class DerivationRouter:
    """Trusted primitive registry; immutable edge objects, fresh metric customization."""

    def __init__(self, edges: tuple[Transform, ...], order: tuple[str, ...] | None = None):
        self.edges = {e.id: e for e in edges}
        if len(self.edges) != len(edges):
            raise ValueError("duplicate transform ID")
        nodes = {e.source for e in edges} | {e.target for e in edges}
        self.order = tuple(sorted(nodes)) if order is None else order
        if len(self.order) != len(nodes) or set(self.order) != nodes:
            raise ValueError("contraction order must be a permutation of nodes")
        self.rank = {n: i for i, n in enumerate(self.order)}
        neighbors: dict[str, set[str]] = {n: set() for n in nodes}
        for e in edges:
            if e.source == e.target:
                raise ValueError("self transformation not supported")
            neighbors[e.source].add(e.target)
            neighbors[e.target].add(e.source)
        self.higher = {}
        # Metric-independent chordal completion (basic CCH preprocessing).
        for v in self.order:
            upper = tuple(sorted(n for n in neighbors[v] if self.rank[n] > self.rank[v]))
            self.higher[v] = upper
            for u in upper:
                neighbors[u].update(w for w in upper if w != u)
        self.version = content_hash([asdict(e) for e in edges])

    def metric(self, costs: dict[str, float] | None = None) -> dict[tuple[str, str], Arc]:
        costs = {} if costs is None else costs
        if set(costs) - set(self.edges):
            raise ValueError("unknown cost edge")
        result: dict[tuple[str, str], Arc] = {}
        for e in self.edges.values():
            weight = costs.get(e.id, e.cost)
            if isinstance(weight, bool) or not math.isfinite(weight) or weight <= 0:
                raise ValueError("positive finite costs required")
            if e.executable and weight < result.get((e.source, e.target), (math.inf, ()))[0]:
                result[e.source, e.target] = (weight, (e.id,))
        return result

    def customize(self, arcs: dict[tuple[str, str], Arc]) -> dict[tuple[str, str], Arc]:
        result = dict(arcs)
        # Lower-triangle relaxation, in increasing elimination order.
        for v in self.order:
            for u in self.higher[v]:
                for w in self.higher[v]:
                    if u == w or (u, v) not in result or (v, w) not in result:
                        continue
                    left, right = result[u, v], result[v, w]
                    candidate = left[0] + right[0]
                    if candidate < result.get((u, w), (math.inf, ()))[0]:
                        result[u, w] = (candidate, left[1] + right[1])
        return result

    def route(
        self,
        source: str,
        target: str,
        method: str = "dijkstra",
        costs: dict[str, float] | None = None,
    ) -> dict:
        if source not in self.rank or target not in self.rank:
            raise ValueError("unknown quantity identity")
        arcs = self.metric(costs)
        shortcuts = []
        if method == "dijkstra":
            best = walk(arcs, source).get(target)
        elif method in ("bidirectional", "cch"):
            if method == "cch":
                arcs = self.customize(arcs)
                shortcuts = [
                    {
                        "status": "DER",
                        "source": u,
                        "target": v,
                        "cost": a[0],
                        "expanded_edges": a[1],
                    }
                    for (u, v), a in arcs.items()
                    if len(a[1]) > 1
                ]
            forward = {
                k: a
                for k, a in arcs.items()
                if method != "cch" or self.rank[k[0]] < self.rank[k[1]]
            }
            backward = {
                (v, u): (cost, tuple(reversed(path)))
                for (u, v), (cost, path) in arcs.items()
                if method != "cch" or self.rank[v] < self.rank[u]
            }
            left, right = walk(forward, source), walk(backward, target)
            meetings = set(left) & set(right)
            meet = min(meetings, key=lambda n: (left[n][0] + right[n][0], n)) if meetings else None
            best = (
                None
                if meet is None
                else (
                    left[meet][0] + right[meet][0],
                    left[meet][1] + tuple(reversed(right[meet][1])),
                )
            )
        else:
            raise ValueError("unknown routing method")
        if best is None:
            reachable = walk(self.metric(costs), source)
            blocked = [
                asdict(e) for e in self.edges.values() if e.source in reachable and not e.executable
            ]
            return {
                "status": "STOP",
                "stop_reason": "No executable EST/DER route to requested identity",
                "next_observation": "Supply a physically justified, sourced bridge and its domain tests",
                "blocked_bridges": blocked,
                "source": source,
                "target": target,
                "method": method,
            }
        return {
            "status": "DER",
            "method": method,
            "source": source,
            "target": target,
            "cost": best[0],
            "expanded_edges": list(best[1]),
            "shortcuts": shortcuts,
            "graph_version": self.version,
            "verification_type": "software_test",
        }

    def derive(
        self,
        source: str,
        target: str,
        value: float,
        unit: str,
        *,
        provenance: tuple[str, ...],
        uncertainty: float | None = None,
        method: str = "dijkstra",
    ) -> dict:
        if not provenance:
            raise ValueError("input provenance required")
        if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            raise ValueError("positive finite input required")
        if uncertainty is not None and (
            isinstance(uncertainty, bool) or not math.isfinite(uncertainty) or uncertainty < 0
        ):
            raise ValueError("invalid uncertainty")
        units = {e.input_unit for e in self.edges.values() if e.source == source} | {
            e.output_unit for e in self.edges.values() if e.target == source
        }
        if units != {unit}:
            raise ValueError("unit does not match quantity identity")
        route = self.route(source, target, method)
        route["input"] = {
            "status": "DER",
            "value": value,
            "unit": unit,
            "uncertainty": uncertainty,
            "provenance": provenance,
            "domain": source,
            "scope": "declared input, not a sensor measurement",
        }
        if route["status"] == "STOP":
            return route
        trace = []
        for key in route["expanded_edges"]:
            e = self.edges[key]
            if e.source != source or e.input_unit != unit:
                raise ValueError("broken typed shortcut")
            out = e.apply(value)
            u = None if uncertainty is None else abs(out / value) * uncertainty
            trace.append(
                {
                    **asdict(e),
                    "input": value,
                    "output": out,
                    "output_uncertainty": u,
                    "constraints": ["positive finite scalar; named-energy referent"],
                    "tests": "tests/test_foundation.py",
                }
            )
            source, unit, value, uncertainty = e.target, e.output_unit, out, u
        route.update(
            trace=trace,
            output={
                "status": "DER",
                "value": value,
                "unit": unit,
                "uncertainty": uncertainty,
                "domain": target,
                "provenance": provenance,
            },
            uncertainty_method="first-order propagation; does not estimate missing input uncertainty",
        )
        return route


def physics_router() -> DerivationRouter:
    anchor = "UPI<information_physics,1,inertia,frequency_mass_equivalent>"
    definitions = (
        ("planck", "frequency", "energy", "Hz", "J", "E=h*f", H, False, "frequency_from_energy"),
        (
            "mass_equivalent",
            "energy",
            "mass_equivalent",
            "J",
            "kg",
            "m_eq=E/c^2",
            1 / C**2,
            False,
            "energy_from_mass",
        ),
        (
            "frequency_from_energy",
            "energy",
            "frequency",
            "J",
            "Hz",
            "f=E/h",
            1 / H,
            False,
            "planck",
        ),
        (
            "energy_from_mass",
            "mass_equivalent",
            "energy",
            "kg",
            "J",
            "E=m_eq*c^2",
            C**2,
            False,
            "mass_equivalent",
        ),
        (
            "wavelength",
            "frequency",
            "vacuum_wavelength",
            "Hz",
            "m",
            "lambda=c/f",
            C,
            True,
            "frequency_from_wavelength",
        ),
        (
            "frequency_from_wavelength",
            "vacuum_wavelength",
            "frequency",
            "m",
            "Hz",
            "f=c/lambda",
            C,
            True,
            "wavelength",
        ),
    )
    edges = tuple(
        Transform(
            i,
            s,
            t,
            iu,
            ou,
            eq,
            f,
            r,
            ScientificStatus.DER,
            (anchor,),
            ("same electromagnetic quantum and lab frame; vacuum wavelength",),
            inv,
        )
        for i, s, t, iu, ou, eq, f, r, inv in definitions
    )
    candidate = Transform(
        "dm_identity",
        "mass_equivalent",
        "dark_matter_particle",
        "kg",
        "kg",
        "m_chi ?= m_eq",
        1.0,
        False,
        ScientificStatus.HYP,
        ("UPI<open-problems,1,dark_matter,H_DM_octave_84>",),
        ("Independent particle identification is missing",),
    )
    return DerivationRouter(edges + (candidate,))
