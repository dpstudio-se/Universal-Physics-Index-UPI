"""Version-bound review gates for the unpromoted 3I/ATLAS case.

These local audit artifacts are not signed attestations or scientific evidence
merely because hashes match. A complete coverage inventory can contain STOP claims.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .feedback import CheckResult

POLICY_VERSION = "atlas-gates-1"
BASELINE_COMMIT = "b2663cb0d9296cb616865d93d549a44159867601"


def digest_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leaves(value: Any, pointer: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            result.update(leaves(child, pointer + "/" + key.replace("~", "~0").replace("/", "~1")))
        return result
    if isinstance(value, list):
        result = {}
        for i, child in enumerate(value):
            result.update(leaves(child, pointer + "/" + str(i)))
        return result
    return {pointer: value}


def canonical_comparison(repo: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    baseline = json.loads((repo / "examples/feedback/canonical_baseline.json").read_bytes())
    if baseline["commit"] != BASELINE_COMMIT:
        raise ValueError("Unexpected selected canonical commit.")
    tree = subprocess.check_output(
        ["git", "rev-parse", BASELINE_COMMIT + ":data"], cwd=repo, text=True
    ).strip()
    if tree != baseline["data_tree"]:
        raise ValueError("Baseline tree mismatch.")
    raw_tree = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", BASELINE_COMMIT, "--", "data"], cwd=repo
    )
    expected = {}
    for entry in raw_tree.split(b"\0"):
        if entry:
            header, path = entry.decode().split("\t", 1)
            if path.endswith(".json"):
                expected[path] = header.split()[2]
    observed = {}
    records: dict[str, list[dict[str, Any]]] = {}
    for entry in baseline["entries"]:
        content = entry["content"].encode()
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if (
            entry["path"] in observed
            or blob != entry["blob_sha1"]
            or hashlib.sha256(content).hexdigest() != entry["sha256"]
        ):
            raise ValueError("Baseline entry identity/integrity mismatch.")
        observed[entry["path"]] = blob
        record = json.loads(content)
        if (
            isinstance(record.get("address"), str)
            and {"title", "status"} <= record.keys()
            and not Path(entry["path"]).name.startswith("invalid_")
        ):
            records.setdefault(record["address"], []).append(record)
    if expected != observed:
        raise ValueError("Baseline inventory does not match the committed tree.")
    original = json.loads((repo / "examples/feedback/sources/3i_atlas_upi_case.json").read_bytes())
    dependencies = original["upi_bridges"]
    missing = [address for address in dependencies if address not in records]
    existing = records.get(candidate["address"], [])
    duplicates = [
        address
        for address, items in records.items()
        if len(items) > 1 and address in dependencies + [candidate["address"]]
    ]
    helical = records.get(dependencies[0], [])
    guard_present = bool(
        helical and "do not generate energy" in helical[0].get("confusion_guard", "")
    )
    return {
        "baseline_commit": BASELINE_COMMIT,
        "data_tree": tree,
        "record_count": len(observed),
        "baseline_sha256": file_hash(repo / "examples/feedback/canonical_baseline.json"),
        "candidate_hash": digest_json(candidate),
        "candidate_version": candidate["version"],
        "address_comparison": (
            "new_candidate" if not existing else "existing_address_requires_diff_review"
        ),
        "missing_dependencies": missing,
        "duplicate_addresses": duplicates,
        "helical_energy_guard_present": guard_present,
        "working_tree_hyperbolic_sha256": file_hash(repo / "data/mechanics/hyperbolic_orbit.json"),
        "working_tree_hyperbolic_is_canonical_at_baseline": False,
        "outcome": "UNKNOWN" if missing or existing or duplicates or not guard_present else "PASS",
        "next_action": "Review/version the absent supporting nodes against a selected canonical commit, then rerun. A working-tree correction is not canonical acceptance; do not merge or promote during this task.",
    }


def check_canonical(repo: Path, candidate: dict[str, Any]) -> CheckResult:
    result = canonical_comparison(repo, candidate)
    return CheckResult(
        result["outcome"],
        json.dumps(result, sort_keys=True),
        "" if result["outcome"] == "PASS" else result["next_action"],
    )


def claim_analysis(repo: Path) -> dict[str, Any]:
    root = repo / "examples/feedback"
    ledger = json.loads((root / "claim_coverage.json").read_bytes())
    original_file = root / "sources/3i_atlas_upi_case.json"
    if file_hash(original_file) != ledger["original_sha256"]:
        raise ValueError("Original case hash mismatch.")
    original = leaves(json.loads(original_file.read_bytes()))
    for source in ledger["sources"].values():
        path = (root / source["path"]).resolve()
        if (
            not path.is_relative_to(root.resolve())
            or file_hash(path) != source["sha256"]
            or not source["version"]
        ):
            raise ValueError("Claim source version/hash mismatch.")
    covered: set[str] = set()
    ids: set[str] = set()
    counts: dict[str, int] = {}
    blockers = []
    for claim in ledger["claims"]:
        if claim["id"] in ids or claim["status"] not in {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}:
            raise ValueError("Duplicate claim id or invalid status.")
        ids.add(claim["id"])
        if not claim["source_paths"] or set(claim["source_paths"]) != set(claim["original_values"]):
            raise ValueError("Claim inventory missing source text.")
        for pointer in claim["source_paths"]:
            if pointer not in original or original[pointer] != claim["original_values"][pointer]:
                raise ValueError("Claim text differs from original.")
            covered.add(pointer)
        if not claim["scope"] or not claim["falsification_condition"] or not claim["evidence"]:
            raise ValueError("Claim scope/evidence/falsification missing.")
        if any(key not in ledger["sources"] for key in claim["evidence"]):
            raise ValueError("Unknown claim evidence reference.")
        counts[claim["status"]] = counts.get(claim["status"], 0) + 1
        if claim["blocks_case"] or claim["status"] == "STOP":
            if not claim["stop_reason"] or not claim["next_action"]:
                raise ValueError("Unresolved claim lacks reason or next action.")
            blockers.append(
                {
                    key: claim[key]
                    for key in ("id", "source_paths", "status", "stop_reason", "next_action")
                }
            )
    if covered != set(original):
        raise ValueError("Original fields are missing from claim coverage.")
    source = json.loads((root / ledger["sources"]["jpl"]["path"]).read_bytes())
    force = ledger["non_gravitational"]
    if (
        force["parameters"] != source["orbit"]["model_pars"]
        or force["two_body_sufficient"] is not False
    ):
        raise ValueError("Non-gravitational model was omitted, altered or misrepresented.")
    if (
        force["long_term_propagation_status"] != "STOP"
        or not force["stop_reason"]
        or not force["next_action"]
    ):
        raise ValueError("Propagation boundary is missing.")
    return {
        "covered_leaf_count": len(covered),
        "claim_count": len(ids),
        "status_counts": counts,
        "coverage_outcome": "PASS",
        "unresolved_claims": blockers,
        "non_gravitational": force,
    }


def check_claim_coverage(repo: Path) -> CheckResult:
    report = claim_analysis(repo)
    return CheckResult(
        "PASS",
        f"{report['claim_count']} classified groups cover all {report['covered_leaf_count']} original leaves; this verifies coverage, not truth of every claim.",
    )


def check_claim_resolution(repo: Path) -> CheckResult:
    report = claim_analysis(repo)
    return CheckResult(
        "UNKNOWN",
        json.dumps(
            {
                "unresolved_claims": report["unresolved_claims"],
                "propagation": report["non_gravitational"],
            },
            sort_keys=True,
        ),
        "Resolve each listed claim with its named observation/action; use a full-force model for propagation. Keep unrelated claims separate.",
    )


def binding_snapshot(repo: Path) -> dict[str, Any]:
    """Bind the current inputs; generated logs/receipts/reports are deliberately excluded."""
    root = repo / "examples/feedback"
    candidate = json.loads((root / "candidates/3i_atlas_upi_case.json").read_bytes())
    paths: set[Path] = set()
    for directory in (
        "src",
        "schemas",
        "tests",
        "data",
        "docs",
        "prompts",
        "projects/resonancefs/src",
        "projects/resonancefs/tests",
    ):
        paths.update(
            p
            for p in (repo / directory).rglob("*")
            if p.is_file()
            and "__pycache__" not in p.parts
            and not any(part.endswith(".egg-info") for part in p.parts)
        )
    for name in (
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "README.sv.md",
        "AGENTS.md",
        ".gitattributes",
        ".gitignore",
        ".github/workflows/ci.yml",
        ".github/workflows/upi-full-audit.yml",
        "projects/resonancefs/pyproject.toml",
    ):
        if (repo / name).is_file():
            paths.add(repo / name)
    paths.update(root.glob("*.py"))
    generated = {
        "test_receipt.json",
        "atlas_review_result.json",
        "canonical_comparison.json",
        "claim_analysis_result.json",
    }
    paths.update(
        p
        for p in (repo / "examples").rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and not p.is_relative_to(root / "runs")
        and not (p.parent == root and p.name in generated)
    )
    paths.update(p for p in (root / "sources").rglob("*") if p.is_file())
    paths.update(
        [
            root / "claim_coverage.json",
            root / "canonical_baseline.json",
            root / "candidates/3i_atlas_upi_case.json",
        ]
    )
    inputs = {p.relative_to(repo).as_posix(): file_hash(p) for p in sorted(paths)}
    ledger = json.loads((root / "claim_coverage.json").read_bytes())
    return {
        "candidate": {
            "version": candidate["version"],
            "json_sha256": digest_json(candidate),
            "file_sha256": file_hash(root / "candidates/3i_atlas_upi_case.json"),
        },
        "sources": ledger["sources"],
        "orbital_support": {
            "version": json.loads((repo / "data/mechanics/hyperbolic_orbit.json").read_bytes())[
                "version"
            ],
            "sha256": file_hash(repo / "data/mechanics/hyperbolic_orbit.json"),
        },
        "canonical_commit": BASELINE_COMMIT,
        "baseline_sha256": inputs["examples/feedback/canonical_baseline.json"],
        "validation": {
            "policy_version": POLICY_VERSION,
            "working_tree_sha256": digest_json(inputs),
            "base_commit": BASELINE_COMMIT,
            "note": "Uncommitted validation code is identified by the full input hash inventory, not by the base commit alone.",
        },
        "inputs": inputs,
        "verification_type": "software_test",
    }


def validate_test_receipt(repo: Path, receipt: dict[str, Any]) -> list[str]:
    current = binding_snapshot(repo)
    binding_id = digest_json(current)
    errors = []
    if receipt.get("binding") != current or receipt.get("binding_sha256") != binding_id:
        errors.append("Candidate, sources, code, baseline, claims or exact test files changed.")
    if receipt.get("verification_type") != "software_test" or receipt.get("state") != "PASS":
        errors.append("Receipt is not a passing software_test run.")
    suites = receipt.get("suites", [])
    if {suite.get("name") for suite in suites} != {"main", "resonancefs", "javascript"} or len(
        suites
    ) != 3:
        errors.append("Required complete test suites are absent or duplicated.")
    for suite in suites:
        ids = suite.get("collected", [])
        results = suite.get("results", [])
        if (
            not ids
            or len(set(ids)) != len(ids)
            or sorted(ids) != sorted(item["nodeid"] for item in results)
            or suite.get("test_set_sha256") != digest_json(sorted(ids))
            or suite.get("exit_code") != 0
        ):
            errors.append(f"{suite.get('name')}: incomplete/failed test set.")
        if (
            suite.get("binding_sha256") != binding_id
            or not suite.get("command")
            or not suite.get("environment")
        ):
            errors.append("Suite lacks binding, command or environment.")
        for result in results:
            if (
                result.get("outcome") != "passed"
                or result.get("binding_sha256") != binding_id
                or result.get("verification_type") != "software_test"
            ):
                errors.append("A test result is failed, skipped or unbound.")
        log = (repo / suite["log_path"]).resolve()
        if (
            not log.is_relative_to(repo.resolve())
            or not log.is_file()
            or file_hash(log) != suite.get("log_sha256")
        ):
            errors.append("Test log is missing or changed.")
        if suite.get("name") in {"main", "resonancefs"}:
            raw_path = (repo / suite.get("result_path", "missing")).resolve()
            if (
                not raw_path.is_relative_to(repo.resolve())
                or not raw_path.is_file()
                or file_hash(raw_path) != suite.get("result_sha256")
            ):
                errors.append("Raw pytest collection/results missing or changed.")
                continue
            raw = json.loads(raw_path.read_bytes())
            stripped = [
                {k: v for k, v in item.items() if k not in {"binding_sha256", "verification_type"}}
                for item in results
            ]
            if (
                raw.get("collected") != ids
                or raw.get("results") != stripped
                or raw.get("exit_code") != 0
            ):
                errors.append("Receipt disagrees with raw pytest collection/results.")
            if raw.get("pytest_args", [])[:4] != ["tests", "-q", "-p", "no:cacheprovider"]:
                errors.append("Unexpected pytest selection.")
            suite_root = repo if suite["name"] == "main" else repo / "projects/resonancefs"
            expected_files = {
                p.relative_to(suite_root).as_posix()
                for p in (suite_root / "tests").rglob("test_*.py")
            }
            observed_files = {nodeid.split("::")[0].replace("\\", "/") for nodeid in ids}
            if expected_files != observed_files:
                errors.append("Not every declared test file was collected.")
        elif suite.get("name") == "javascript" and log.is_file():
            matches = re.findall(
                r"^(ok|not ok) \d+ - (.+)$", log.read_text(encoding="utf-8"), re.MULTILINE
            )
            if [name for _, name in matches] != ids or any(state != "ok" for state, _ in matches):
                errors.append("JavaScript receipt disagrees with TAP output.")
            if suite.get("command") != [
                "node",
                "--test",
                "--test-reporter=tap",
                "tests/test_lab_math.cjs",
            ]:
                errors.append("Unexpected JavaScript test set.")
    quality = receipt.get("quality_checks", [])
    if {item.get("name") for item in quality} != {
        "ruff",
        "mypy",
        "resonance_ruff",
        "resonance_mypy",
    } or len(quality) != 4:
        errors.append("Required lint/type checks missing.")
    for item in quality:
        path = (repo / item["log_path"]).resolve()
        if (
            item.get("exit_code") != 0
            or item.get("binding_sha256") != binding_id
            or not path.is_relative_to(repo.resolve())
            or not path.is_file()
            or file_hash(path) != item.get("log_sha256")
        ):
            errors.append("Quality check failed or unbound.")
    return errors


def check_software_binding(repo: Path) -> CheckResult:
    path = repo / "examples/feedback/test_receipt.json"
    if not path.exists():
        return CheckResult(
            "UNKNOWN",
            "No bound full-suite receipt exists.",
            "Run examples/feedback/run_validation.py on the final inputs.",
        )
    errors = validate_test_receipt(repo, json.loads(path.read_bytes()))
    return CheckResult(
        "UNKNOWN" if errors else "PASS",
        (
            "; ".join(errors)
            if errors
            else f"All recorded test results bind to current inputs; receipt SHA256 {file_hash(path)}."
        ),
        (
            "Run examples/feedback/run_validation.py after resolving the reported binding failures."
            if errors
            else ""
        ),
    )
