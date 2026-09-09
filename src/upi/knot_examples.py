"""Deterministic synthetic controls, including the existing Lorentz profile."""

from dataclasses import asdict, replace

from .constants import C
from .dual_observer import Event1D, dual_observer_trace, lorentz_transform_event
from .knot import analyze
from .knot_model import Observation, PathTrace, Step, Tolerance
from .models import ScientificStatus


def example_paths() -> tuple[tuple[PathTrace, ...], dict[str, Tolerance]]:
    event = Event1D(2e-6, 300.0)
    predicted = lorentz_transform_event(event, 0.6 * C)
    exact = dual_observer_trace(event, 0.6 * C)
    perturbed = dual_observer_trace(event, 0.6 * C,
                                    observed_b=Event1D(predicted.time_s + 2e-9,
                                                      predicted.position_m + 0.25))
    rows: list[tuple[str, str, str, float | str, float | str, float, float, str]] = [
        ("lorentz-time", "physics", "s", event.time_s, exact.reconstructed_a.time_s,
         1e-9, 1e-18, "Lorentz forward then inverse; beta=0.6"),
        ("observer-offset", "physics", "m", event.position_m, perturbed.reconstructed_a.position_m,
         0.1, 1e-12, "Lorentz inverse; injected B offsets +2 ns and +0.25 m"),
        ("historical-territory", "history", "label", "Territory A", "Territory B", 0, 0,
         "inside_at(place, time); synthetic territory"),
        ("name-function", "semantics", "label", "harbour", "farm", 0, 0, "function_at"),
        ("spelling", "semantics", "label", "Kytämäki", "Kytiniemi", 0, 0, "named_as"),
        ("false-mirror", "physics", "m", 3.0, 3.0, 0.001, 0, "shared form candidate"),
        ("lost-sign", "mathematics", "1", -3.0, ((-3.0) ** 2) ** 0.5,
         0, 0, "square then principal square root"),
    ]
    left: list[Step] = []
    right: list[Step] = []
    tolerances = {}
    for key, domain, units, x, y, tau, numerical, mirror in rows:
        a = Observation(f"{key}-a", key, domain, "2026", "synthetic fixture", "common frame",
                        key, key, "synthetic:A", 0.9, x, units, ("fixture:A",),
                        coordinate="common", source_group="fixture", source_quality=0.8,
                        status=ScientificStatus.DER)
        b = replace(a, id=f"{key}-b", raw_value=y, source="synthetic:B", provenance=("fixture:B",))
        if key == "historical-territory":
            a = replace(a, time="1690")
        if key == "name-function":
            a, b = replace(a, function="harbour"), replace(b, function="farm")
        if key == "spelling":
            a, b = replace(a, name="Kytämäki"), replace(b, name="Kytiniemi")
        if key == "false-mirror":
            b = replace(b, domain="semantics", units="label")
        left.append(Step(key, a, f"reference:{key}", "reference observation", "root" if not left
                         else left[-1].observation.id, True, True, "", True))
        right.append(Step(key, b, f"candidate:{key}", mirror, "root" if not right
                          else right[-1].observation.id, key != "lost-sign", True,
                          "sign discarded by square" if key == "lost-sign" else "", True))
        tolerances[key] = Tolerance(tau, units, numerical)
    return (PathTrace("reference", tuple(left)), PathTrace("reconstruction", tuple(right))), tolerances


def example_document() -> dict:
    paths, tolerances = example_paths()
    return {"format": "upi-oden-paths", "version": "1.0",
            "paths": [asdict(replace(p, steps=p.steps[:2])) for p in paths],
            "tolerances": {k: asdict(v) for k, v in tolerances.items()
                           if k in {"lorentz-time", "observer-offset"}}}


def example_report() -> dict:
    paths, tolerances = example_paths()
    reports = []
    for a, b in zip(paths[0].steps, paths[1].steps, strict=True):
        pair = (PathTrace(a.checkpoint + ":reference", (replace(a, input_id="root"),)),
                PathTrace(b.checkpoint + ":reconstruction", (replace(b, input_id="root"),)))
        reports.append(analyze(pair, tolerances))
    result = {**reports[0], "paths": [], "knots": [], "gallery": "Independent synthetic controls"}
    for report in reports:
        result["paths"].extend(report["paths"])
        for knot in report["knots"]:
            result["knots"].append({**knot, "id": f"knot-{len(result['knots']) + 1:04d}"})
    event = Event1D(2e-6, 300.0)
    predicted = lorentz_transform_event(event, 0.6 * C)
    result["control_provenance"] = {
        "fixture:A": {"type": "synthetic reference", "observer_a": asdict(event)},
        "fixture:B": {
            "type": "synthetic reconstruction; not independent evidence",
            "exact_lorentz": dual_observer_trace(event, 0.6 * C).as_dict(),
            "perturbed_lorentz": dual_observer_trace(
                event, 0.6 * C,
                observed_b=Event1D(predicted.time_s + 2e-9, predicted.position_m + 0.25),
                position_tolerance_m=0.1,
            ).as_dict(),
        },
    }
    return result
