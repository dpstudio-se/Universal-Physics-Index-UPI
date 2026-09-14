"""Run an offline review of pinned repository claims, not raw 3I observations."""

import json
import math
from pathlib import Path

from upi.atlas_gates import (
    check_canonical,
    check_claim_coverage,
    check_claim_resolution,
    check_software_binding,
)
from upi.feedback import CheckResult, EvidenceArtifact, Quantity, review_node
from upi.orbital_review import check_signed_periapsis_equation
from upi.orbital_source import SBDB_URL, check_candidate_binding, inspect_sbdb
from upi.schema_resources import schema_path
from upi.validation import validate_node_json

REVISION = "2aa811bf9594a8b4aae06287fa800e65c7f4aa57"
BASE = f"https://github.com/dpstudio-se/Universal-Physics-Index-UPI/blob/{REVISION}"
FILES = (
    (
        "data/examples/3i_atlas_upi_case.json",
        "e2af2d3f16967e1584dcae840e87cd524c06f3617dc9bb4aed25af6fbefeeea6",
    ),
    (
        "data/mechanics/hyperbolic_orbit.json",
        "6f71ad54a3e335fcfd95941a7fe903b5b066ea3bb44641bf117bb86df00ac555",
    ),
)


def run_legacy_review(*, use_original=False):
    artifacts = tuple(
        EvidenceArtifact(
            f"{BASE}/{path}",
            (Path(__file__).parent / "sources" / Path(path).name).read_bytes(),
            digest,
        )
        for path, digest in FILES
    )
    if not use_original:
        corrected = Path(__file__).resolve().parents[2] / "data/mechanics/hyperbolic_orbit.json"
        artifacts = (
            artifacts[0],
            EvidenceArtifact(
                "workspace:data/mechanics/hyperbolic_orbit.json@0.1.1",
                corrected.read_bytes(),
                "db6fd8853dfd6c4bd38af007f3167fa0d8198c5602500ac0ee074f88474df9ff",
            ),
        )
    case = json.loads(artifacts[0].content)
    orbit = json.loads(artifacts[1].content)
    parameters = case["orbital_parameters"]
    candidate = {
        "address": "UPI<physics,2,celestial_mechanics,atlas_semimajor_review>",
        "title": "Scoped review of approximate semimajor-axis calculation",
        "description": "Derived projection from a pinned repository case; not a primary observation.",
        "status": "DER",
        "evidence": [{"type": "calculation", "source": artifact.source} for artifact in artifacts],
    }

    def derive(evidence):
        inputs = json.loads(evidence[0].content)["orbital_parameters"]
        e = inputs["eccentricity"]["value_approx"]
        q = inputs["perihelion_distance_AU"]["value_approx"]
        return Quantity(q / (1 - e), "AU", "signed Newtonian two-body semimajor axis")

    def physics(node, evidence):
        return check_signed_periapsis_equation(
            orbit,
            eccentricity=parameters["eccentricity"]["value_approx"],
            periapsis=parameters["perihelion_distance_AU"]["value_approx"],
        )

    def case_schema(node, evidence):
        valid, errors = validate_node_json(case, schema_path("node"))
        return CheckResult(
            "PASS" if valid else "FAIL",
            "Source case schema passed." if valid else "\n".join(errors),
            (
                ""
                if valid
                else "Correct the original case record's schema before considering its publication."
            ),
        )

    return review_node(
        candidate,
        human_intent="Review the existing 3I/ATLAS case and return conflicts and missing evidence to me.",
        expected=Quantity(
            parameters["semimajor_axis_AU"]["value_approx"],
            "AU",
            "signed Newtonian two-body semimajor axis",
        ),
        evidence=artifacts,
        derive_from_evidence=derive,
        absolute_tolerance=0.0005,  # Rounding control only; not an observational uncertainty.
        checks={
            "physics": physics,
            "source_case_schema": case_schema,
            "observation_binding": lambda node, evidence: CheckResult(
                "UNKNOWN",
                "Pinned case supplies approximate values without a bound solution epoch, frame and uncertainty.",
                "Bind e and q to a versioned primary orbital solution with epoch, frame and uncertainties.",
            ),
        },
        required_checks=(
            "physics",
            "source_case_schema",
            "observation_binding",
            "canonical",
            "software_tests",
        ),
    )


def run_review(*, use_original=False, use_primary=True):
    if use_original or not use_primary:
        return run_legacy_review(use_original=use_original)
    root = Path(__file__).resolve().parent
    candidate = json.loads((root / "candidates/3i_atlas_upi_case.json").read_bytes())
    manifest = json.loads((root / "sources/jpl_3i_atlas_manifest.json").read_bytes())
    artifacts = (
        EvidenceArtifact(
            SBDB_URL, (root / "sources/jpl_3i_atlas_sbdb.json").read_bytes(), manifest["sha256"]
        ),
        EvidenceArtifact(
            "workspace:data/mechanics/hyperbolic_orbit.json@0.1.1",
            (root.parents[1] / "data/mechanics/hyperbolic_orbit.json").read_bytes(),
            "db6fd8853dfd6c4bd38af007f3167fa0d8198c5602500ac0ee074f88474df9ff",
        ),
    )

    def derive(evidence):
        solution = inspect_sbdb(evidence[0], manifest)
        return Quantity(
            solution["derived_a"], "AU", "signed osculating semimajor axis at JPL solution epoch"
        )

    def binding(node, evidence):
        try:
            solution = inspect_sbdb(evidence[0], manifest)
        except (ValueError, KeyError, TypeError, IndexError):
            return CheckResult(
                "UNKNOWN",
                "Primary solution metadata or covariance is incomplete/inconsistent.",
                "Inspect the pinned response and manifest; restore the missing source field.",
            )
        errors = check_candidate_binding(node, solution)
        return CheckResult(
            "FAIL" if errors else "PASS",
            (
                "; ".join(errors)
                if errors
                else f'JPL solution {solution["orbit_id"]}: candidate values, epoch, frame, formal sigmas and source digest match.'
            ),
            "Correct candidate/source bindings." if errors else "",
        )

    def physics(node, evidence):
        solution = inspect_sbdb(evidence[0], manifest)
        return check_signed_periapsis_equation(
            json.loads(evidence[1].content), eccentricity=solution["e"], periapsis=solution["q"]
        )

    def uncertainty(node, evidence):
        solution = inspect_sbdb(evidence[0], manifest)
        passed = math.isclose(
            solution["derived_sigma_a"], solution["sigma_a"], rel_tol=1e-4, abs_tol=0
        )
        return CheckResult(
            "PASS" if passed else "FAIL",
            f'DER sigma_a={solution["derived_sigma_a"]} AU from correlated e/q covariance; JPL sigma_a={solution["sigma_a"]} AU. Relative rounding tolerance=1e-4.',
            "" if passed else "Inspect covariance ordering, epoch and uncertainty propagation.",
            verification_type="mathematical_check",
        )

    def case_schema(node, evidence):
        valid, errors = validate_node_json(node, schema_path("node"))
        return CheckResult(
            "PASS" if valid else "FAIL",
            "Scoped candidate fits the actual node schema." if valid else "\n".join(errors),
            "" if valid else "Correct the scoped candidate schema.",
        )

    quantities = {item["name"]: item for item in candidate["quantities"]}
    return review_node(
        candidate,
        human_intent="Audit the primary 3I/ATLAS orbital solution and remaining boundaries; do not promote.",
        expected=Quantity(
            quantities["semimajor_axis"]["value"],
            "AU",
            "signed osculating semimajor axis at JPL solution epoch",
        ),
        evidence=artifacts,
        derive_from_evidence=derive,
        absolute_tolerance=1e-12,
        checks={
            "physics": physics,
            "source_case_schema": case_schema,
            "observation_binding": binding,
            "uncertainty": uncertainty,
            "canonical": lambda node, evidence: check_canonical(root.parents[1], node),
            "software_tests": lambda node, evidence: check_software_binding(root.parents[1]),
            "claim_coverage": lambda node, evidence: check_claim_coverage(root.parents[1]),
            "claim_resolution": lambda node, evidence: check_claim_resolution(root.parents[1]),
        },
        required_checks=(
            "physics",
            "source_case_schema",
            "observation_binding",
            "uncertainty",
            "claim_coverage",
            "claim_resolution",
            "canonical",
            "software_tests",
        ),
    )


if __name__ == "__main__":
    print(json.dumps(run_review().as_dict(), indent=2, ensure_ascii=False, allow_nan=False))
