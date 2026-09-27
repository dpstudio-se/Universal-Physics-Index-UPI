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
    for path in sorted((ROOT / "data").rglob("*.json")):
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
