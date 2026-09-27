"""verification_type: software_test; source classification is not experimental validation."""

import json
import shutil
from pathlib import Path

import pytest

from upi.atlas_gates import (
    BASELINE_COMMIT,
    binding_snapshot,
    canonical_comparison,
    claim_analysis,
    digest_json,
    file_hash,
    validate_test_receipt,
)

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "examples/feedback"


def test_committed_baseline_does_not_absorb_uncommitted_dependencies():
    candidate = json.loads((ROOT / "candidates/3i_atlas_upi_case.json").read_bytes())
    result = canonical_comparison(REPO, candidate)
    assert result["baseline_commit"] == BASELINE_COMMIT
    assert result["record_count"] == 99
    assert result["address_comparison"] == "new_candidate"
    assert result["helical_energy_guard_present"] is True
    assert len(result["missing_dependencies"]) == 3
    assert result["working_tree_hyperbolic_is_canonical_at_baseline"] is False
    assert result["outcome"] == "UNKNOWN"


def test_claim_coverage_is_complete_without_promoting_unresolved_claims():
    result = claim_analysis(REPO)
    assert result["coverage_outcome"] == "PASS"
    assert result["covered_leaf_count"] == 104
    assert result["claim_count"] == 43
    assert set(result["status_counts"]) == {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}
    assert result["unresolved_claims"]
    assert result["non_gravitational"]["two_body_sufficient"] is False
    assert result["non_gravitational"]["long_term_propagation_status"] == "STOP"


@pytest.mark.parametrize("mutation", ["omitted", "source", "status", "reason", "force_model"])
def test_claim_coverage_rejects_incomplete_or_corrupted_ledger(tmp_path, mutation):
    root = tmp_path / "examples/feedback"
    root.mkdir(parents=True)
    shutil.copytree(ROOT / "sources", root / "sources")
    shutil.copyfile(ROOT / "canonical_baseline.json", root / "canonical_baseline.json")
    ledger = json.loads((ROOT / "claim_coverage.json").read_bytes())
    if mutation == "omitted":
        ledger["claims"].pop(0)
    elif mutation == "source":
        ledger["sources"]["hubble"]["sha256"] = "0" * 64
    elif mutation == "status":
        ledger["claims"][0]["status"] = "EST/DER"
    elif mutation == "reason":
        next(item for item in ledger["claims"] if item["blocks_case"])["next_action"] = ""
    else:
        ledger["non_gravitational"]["parameters"] = []
    (root / "claim_coverage.json").write_text(json.dumps(ledger), encoding="utf-8")
    with pytest.raises(ValueError):
        claim_analysis(tmp_path)


def test_binding_tracks_versions_code_sources_and_exact_test_files():
    binding = binding_snapshot(REPO)
    assert binding["candidate"]["version"] == "0.2.1"
    assert binding["verification_type"] == "software_test"
    assert binding["sources"]["jpl"]["version"].startswith("orbit 54")
    assert "src/upi/feedback.py" in binding["inputs"]
    assert "tests/test_atlas_gates.py" in binding["inputs"]
    assert "examples/feedback/test_recorder.py" in binding["inputs"]
    assert binding["validation"]["working_tree_sha256"] == digest_json(binding["inputs"])


def test_empty_green_receipt_does_not_pass():
    binding = binding_snapshot(REPO)
    receipt = {
        "state": "PASS",
        "verification_type": "software_test",
        "binding": binding,
        "binding_sha256": digest_json(binding),
        "suites": [],
        "quality_checks": [],
    }
    assert validate_test_receipt(REPO, receipt)


def test_stale_input_receipt_does_not_pass():
    binding = binding_snapshot(REPO)
    receipt = {
        "state": "PASS",
        "verification_type": "software_test",
        "binding": binding,
        "binding_sha256": "0" * 64,
        "suites": [],
        "quality_checks": [],
    }
    assert any("changed" in error for error in validate_test_receipt(REPO, receipt))


@pytest.fixture
def receipt_fixture(tmp_path, monkeypatch):
    """Synthetic receipt-format control; does not claim these fixture tests executed."""
    from upi import atlas_gates

    binding = {"fixture": True}
    binding_id = digest_json(binding)
    monkeypatch.setattr(atlas_gates, "binding_snapshot", lambda repo: binding)
    receipt = {
        "binding": binding,
        "binding_sha256": binding_id,
        "state": "PASS",
        "verification_type": "software_test",
        "suites": [],
        "quality_checks": [],
    }
    for name, folder in [("main", tmp_path), ("resonancefs", tmp_path / "projects/resonancefs")]:
        (folder / "tests").mkdir(parents=True)
        (folder / "tests/test_control.py").write_text("# synthetic fixture", encoding="utf-8")
        ids = ["tests/test_control.py::test_control"]
        result = {
            "nodeid": ids[0],
            "outcome": "passed",
            "phases": {"setup": "passed", "call": "passed", "teardown": "passed"},
        }
        raw_path = tmp_path / f"{name}.json"
        raw_path.write_text(
            json.dumps(
                {
                    "collected": ids,
                    "results": [result],
                    "exit_code": 0,
                    "pytest_args": ["tests", "-q", "-p", "no:cacheprovider"],
                }
            ),
            encoding="utf-8",
        )
        log = tmp_path / f"{name}.log"
        log.write_text("synthetic format control", encoding="utf-8")
        receipt["suites"].append(
            {
                "name": name,
                "collected": ids,
                "results": [
                    {**result, "binding_sha256": binding_id, "verification_type": "software_test"}
                ],
                "binding_sha256": binding_id,
                "test_set_sha256": digest_json(ids),
                "exit_code": 0,
                "command": ["synthetic"],
                "environment": {"synthetic": True},
                "log_path": log.name,
                "log_sha256": file_hash(log),
                "result_path": raw_path.name,
                "result_sha256": file_hash(raw_path),
            }
        )
    log = tmp_path / "js.log"
    log.write_text("ok 1 - synthetic-control\n", encoding="utf-8")
    receipt["suites"].append(
        {
            "name": "javascript",
            "collected": ["synthetic-control"],
            "results": [
                {
                    "nodeid": "synthetic-control",
                    "outcome": "passed",
                    "binding_sha256": binding_id,
                    "verification_type": "software_test",
                }
            ],
            "binding_sha256": binding_id,
            "test_set_sha256": digest_json(["synthetic-control"]),
            "exit_code": 0,
            "command": ["node", "--test", "--test-reporter=tap", "tests/test_lab_math.cjs"],
            "environment": {"synthetic": True},
            "log_path": log.name,
            "log_sha256": file_hash(log),
        }
    )
    for name in ("ruff", "mypy", "resonance_ruff", "resonance_mypy"):
        receipt["quality_checks"].append(
            {
                "name": name,
                "exit_code": 0,
                "binding_sha256": binding_id,
                "log_path": log.name,
                "log_sha256": file_hash(log),
            }
        )
    return tmp_path, receipt


def test_complete_receipt_format_can_pass(receipt_fixture):
    repo, receipt = receipt_fixture
    assert validate_test_receipt(repo, receipt) == []


@pytest.mark.parametrize(
    "mutation", ["omitted", "failed", "unbound", "test_set", "log", "raw", "new_file"]
)
def test_receipt_rejects_lost_or_changed_test_evidence(receipt_fixture, mutation):
    repo, receipt = receipt_fixture
    suite = receipt["suites"][0]
    if mutation == "omitted":
        suite["results"] = []
    elif mutation == "failed":
        suite["results"][0]["outcome"] = "failed"
    elif mutation == "unbound":
        suite["results"][0]["binding_sha256"] = "other"
    elif mutation == "test_set":
        suite["test_set_sha256"] = "other"
    elif mutation == "log":
        (repo / suite["log_path"]).write_text("changed", encoding="utf-8")
    elif mutation == "raw":
        (repo / suite["result_path"]).write_text("{}", encoding="utf-8")
    else:
        (repo / "tests/test_missing.py").write_text("# not collected", encoding="utf-8")
    assert validate_test_receipt(repo, receipt)
