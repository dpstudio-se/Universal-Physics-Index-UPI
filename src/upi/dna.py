"""Read the entire DNA catalog; execute only explicitly registered typed relations.

JSON equations never become Python code. Unknown laws remain searchable/open.
Adapters are trusted validation code, separately versioned from untrusted records.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import H
from .dimensions import equation_dimensions_match
from .index import classify
from .physics import (
    angular_frequency,
    energy_from_frequency,
    frequency_from_mass,
    mass_from_frequency,
    period_from_frequency,
    phase_from_frequency,
    spiral_time_from_frequency,
)
from .schema_resources import schema_path
from .validation import validate_node_json


@dataclass(frozen=True)
class Value:
    value: float
    unit: str
    status: str = "DER"

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not math.isfinite(self.value):
            raise ValueError("Quantity must be a finite number")
        if self.status not in {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}:
            raise ValueError("Unknown scientific status")


@dataclass(frozen=True)
class Relation:
    """A reviewed function, its exact DNA equation, and typed input/output roles."""

    address: str
    equation: str
    inputs: tuple[tuple[str, str], ...]
    output: tuple[str, str]
    forward: Callable[[Mapping[str, float]], float]
    inverse: Callable[[float, Mapping[str, float]], float]
    inverse_input: str
    assumption: str


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


class DNAReader:
    def analyze_dynamic(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Analyze new sampled input using the existing spiral-flow engine.

        Frequencies are supplied or explicitly estimated from crossings, never
        selected from the reference catalog. The result is a proposal, not a write.
        """
        from .spiral_flow import (
            DetectionPolicy,
            NavierMode,
            estimate_crossing_frequency,
            run_dynamic_series,
        )

        if payload.get("format") != "upi-dynamic-series" or not payload.get("source"):
            raise ValueError("Require format=upi-dynamic-series and a declared source")
        times = payload["times_s"]
        estimate = None
        if payload.get("input_kind") == "frequency_series":
            frequencies = payload["frequencies_hz"]
        elif payload.get("input_kind") == "single_component_crossings":
            estimate = estimate_crossing_frequency(
                times, payload["amplitudes"], crossing_level=payload["crossing_level"]
            )
            times, frequencies = estimate["times_s"], estimate["frequencies_hz"]
        else:
            raise ValueError(
                "STOP: declare frequency_series or the single_component_crossings model"
            )
        control = payload["control"]
        report = run_dynamic_series(
            times,
            frequencies,
            initial_positions=tuple(tuple(p) for p in control["initial_positions"]),
            phase0_rad=control["phase0_rad"],
            density=control["density_kg_m3"],
            viscosity=control["kinematic_viscosity_m2_s"],
            force_mode=control["force_mode"],
            residual_tolerance=control["residual_tolerance_m_s2"],
            detection=DetectionPolicy(**payload["detection"]),
            modes=tuple(NavierMode(mode) for mode in payload.get("modes", list(NavierMode))),
            response_amplitudes=payload.get("response_amplitudes"),
        )
        input_hash = _hash(json.dumps(payload, sort_keys=True, allow_nan=False).encode())
        report.update(
            input_sha256=input_hash,
            input_source=payload["source"],
            input_snapshot=payload,
            frequency_estimation=estimate,
            dna_inventory=self.inventory,
            dna_sources=self.sources,
            code_sha256={
                name: _hash(Path(__file__).with_name(name).read_bytes())
                for name in ("dna.py", "spiral_flow.py", "physics.py", "constants.py")
            },
        )
        candidates = []
        for index, feature in enumerate(report["dynamic_nodes"]):
            node = {
                "address": f"UPI<information_physics,1,dynamic_signal,{input_hash[:16]}_{index}>",
                "title": "Dynamic sample feature: " + feature["kind"],
                "description": "Algorithmic feature in the supplied series, not an established resonance.",
                "status": "DER",
                "version": "0.1.0",
                "tags": ["DYNAMIC", feature["kind"]],
                "quantities": [
                    {"name": "time", "value": feature["t"], "unit": "s"},
                    {"name": "frequency", "value": feature["f"], "unit": "Hz"},
                ],
                "assumptions": [
                    "Sampling and explicitly supplied detection thresholds define the feature"
                ],
                "primary_sources": [payload["source"], "sha256:" + input_hash],
                "evidence": [
                    {"type": "calculation", "source": json.dumps(feature, sort_keys=True)}
                ],
                "falsification_conditions": [
                    "Recomputation from the same samples fails the feature criterion"
                ],
                "verification_type": "software_test",
                "claims_experimental_verification": False,
            }
            ok, errors = validate_node_json(node, schema_path("node"))
            if not ok:
                raise ValueError("Invalid dynamic candidate: " + "; ".join(errors))
            candidates.append(node)
        report["candidates"] = candidates
        return report

    def __init__(self, root: Path, relations: tuple[Relation, ...] = ()):
        self.root = root
        self.relations = relations
        self.records: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, dict[str, str]] = {}
        self.inventory: list[dict[str, Any]] = []
        if not root.is_dir():
            raise ValueError("DNA root is unavailable")
        duplicates: set[str] = set()
        for path in sorted(root.rglob("*.json")):
            entry: dict[str, Any] = {"path": path.relative_to(root).as_posix()}
            try:
                raw = path.read_bytes()
                entry["sha256"] = _hash(raw)
                record = json.loads(raw, object_pairs_hook=_unique_object)
                if not isinstance(record, dict):
                    raise ValueError("Expected object")
                entry.update(
                    kind=classify(record),
                    status=record.get("status"),
                    address=record.get("address"),
                    state="OPEN",
                )
                address = record.get("address")
                if address is not None and not isinstance(address, str):
                    entry["address"] = None
                    raise ValueError("Legacy or invalid address shape; no executable adapter")
                if address:
                    if address in self.records or address in duplicates:
                        duplicates.add(address)
                        self.records.pop(address, None)
                        self.sources.pop(address, None)
                        raise ValueError("Duplicate address; all copies excluded from execution")
                    self.records[address] = record
                    self.sources[address] = {
                        "path": entry["path"],
                        "sha256": entry["sha256"],
                        "version": str(record.get("version", "unknown")),
                    }
            except (OSError, ValueError) as exc:
                entry.update(state="OPEN", reason=str(exc))
            self.inventory.append(entry)

    def derive(self, inputs: Mapping[str, Value]) -> dict[str, Any]:
        """Forward closure with inverse checks; conflicts never overwrite supplied values."""
        values = dict(inputs)
        trace: list[dict[str, Any]] = []
        pending = list(self.relations)
        while pending:
            progressed = False
            for relation in list(pending):
                if not all(name in values for name, _ in relation.inputs):
                    continue
                pending.remove(relation)
                progressed = True
                row: dict[str, Any] = {
                    "address": relation.address,
                    "equation": relation.equation,
                    "inputs": dict(relation.inputs),
                    "output": relation.output,
                    "verification_type": "software_test",
                    "status": "STOP",
                }
                trace.append(row)
                try:
                    record = self.records.get(relation.address)
                    if record is None:
                        raise ValueError("Missing or ambiguous DNA dependency")
                    ok, errors = validate_node_json(record, schema_path("node"))
                    if not ok:
                        raise ValueError("Invalid DNA record: " + "; ".join(errors))
                    if relation.equation not in record.get("equations", []):
                        raise ValueError("DNA equation differs from reviewed adapter")
                    if relation.assumption not in record.get("assumptions", []):
                        raise ValueError("DNA assumption differs from reviewed adapter")
                    expression = relation.equation.split("=", 1)[1].strip()
                    expression = (
                        expression.replace("h f", "h*f").replace("×", "*").replace("^", "**")
                    )
                    if not equation_dimensions_match(
                        expression, dict(relation.inputs), relation.output[1]
                    ):
                        raise ValueError("Equation dimensions incompatible with typed ports")
                    if record["status"] in {"STOP", "ERR"}:
                        raise ValueError("Dependency status blocks execution")
                    for name, unit in relation.inputs:
                        if values[name].unit != unit:
                            raise ValueError(f"Unit mismatch: {name} requires {unit}")
                        if values[name].status in {"STOP", "ERR"}:
                            raise ValueError(f"Input {name} is blocked")
                    scalar = {name: values[name].value for name, _ in relation.inputs}
                    row["input_values"] = {name: vars(values[name]) for name, _ in relation.inputs}
                    result = relation.forward(scalar)
                    if not math.isfinite(result):
                        raise ValueError("Output exceeds floating-point range")
                    inverse = relation.inverse(result, scalar)
                    if not math.isclose(
                        inverse, scalar[relation.inverse_input], rel_tol=1e-12, abs_tol=0
                    ):
                        raise ValueError("Inverse check failed")
                    statuses = {record["status"], *(values[n].status for n, _ in relation.inputs)}
                    status = "HYP" if "HYP" in statuses else "SYM" if "SYM" in statuses else "DER"
                    name, unit = relation.output
                    if name in values:
                        old = values[name]
                        if old.unit != unit or not math.isclose(
                            old.value, result, rel_tol=1e-12, abs_tol=0
                        ):
                            values[name] = Value(old.value, old.unit, "STOP")
                            raise ValueError(f"CONFLICT: supplied {name} disagrees with derivation")
                    else:
                        values[name] = Value(result, unit, status)
                    row.update(
                        state="PASS",
                        status=status,
                        result=result,
                        inverse=inverse,
                        source=self.sources[relation.address],
                        assumption=relation.assumption,
                        assumptions=record.get("assumptions", []),
                    )
                except (ValueError, ArithmeticError) as exc:
                    row.update(
                        state="STOP",
                        stop_reason=str(exc),
                        next_action="Supply valid compatible inputs and the reviewed DNA dependency",
                    )
            if not progressed:
                break
        for relation in pending:
            trace.append(
                {
                    "address": relation.address,
                    "state": "STOP",
                    "status": "STOP",
                    "stop_reason": "Missing inputs: "
                    + ", ".join(n for n, _ in relation.inputs if n not in values),
                    "next_action": "Supply the named quantities with declared units and provenance",
                }
            )
        registered = {r.address for r in self.relations}
        return {
            "operation": "upi_dna_derivation",
            "verification_type": "software_test",
            "promotion": "BLOCKED",
            "claims_experimental_verification": False,
            "state": "STOP" if not trace or any(t["state"] != "PASS" for t in trace) else "PASS",
            "values": {n: vars(v) for n, v in values.items()},
            "trace": trace,
            "inventory": self.inventory,
            "open_records": [r for r in self.inventory if r.get("address") not in registered],
            "validation_code_sha256": _hash(Path(__file__).read_bytes()),
        }

    def candidate_nodes(self, report: dict[str, Any]) -> list[dict[str, Any]]:
        """Existing node schema, one calculation claim per node; no canonical writes."""
        result = []
        run_hash = _hash(json.dumps(report, sort_keys=True, allow_nan=False).encode())
        for index, step in enumerate(report["trace"]):
            node: dict[str, Any] = {
                "address": f"UPI<information_physics,1,rna_result,step_{index}_{run_hash[:16]}>",
                "title": "RNA result: " + step["address"],
                "description": "Conditional computation from declared inputs and a pinned DNA record.",
                "status": step["status"],
                "version": "0.1.0",
                "verification_type": "software_test",
                "claims_experimental_verification": False,
                "primary_sources": [step["address"]],
                "assumptions": step.get("assumptions", ["Named dependency remains unresolved"]),
                "falsification_conditions": ["Inverse, units or source binding fails"],
                "evidence": [{"type": "calculation", "source": json.dumps(step, sort_keys=True)}],
            }
            if step["state"] == "PASS":
                name, unit = step["output"]
                node.update(
                    equations=[step["equation"]],
                    quantities=[{"name": name, "value": step["result"], "unit": unit}],
                )
            else:
                node["stop_reason"] = step["stop_reason"] + "; " + step["next_action"]
            ok, errors = validate_node_json(node, schema_path("node"))
            if not ok:
                raise ValueError("Invalid generated candidate: " + "; ".join(errors))
            result.append(node)
        return result


FREQUENCY_NODE = "UPI<information_physics,1,frequency,ordinary_frequency_relations>"
MASS_NODE = "UPI<information_physics,1,inertia,frequency_mass_equivalent>"
SPIRAL_NODE = "UPI<information_physics,1,spiral_flow,tf1766_1_766hz>"
FREQUENCY_ASSUMPTION = "f is a declared ordinary frequency, not an angular frequency."
MASS_ASSUMPTION = "SI units. h and c take their exact SI values."
SPIRAL_ASSUMPTION = "The Spiral Flow time relation is a declared model transformation, not an established cosmological law."


def frequency_relations() -> tuple[Relation, ...]:
    """Adapters bind exact equations; these definitions are not a universal solver."""
    return (
        Relation(
            FREQUENCY_NODE,
            "T = 1/f",
            (("f", "Hz"),),
            ("T", "s"),
            lambda q: period_from_frequency(q["f"]),
            lambda y, q: 1 / y,
            "f",
            FREQUENCY_ASSUMPTION,
        ),
        Relation(
            FREQUENCY_NODE,
            "omega = 2*pi*f",
            (("f", "Hz"),),
            ("omega", "rad/s"),
            lambda q: angular_frequency(q["f"]),
            lambda y, q: y / math.tau,
            "f",
            FREQUENCY_ASSUMPTION,
        ),
        Relation(
            MASS_NODE,
            "E = h f",
            (("f", "Hz"),),
            ("E", "J"),
            lambda q: energy_from_frequency(q["f"]),
            lambda y, q: y / H,
            "f",
            MASS_ASSUMPTION,
        ),
        Relation(
            MASS_NODE,
            "m = h f / c^2",
            (("f", "Hz"),),
            ("m_eq", "kg"),
            lambda q: mass_from_frequency(q["f"]),
            lambda y, q: frequency_from_mass(y),
            "f",
            MASS_ASSUMPTION,
        ),
        Relation(
            SPIRAL_NODE,
            "t(f) = t_ref × f_ref / f",
            (("f", "Hz"), ("f_ref", "Hz"), ("t_ref", "Gyr")),
            ("t_model", "Gyr"),
            lambda q: spiral_time_from_frequency(q["f"], q["f_ref"], q["t_ref"]),
            lambda y, q: q["t_ref"] * q["f_ref"] / y,
            "f",
            SPIRAL_ASSUMPTION,
        ),
        Relation(
            FREQUENCY_NODE,
            "phase = 2*pi*f*t + phase0",
            (("f", "Hz"), ("t", "s"), ("phase0", "rad")),
            ("phase", "rad"),
            lambda q: phase_from_frequency(q["f"], q["t"], q["phase0"]),
            lambda y, q: (y - q["phase0"]) / (math.tau * q["f"]),
            "t",
            FREQUENCY_ASSUMPTION,
        ),
    )
