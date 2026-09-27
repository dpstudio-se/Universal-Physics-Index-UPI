"""Export deterministic synthetic controls through the real DNA->dynamics API."""

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from upi.dna import DNAReader
from upi.spiral_flow import dynamic_reference_points


def controls() -> dict[str, dict]:
    template = json.loads(Path(__file__).with_name("frequency-series.json").read_bytes())
    times = template["times_s"]
    duration = times[-1] - times[0]
    trajectories = {
        "constant": [3.21] * len(times),
        "linear": [1 + 9 * (t - times[0]) / duration for t in times],
        "sinusoidal": list(template["frequencies_hz"]),
    }
    for reference in dynamic_reference_points():
        # Center sample exactly crosses the reference; no rounding to another reference.
        trajectories["cross_" + reference.label] = [
            reference.frequency_hz + (t - (times[0] + duration / 2)) for t in times
        ]
    result = {}
    for name, frequencies in trajectories.items():
        for force in ("none", "manufactured_rotation"):
            key = name + "__" + force
            payload = deepcopy(template)
            payload.update(source="SYNTHETIC CONTROL: " + key, frequencies_hz=frequencies)
            payload["control"]["force_mode"] = force
            result[key] = payload
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="New output directory; never overwrite a run")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    reader = DNAReader(repo / "data")
    args.output.mkdir(parents=True, exist_ok=False)
    summary = []
    for name, payload in controls().items():
        report = reader.analyze_dynamic(payload)
        expected = (
            "PASS"
            if name.startswith("constant__") or name.endswith("__manufactured_rotation")
            else "STOP"
        )
        path = args.output / (name + ".json")
        raw = (json.dumps(report, indent=2, allow_nan=False) + "\n").encode()
        path.write_bytes(raw)
        summary.append(
            {
                "control": name,
                "expected": expected,
                "observed": report["state"],
                "file": path.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "input_sha256": report["input_sha256"],
                "code_sha256": report["code_sha256"],
                "max_residual_m_s2": max(
                    f["residual_norm"] for r in report["rows"] for f in r["particle_fields"]
                ),
                "dynamic_nodes": len(report["dynamic_nodes"]),
                "verification_type": "software_test",
            }
        )
    passed = all(r["observed"] == r["expected"] for r in summary)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "verification_type": "software_test",
                "controls": len(summary),
                "state": "PASS" if passed else "STOP",
                "promotion": "BLOCKED",
                "summary": str(args.output / "summary.json"),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
