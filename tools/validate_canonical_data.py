#!/usr/bin/env python3
"""Validate every canonical JSON record that has a declared UPI record shape."""

import json
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    name: json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
    for name in ("node", "bridge", "theory")
}


def main() -> int:
    checked = 0
    skipped = 0
    # Explicit legacy records with specialized shapes, pending dedicated schemas.
    # Do not treat these as canonical physics nodes.
    legacy_special_records = {
        "data/bridges/multi_scale_wave_time_space_network_20260921.json",
        "data/bridges/omega1766_rotation_pressure_flow_work_entropy.json",
        "data/hypotheses/psi27d_navier_regularity.json",
        "data/infrastructure_physics/gates_packet.json",
        "data/research/triskelion_public_source_map.json",
    }
    for record in legacy_special_records:
        if not (ROOT / record).is_file():
            raise FileNotFoundError(f"Legacy record missing: {record}")

    for path in sorted((ROOT / "data").rglob("*.json")):
        relative_path = path.relative_to(ROOT).as_posix()
        if relative_path in legacy_special_records:
            skipped += 1
            print(f"Legacy specialized record (not schema-validated): {relative_path}")
            continue
        if path.name.startswith("invalid_") or "sources" in path.parts:
            skipped += 1
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if {"source", "target", "relation"} <= obj.keys():
            kind = "bridge"
        elif {"domain", "scope"} <= obj.keys():
            kind = "theory"
        elif {"address", "status", "title"} <= obj.keys():
            kind = "node"
        else:
            skipped += 1
            continue
        validate(instance=obj, schema=SCHEMAS[kind])
        checked += 1
    print(f"Canonical data validation passed: checked={checked}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
