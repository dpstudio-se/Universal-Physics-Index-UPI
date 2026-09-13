"""Run all suites, bind each result, then rerun feedback. Never promote."""

import json
import os
import re
import runpy
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from upi.atlas_gates import (
    binding_snapshot,
    canonical_comparison,
    claim_analysis,
    digest_json,
    file_hash,
    validate_test_receipt,
)


def main():
    repo = Path(__file__).resolve().parents[2]
    root = repo / "examples/feedback"
    binding = binding_snapshot(repo)
    binding_id = digest_json(binding)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = root / "runs" / stamp
    run_dir.mkdir(parents=True)
    temp_root = Path(tempfile.mkdtemp(prefix="upi-validation-"))
    receipt = {
        "format": "upi-bound-tests-v1",
        "started_at": stamp,
        "binding": binding,
        "binding_sha256": binding_id,
        "verification_type": "software_test",
        "suites": [],
        "quality_checks": [],
        "trust_scope": "Local execution record, not a signed independent attestation.",
    }
    for name, cwd in [("main", repo), ("resonancefs", repo / "projects/resonancefs")]:
        raw_path = run_dir / f"{name}.json"
        command = [
            sys.executable,
            str(root / "test_recorder.py"),
            str(raw_path),
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(temp_root / name),
        ]
        # No inherited pytest selectors or plugins may silently reduce the declared test set.
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"}
        }
        env["PYTHONPATH"] = str(cwd / "src")
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        log_path = run_dir / f"{name}.log"
        log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        raw = (
            json.loads(raw_path.read_bytes())
            if raw_path.exists()
            else {"collected": [], "results": [], "environment": {}}
        )
        suite = {
            **raw,
            "name": name,
            "exit_code": completed.returncode,
            "command": command,
            "cwd": cwd.relative_to(repo).as_posix(),
            "binding_sha256": binding_id,
            "test_set_sha256": digest_json(sorted(raw["collected"])),
            "log_path": log_path.relative_to(repo).as_posix(),
            "log_sha256": file_hash(log_path),
        }
        if raw_path.exists():
            suite.update(
                result_path=raw_path.relative_to(repo).as_posix(), result_sha256=file_hash(raw_path)
            )
        for result in suite["results"]:
            result.update(binding_sha256=binding_id, verification_type="software_test")
        receipt["suites"].append(suite)
        print(f'{name}: {len(raw["collected"])} collected; exit {completed.returncode}', flush=True)
    command = ["node", "--test", "--test-reporter=tap", "tests/test_lab_math.cjs"]
    completed = subprocess.run(
        command, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    log_path = run_dir / "javascript.log"
    log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    matches = re.findall(r"^(ok|not ok) \d+ - (.+)$", completed.stdout, flags=re.MULTILINE)
    ids = [name for _, name in matches]
    receipt["suites"].append(
        {
            "name": "javascript",
            "collected": ids,
            "results": [
                {
                    "nodeid": name,
                    "outcome": "passed" if status == "ok" else "not_passed",
                    "binding_sha256": binding_id,
                    "verification_type": "software_test",
                }
                for status, name in matches
            ],
            "exit_code": completed.returncode,
            "command": command,
            "cwd": ".",
            "environment": {
                "node": subprocess.check_output(["node", "--version"], text=True).strip()
            },
            "binding_sha256": binding_id,
            "test_set_sha256": digest_json(sorted(ids)),
            "log_path": log_path.relative_to(repo).as_posix(),
            "log_sha256": file_hash(log_path),
        }
    )
    for name, cwd, args in [
        ("ruff", repo, ["ruff", "check", "src", "tests", "examples/feedback"]),
        ("mypy", repo, ["mypy", "src/upi", "--ignore-missing-imports"]),
        ("resonance_ruff", repo / "projects/resonancefs", ["ruff", "check", "src", "tests"]),
        ("resonance_mypy", repo / "projects/resonancefs", ["mypy", "src"]),
    ]:
        command = [sys.executable, "-m", *args]
        completed = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        path = run_dir / f"{name}.log"
        path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        receipt["quality_checks"].append(
            {
                "name": name,
                "command": command,
                "exit_code": completed.returncode,
                "binding_sha256": binding_id,
                "log_path": path.relative_to(repo).as_posix(),
                "log_sha256": file_hash(path),
            }
        )
        print(f"{name}: exit {completed.returncode}", flush=True)
    unchanged = binding_snapshot(repo) == binding
    passed = (
        unchanged
        and all(
            s["exit_code"] == 0
            and s["collected"]
            and all(t["outcome"] == "passed" for t in s["results"])
            for s in receipt["suites"]
        )
        and all(c["exit_code"] == 0 for c in receipt["quality_checks"])
    )
    receipt.update(
        state="PASS" if passed else "STOP",
        inputs_unchanged=unchanged,
        finished_at=datetime.now(timezone.utc).isoformat(),
    )
    receipt_errors = validate_test_receipt(repo, receipt)
    if receipt_errors:
        passed = False
        receipt.update(state="STOP", receipt_validation_errors=receipt_errors)
    (root / "test_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    report = runpy.run_path(str(root / "review_atlas.py"))["run_review"]().as_dict()
    (root / "atlas_review_result.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    candidate = json.loads((root / "candidates/3i_atlas_upi_case.json").read_bytes())
    (root / "canonical_comparison.json").write_text(
        json.dumps(canonical_comparison(repo, candidate), indent=2) + "\n", encoding="utf-8"
    )
    (root / "claim_analysis_result.json").write_text(
        json.dumps(claim_analysis(repo), indent=2) + "\n", encoding="utf-8"
    )
    print(
        f'Test receipt: {receipt["state"]}; feedback: {report["decision"]}/{report["promotion_gate"]}',
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
