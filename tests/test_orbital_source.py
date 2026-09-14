"""verification_type: software_test; pinned JPL fit, not independent observation."""

import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from upi.feedback import EvidenceArtifact
from upi.orbital_source import SBDB_URL, check_candidate_binding, inspect_sbdb

ROOT = Path(__file__).resolve().parents[1] / "examples/feedback"


@pytest.fixture
def source():
    content = (ROOT / "sources/jpl_3i_atlas_sbdb.json").read_bytes()
    manifest = json.loads((ROOT / "sources/jpl_3i_atlas_manifest.json").read_bytes())
    return EvidenceArtifact(SBDB_URL, content, manifest["sha256"]), manifest


def test_pinned_solution_metadata_and_correlated_uncertainty(source):
    result = inspect_sbdb(*source)
    assert result["orbit_id"] == "54"
    assert result["epoch"] == 2461090.5
    assert result["derived_a"] == pytest.approx(-0.2638374502507929, abs=1e-15)
    assert result["derived_sigma_a"] == pytest.approx(result["sigma_a"], rel=1e-4)
    assert result["e"] - 3 * result["sigma_e"] > 1
    assert {entry["name"] for entry in result["model_parameters"]} >= {"A1", "A2", "A3", "DT"}
    candidate = json.loads((ROOT / "candidates/3i_atlas_upi_case.json").read_bytes())
    assert check_candidate_binding(candidate, result) == []


@pytest.mark.parametrize(
    "field", ["orbit_id", "epoch_jd_tdb", "equinox", "solution_date", "frame", "sha256"]
)
def test_missing_manifest_metadata_blocks(source, field):
    artifact, manifest = source
    manifest.pop(field)
    with pytest.raises(ValueError):
        inspect_sbdb(artifact, manifest)


@pytest.mark.parametrize(
    "mutation",
    ["sigma", "units", "object", "epoch", "cov_epoch", "covariance", "asymmetry", "variance"],
)
def test_source_metadata_and_covariance_cannot_silently_pass(source, mutation):
    artifact, manifest = source
    data = json.loads(artifact.content)
    orbit = data["orbit"]
    elements = {item["name"]: item for item in orbit["elements"]}
    if mutation == "sigma":
        elements["e"]["sigma"] = None
    elif mutation == "units":
        elements["q"]["units"] = "km"
    elif mutation == "object":
        data["object"]["spkid"] = "other"
    elif mutation == "epoch":
        orbit.pop("epoch")
    elif mutation == "cov_epoch":
        orbit["covariance"]["epoch"] = "2460000.5"
    elif mutation == "covariance":
        orbit["covariance"] = None
    elif mutation == "asymmetry":
        orbit["covariance"]["data"][0][1] = "1"
    else:
        orbit["covariance"]["data"][0][0] = "-1"
    # Bind new bytes so the test reaches metadata checks, not only the digest guard.
    content = json.dumps(data).encode()
    digest = hashlib.sha256(content).hexdigest()
    manifest["sha256"] = digest
    with pytest.raises(ValueError):
        inspect_sbdb(EvidenceArtifact(SBDB_URL, content, digest), manifest)


@pytest.mark.parametrize(
    "field,value", [("value", 99), ("unit", "km"), ("uncertainty", None), ("reference", "unbound")]
)
def test_candidate_cannot_diverge_from_bound_solution(source, field, value):
    solution = inspect_sbdb(*source)
    candidate = json.loads((ROOT / "candidates/3i_atlas_upi_case.json").read_bytes())
    candidate["quantities"][1][field] = value
    assert check_candidate_binding(candidate, solution)


def test_complete_primary_review_resolves_only_its_scoped_barriers():
    example = runpy.run_path(str(ROOT / "review_atlas.py"))
    report = example["run_review"]()
    assert report.comparison == "AGREE"
    assert report.proposed_status == "STOP"
    assert report.promotion_gate == "BLOCKED"
    assert report.checks["source_case_schema"].outcome == "PASS"
    assert report.checks["observation_binding"].outcome == "PASS"
    assert report.checks["uncertainty"].outcome == "PASS"
    remaining = {name for name, check in report.checks.items() if check.outcome != "PASS"}
    assert {"canonical", "claim_resolution"} <= remaining
    assert remaining <= {"canonical", "claim_resolution", "software_tests"}
    assert report.checks["claim_coverage"].outcome == "PASS"
    assert all(report.checks[name].next_observation for name in remaining)
    assert report.as_dict()["review_result"]["evidence_result"]["independence"].endswith(
        "not_established"
    )


def test_manifest_and_artifact_digest_must_both_match(source):
    artifact, manifest = source
    altered = deepcopy(manifest)
    altered["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest"):
        inspect_sbdb(artifact, altered)
