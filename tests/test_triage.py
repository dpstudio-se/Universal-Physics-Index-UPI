import json
from pathlib import Path

from upi.debug import generate_debug_report
from upi.triage import compare_report, finding_key

ROOT = Path(__file__).parents[1]
KNOWN = ROOT / "examples" / "ledger" / "baselines" / "known-findings.json"
CANONICAL = ROOT / "examples" / "ledger" / "baselines" / "baseline-1.json"


def test_three_baselines_share_one_artifact_hash() -> None:
    runs = json.loads((ROOT / "examples" / "ledger" / "baselines" / "runs.json").read_text(encoding="utf-8"))
    catalog = json.loads(KNOWN.read_text(encoding="utf-8"))
    assert runs["runs"] == 3
    assert runs["identical_artifacts"] is True
    assert runs["artifact_hash"] == catalog["artifact_hash"]
    assert runs["artifact_hash"] == (
        "b89b24577cc6250e449d3cd0eb7ddeb02f351333cb1a87b4d2be7d8f33d28f46"
    )


def test_live_report_matches_known_catalog() -> None:
    report = generate_debug_report(ROOT / "data", inspect=True)
    catalog = json.loads(KNOWN.read_text(encoding="utf-8"))
    result = compare_report(report, catalog)
    assert result["verification_type"] == "software_test"
    assert result["unexpected"] == []
    assert result["missing"] == []
    assert result["decision"] == "advance"
    assert result["heartbeat"] is True


def test_canonical_baseline_matches_live_report() -> None:
    live = generate_debug_report(ROOT / "data", inspect=True)
    stored = json.loads(CANONICAL.read_text(encoding="utf-8"))
    live_keys = sorted(finding_key(item) for item in live["findings"])
    stored_keys = sorted(finding_key(item) for item in stored["findings"])
    assert live_keys == stored_keys
    assert stored["verification_type"] == "software_test"
    assert stored["inspector"]["source_values_redacted"] is True


def test_unexpected_finding_requires_approval() -> None:
    catalog = json.loads(KNOWN.read_text(encoding="utf-8"))
    report = {"findings": [{"code": "UPI-X999", "status": "ERR", "path": "path:deadbeefdeadbeef"}]}
    result = compare_report(report, catalog)
    assert result["decision"] == "escalate"
    assert result["approval_required"] is True
