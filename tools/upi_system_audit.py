#!/usr/bin/env python3
"""Fail-closed UPI system health audit.

Checks core runtime, governance, workflow, schema, skill/routine and research
entry points. It reports missing components and never promotes research claims.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]

EXPECTED = [
    "src/upi",
    "tests",
    ".github/workflows/ci.yml",
    ".github/workflows/upi-full-audit.yml",
    ".github/workflows/rna-delta.yml",
    ".github/workflows/upi-system-health-loop.yml",
    ".grok/workflows/index-triage.rhai",
    "docs/GOVERNED_SYSTEM.md",
    "docs/ASTRA_UPI_FEEDBACK_LOOP.md",
    "docs/UNIVERS_OCR.md",
    "AGENTS.md",
    "schemas/skill.schema.json",
    "schemas/routine.schema.json",
    "examples/workflows/index-triage.workflow.json",
    "examples/skills/index-triage.skill.json",
    "examples/skills/schema-validator.skill.json",
    "examples/routines/index-triage.routine.json",
    "examples/ledger/index-triage.ledger.json",
    "examples/handoffs/index-triage.handoff.json",
    "examples/handoffs/schema-validator.handoff.json",
    "docs/UPI_MIRROR_BRIDGE_LOOP.md",
    "docs/FL_TERMINOLOGY.md",
    "docs/FL_EXECUTION_CONTRACT.md",
    "schemas/fl-bridge.schema.json",
    "examples/workflows/mirror-bridge-verification.workflow.json",
    "examples/skills/mirror-bridge-verification.skill.json",
    "examples/routines/mirror-bridge-verification.routine.json",
    "examples/bridges/fl-bridge.example.json",
]


def check_paths() -> list[str]:
    return [p for p in EXPECTED if not (ROOT / p).exists()]


def check_python() -> int:
    targets = [ROOT / "src", ROOT / "tests", ROOT / "tools"]
    py = [str(p) for base in targets for p in base.rglob("*.py") if p.is_file()]
    if not py:
        return 0
    return subprocess.run([sys.executable, "-m", "py_compile", *py], cwd=ROOT).returncode


def write_research_handoff(missing: list[str], compile_rc: int) -> None:
    """Route failed audit evidence into the research layer without promoting it."""
    out = ROOT / "examples" / "research" / "audit-handoff-latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "STOP",
        "scientific_status": "STOP",
        "workflow_status": "FAIL",
        "mode": "RESEARCH",
        "reason": "UPI health audit did not pass",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "missing_expected_paths": missing,
        "python_compile_rc": compile_rc,
        "next_action": "Investigate each failed component in research mode; preserve evidence and do not promote automatically.",
        "promotion_guard": "Research findings require their own verification and review before canonical promotion.",
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    missing = check_paths()
    compile_rc = check_python()
    print("UPI SYSTEM HEALTH AUDIT")
    print("========================")
    print(f"expected_components={len(EXPECTED)}")
    print(f"missing_expected_paths={len(missing)}")
    for item in missing:
        print(f"MISSING: {item}")
    print(f"python_compile_rc={compile_rc}")
    if missing or compile_rc != 0:
        write_research_handoff(missing, compile_rc)
        print("STATUS=STOP")
        print("ROUTE=RESEARCH")
        print("RESEARCH_HANDOFF=examples/research/audit-handoff-latest.json")
        return 1
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
