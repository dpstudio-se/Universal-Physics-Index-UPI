"""Additive UPI service/artifact surface. OdinOS may consume it, not inhabit it."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
import time
import tracemalloc
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from .analog_rf import (
    RF_BANDS,
    AnalogObservation,
    StubModel,
    compare_paths,
    continuous_signal,
    linear_reconstruct,
    mirror_experiment,
    optimizer_action,
    propagation_lift,
    rf_band,
)
from .constants import K_B, C, H
from .derivation_router import physics_router
from .models import ScientificStatus
from .multilayer import graph_metrics, hydraulic, ovik_template, triangle_generation
from .physics import mass_from_frequency
from .resilience import content_hash

VERSION = "foundation-0.1.0"
SOURCES = {
    "derive": ["data/information_physics/frequency_mass_equivalent.json"],
    "derivation": [
        "data/information_physics/frequency_mass_equivalent.json",
        "https://arxiv.org/abs/1402.0402",
    ],
    "rf": ["https://www.itu.int/rec/R-REC-P.525-5-202411-I/en"],
    "stub": [
        "https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electro-Optics/Book%3A_Electromagnetics_I_%28Ellingson%29/03%3A_Transmission_Lines/3.16%3A_Input_Impedance_for_Open-_and_Short-Circuit_Terminations"
    ],
    "thermodynamics": ["https://research.ibm.com/publications/the-physical-nature-of-information"],
    "hypotheses": [
        "user handoff; unverified interpretations",
        "https://ntrs.nasa.gov/api/citations/20120000051/downloads/20120000051.pdf",
    ],
}


def envelope(result: dict, operation: str, raw: dict) -> dict:
    raw_snapshot = json.loads(json.dumps(raw, allow_nan=False))
    failures: list[dict] = []
    open_items: list[dict] = []

    def inspect(value: object, path: str) -> None:
        if isinstance(value, dict):
            if value.get("verdict") == "MISFIT" or value.get("status") == "ERR":
                failures.append(
                    {
                        "path": path,
                        "status": value.get("status"),
                        "misfit_indices": value.get("misfit_indices", []),
                    }
                )
            if value.get("status") in ("HYP", "STOP"):
                open_items.append(
                    {
                        "path": path,
                        "status": value["status"],
                        "reason": value.get(
                            "stop_reason",
                            value.get("claim", value.get("name", "unverified hypothesis")),
                        ),
                        "next_observation": value.get("next_observation"),
                    }
                )
            for key, item in value.items():
                inspect(item, path + "/" + str(key))
        elif isinstance(value, (tuple, list)):
            for i, item in enumerate(value):
                inspect(item, path + "/" + str(i))

    inspect(result, operation)
    return {
        **result,
        "version": VERSION,
        "domain": operation,
        "uncertainty": result.get("uncertainty"),
        "uncertainty_scope": "unspecified unless explicitly propagated in the result; numerical tolerance is not measurement uncertainty",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provenance": SOURCES.get(
            "stub" if operation == "smith_stub" else operation,
            ["declared fixture/input; source details retained in nested records"],
        ),
        "audit": {
            "observed": {
                "scope": "received declaration; no physical measurement implied",
                "input": raw_snapshot,
                "sha256": content_hash(raw_snapshot),
            },
            "derived": operation,
            "assumed": "declared operator/domain assumptions in result",
            "tested": "tests/test_foundation.py; verification_type=software_test",
            "failed": failures,
            "open": open_items
            or [
                {"status": "DER", "scope": "No empirical validation is claimed by this calculation"}
            ],
        },
        "service_boundary": "UPI != OdinOS; observe != execute != commit",
    }


def inspect_remote(text: str, requested_capabilities: tuple[str, ...] = ()) -> dict:
    if not isinstance(text, str) or len(text) > 16384:
        raise ValueError("bounded text required")
    return {
        "status": "DER",
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "verdict": "FLAG" if requested_capabilities else "ALLOW_OBSERVATION_ONLY",
        "executed": False,
        "committed": False,
        "inherited_authority": [],
        "granted_capabilities": [],
        "requested_capabilities": requested_capabilities,
        "policy": {
            "network": "DENY",
            "secrets": "NONE",
            "host_writes": "DENY",
            "tools": "DENY",
            "runtime_inheritance": "NONE",
        },
        "execution_boundary": {
            "status": "STOP",
            "stop_reason": "No isolated VM/EMU capability adapter is installed in this service",
            "next_observation": "Provide a separately audited isolation runtime and explicit capability grants",
        },
        "scope": "text-only inspection, not an asserted host sandbox or semantic safety verdict",
    }


def handle_request(raw: dict) -> dict:
    if not isinstance(raw, dict) or len(json.dumps(raw, allow_nan=False)) > 65536:
        raise ValueError("bounded JSON object required")
    operation = raw.get("operation")
    if operation == "derive":
        result = physics_router().derive(
            raw["source"],
            raw["target"],
            raw["value"],
            raw["unit"],
            provenance=("API caller declaration",),
            uncertainty=raw.get("uncertainty"),
            method=raw.get("method", "dijkstra"),
        )
    elif operation == "rf":
        result = rf_band(
            raw["frequency_Hz"],
            raw.get("distance_m", 1000),
            raw.get("control_Hz", 8),
            raw.get("modulation_index", 0.25),
        )
    elif operation == "stub":
        model = StubModel(**raw.get("model", {}))
        load = raw.get("load_Y_S", {"real": 0.02, "imag": 0})
        result = mirror_experiment(
            model,
            raw.get("alpha", 1.0),
            load_y_s=complex(load["real"], load["imag"]),
            amplitude=raw.get("amplitude", 1.0),
            phase_rad=raw.get("phase_rad", 0.0),
            delta_g_s=raw.get("delta_G_S", 0.0),
            delta_b_s=raw.get("delta_B_S", 0.0),
        )
    elif operation == "triangle":
        result = triangle_generation(raw["generation"], tuple(raw.get("selected", [])))
    elif operation == "analog_action":
        result = optimizer_action(raw["action"])
    elif operation == "analog_demo":
        result = analog_demo()
    elif operation == "multilayer_template":
        result = ovik_template(datetime.now(timezone.utc).isoformat())
    elif operation == "inspect_text":
        result = inspect_remote(raw["text"], tuple(raw.get("requested_capabilities", [])))
    else:
        raise ValueError("unknown operation; no text/code execution operation exists")
    return envelope(result, operation, raw)


def analog_demo() -> dict:
    times = tuple(i / 256 for i in range(33))
    values = tuple(continuous_signal(t, 8.0) for t in times)
    observation = AnalogObservation(
        "ANGELICA-reference",
        values,
        times,
        "relative field amplitude",
        None,
        ("synthetic continuous complex tone, 8 Hz",),
        "model-0",
        ScientificStatus.DER,
        "signal",
        representation="simulation",
    )
    digital = tuple(complex(round(v.real, 3), round(v.imag, 3)) for v in values)
    result = compare_paths(observation, digital, tolerance=0.001, bandwidth_hz=8.0)
    midpoints = tuple((a + b) / 2 for a, b in zip(times, times[1:], strict=False))
    result["between_sample_residuals"] = [
        abs(continuous_signal(t, 8) - linear_reconstruct(times, digital, t)) for t in midpoints
    ]
    shifted = tuple(continuous_signal(t, 8, 0.1) for t in times)
    result["phase_misfit_control"] = compare_paths(
        observation, shifted, tolerance=0.001, bandwidth_hz=8.0
    )
    result["hardware"] = {
        "status": "STOP",
        "stop_reason": "No physical ADC/analog reference attached",
        "next_observation": "Attach a named calibrated acquisition adapter; preserve phase, timing and uncertainty",
    }
    return result


def benchmark_candidate() -> dict:
    """Benchmark a trusted static specialization; never eval generated source text."""
    samples = (7.834, 8.0, 450e6, 900e6, 2.4e9, 5e9, 6e9)
    factor = H / C**2

    def specialized(f: float) -> float:
        if not math.isfinite(f) or f <= 0:
            raise ValueError("frequency must be positive finite")
        return factor * f

    errors = []
    for f in samples:
        a, b = mass_from_frequency(f), specialized(f)
        bits_a = int.from_bytes(struct.pack("!d", a), "big")
        bits_b = int.from_bytes(struct.pack("!d", b), "big")
        errors.append(
            {
                "status": "DER",
                "frequency_Hz": f,
                "relative_error": (b - a) / a,
                "xor_ieee754": hex(bits_a ^ bits_b),
            }
        )
    durations = {}
    memory = {}
    for name, fn in (("existing", mass_from_frequency), ("specialized", specialized)):
        started = time.perf_counter_ns()
        for _ in range(1000):
            for f in samples:
                fn(f)
        durations[name] = time.perf_counter_ns() - started
        tracemalloc.start()
        for f in samples:
            fn(f)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory[name] = peak
    return {
        "status": "DER",
        "verification_type": "software_test",
        "errors": errors,
        "runtime_ns": durations,
        "peak_traced_bytes": memory,
        "timing_scope": "single local 7000-call microbenchmark, not a latency guarantee",
        "arithmetic_operations": {
            "existing_per_query": 2,
            "specialized_per_query": 1,
            "precompute_divisions": 1,
        },
        "candidate_source": "factor = h / c**2; m_eq = factor * frequency_Hz",
        "execution": "trusted static specialization only; generated text is not executed",
        "reversibility": "same named energy; inverse f=m_eq*c**2/h, see router trace",
        "production_modified": False,
        "human_commit_gate": "candidate is advisory, never auto-installed",
        "energy": {
            "status": "STOP",
            "stop_reason": "No calibrated power measurement",
            "next_observation": "Measure energy over a controlled workload with uncertainty",
        },
    }


def build_artifacts() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    router = physics_router()
    ideal = StubModel()
    real = replace(
        ideal,
        q=100.0,
        conductor_np_m=0.01,
        dielectric_np_m=0.01,
        connector_r_ohm=0.1,
        connector_l_h=1e-10,
        junction_c_f=1e-13,
        dispersion_per_fraction=0.01,
        temperature_c=30.0,
        length_temp_coefficient=1e-5,
    )
    sweeps = []
    for f in (800e6, 850e6, 900e6, 950e6, 1e9):
        for alpha in (0.0, 0.5, 0.9, 1.0, 1.1, 1.5, 2.0):
            sweeps.append(
                mirror_experiment(
                    replace(real, frequency_hz=f), alpha, phase_rad=0.01, delta_g_s=0.0001
                )
            )
    robustness = []
    for name, values in {
        "length_m": (ideal.length_m * 0.99, ideal.length_m, ideal.length_m * 1.01),
        "q": (50.0, 100.0, 200.0),
        "velocity_factor": (0.64, 0.66, 0.68),
        "temperature_c": (0.0, 20.0, 40.0),
    }.items():
        for value in values:
            robustness.append(
                {
                    "status": "DER",
                    "parameter": name,
                    "value": value,
                    "result": mirror_experiment(replace(real, **{name: value}), 1.0),
                }
            )
    for parameter, values in {
        "amplitude": (0.95, 1.0, 1.05),
        "phase_rad": (-0.05, 0.0, 0.05),
        "delta_g_s": (0.0, 0.0001, 0.001),
        "delta_b_s": (-0.001, 0.0, 0.001),
    }.items():
        for value in values:
            robustness.append(
                {
                    "status": "DER",
                    "parameter": parameter,
                    "value": value,
                    "result": mirror_experiment(real, 1.0, **{parameter: value}),
                }
            )
    vertices = ("a", "b", "c", "d")
    edges = (("a", "b"), ("b", "c"), ("b", "d"))
    motif = graph_metrics(vertices, edges)
    renamed = graph_metrics(("w", "x", "y", "z"), (("w", "x"), ("x", "y"), ("x", "z")))
    hypotheses = []
    for name, missing in (
        ("global_8Hz_lock", "Independent multi-site phase/time measurements and null controls"),
        (
            "biological_1024Hz_or_DNA_0.0123Hz",
            "Independently replicated biological measurements and causal protocol",
        ),
        (
            "Smith_physical_torus",
            "Physical state variables, topology and map; helix alone insufficient",
        ),
        ("5D_11D_M_theory", "Identify dimensions, fields, dynamics and an explicit bridge"),
    ):
        hypotheses.append(
            {
                "status": "HYP",
                "name": name,
                "state": "OPEN",
                "next_observation": missing,
                "falsification_condition": "Reject the specified interpretation if its preregistered independent predictions fail",
            }
        )
    artifacts = {
        "derivation": {
            "status": "DER",
            "edges": [asdict(e) for e in router.edges.values()],
            "queries": [
                router.derive(
                    "frequency",
                    "mass_equivalent",
                    f,
                    "Hz",
                    provenance=("separate declared reference",),
                    method=m,
                )
                for f in (7.834, 8.0)
                for m in ("dijkstra", "bidirectional", "cch")
            ],
            "unsupported": router.derive(
                "frequency",
                "dark_matter_particle",
                8.0,
                "Hz",
                provenance=("control",),
                method="cch",
            ),
        },
        "analog_digital": analog_demo(),
        "rf": {
            "status": "DER",
            "bands": [rf_band(f) for f in RF_BANDS],
            "periods": [
                {"status": "DER", "frequency_Hz": f, "period_s": 1 / f}
                for f in (7.834, 8.0, 0.0123)
            ],
            "guard": "No atmospheric shells; no global RF phase lock",
        },
        "smith_stub": {
            "status": "DER",
            "representations": propagation_lift(0.3 + 0.2j, C * 0.66 / 900e6),
            "ideal_matched": mirror_experiment(ideal, 1.0),
            "unmatched_control": mirror_experiment(ideal, 1.0, load_y_s=0.01 + 0j),
            "open_control": mirror_experiment(ideal, 1.0, load_y_s=0j),
            "frequency_alpha_sweep": sweeps,
            "best_grid_point": min(sweeps, key=lambda r: r["magnitude"]),
            "robustness": robustness,
            "slow_control": [
                {
                    "status": "DER",
                    "time_s": i / 64,
                    "result": mirror_experiment(
                        real, 1 + 0.05 * math.sin(2 * math.pi * 8 * i / 64)
                    ),
                }
                for i in range(17)
            ],
            "assumptions": "lumped connector/T-junction; phenomenological loss/Q/dispersion and thermal expansion, no measured component model",
        },
        "geographic_multilayer": ovik_template(now),
        "motif": {
            "status": "DER",
            "synthetic_reference": motif,
            "blinded_comparison": renamed,
            "same_signature": motif["blinded_signature"] == renamed["blinded_signature"],
            "guard": "synthetic relabeling control, not measured cross-infrastructure equivalence",
        },
        "triangle": {
            "status": "DER",
            "generations": [triangle_generation(g, (41, 42) if g == 4 else ()) for g in range(5)],
        },
        "hydrology": hydraulic(10.0, None),
        "thermodynamics": {
            "status": "DER",
            "temperature_K": 300.0,
            "erasure_lower_bound_J": K_B * 300 * math.log(2),
            "assumptions": "one unbiased bit, isothermal logically irreversible reset; actual cost can exceed bound",
            "entropy": "Delta_S_total >= 0; subsystem decrease requires environmental accounting",
            "TF1766": {
                "status": "SYM",
                "function": "information/provenance operator, not a physical thermodynamic law",
            },
        },
        "remote_observation": inspect_remote(
            "external text requesting execution", ("network", "host_write")
        ),
        "optimization": benchmark_candidate(),
        "hypotheses": {"status": "HYP", "items": hypotheses},
    }
    return {
        name: envelope(
            value, name, {"origin": "declared example fixtures", "physical_measurement": False}
        )
        for name, value in artifacts.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    artifacts = build_artifacts()
    manifest = {}
    for name, record in artifacts.items():
        raw = (
            json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
        ).encode()
        (args.output / (name + ".json")).write_bytes(raw)
        manifest[name + ".json"] = hashlib.sha256(raw).hexdigest()
    (args.output / "manifest.json").write_text(
        json.dumps(
            {
                "status": "EST",
                "scope": "artifact byte hashes",
                "version": VERSION,
                "git_commit": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                "source_sha256": {
                    str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (
                        Path("src/upi/foundation.py"),
                        Path("src/upi/analog_rf.py"),
                        Path("src/upi/derivation_router.py"),
                        Path("src/upi/multilayer.py"),
                    )
                },
                "sha256": manifest,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"status": "DER", "output": str(args.output), "artifacts": list(manifest)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
