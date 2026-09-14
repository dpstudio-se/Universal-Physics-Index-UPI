"""Scoped checks for the pinned 3I/ATLAS JPL orbit solution.

Validates published fit metadata and the e/q covariance submatrix; does not
refit astrometry, validate the full dynamical model, or authenticate a digest.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime
from typing import Any

from .feedback import EvidenceArtifact

SBDB_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=3I&full-prec=true&cov=mat"
SBDB_DOC = "https://ssd-api.jpl.nasa.gov/doc/sbdb.html"
FRAME = "heliocentric IAU76/80 ecliptic J2000"


def _number(value: Any, name: str) -> float:
    if value is None or isinstance(value, bool):
        raise ValueError(f"Missing or invalid {name}.")
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Missing or invalid {name}.") from None
    if not math.isfinite(number):
        raise ValueError(f"Non-finite {name}.")
    return number


def inspect_sbdb(artifact: EvidenceArtifact, manifest: dict[str, Any]) -> dict[str, Any]:
    """Require complete, mutually consistent source metadata before calculation."""
    if artifact.source != SBDB_URL or manifest.get("source_url") != SBDB_URL:
        raise ValueError("Unexpected source URL.")
    digest = hashlib.sha256(artifact.content).hexdigest()
    if digest != artifact.expected_sha256 or digest != manifest.get("sha256"):
        raise ValueError("Source digest mismatch.")
    data = json.loads(artifact.content)
    orbit = data["orbit"]
    if data["signature"] != {"version": "1.3", "source": "NASA/JPL Small-Body Database (SBDB) API"}:
        raise ValueError("Unsupported SBDB signature/version.")
    if data["object"].get("des") != "2025 N1" or data["object"].get("spkid") != "1004083":
        raise ValueError("Source object is not the bound ATLAS designation/SPK identity.")
    if orbit.get("source") != "JPL" or not orbit.get("producer"):
        raise ValueError("Missing JPL solution producer.")
    for field, actual in {
        "api_version": data["signature"]["version"],
        "object_designation": data["object"]["des"],
        "spkid": data["object"]["spkid"],
        "orbit_id": orbit.get("orbit_id"),
        "solution_date": orbit.get("soln_date"),
        "epoch_jd_tdb": orbit.get("epoch"),
        "equinox": orbit.get("equinox"),
    }.items():
        if actual is None or actual == "" or manifest.get(field) != actual:
            raise ValueError(f"Missing or mismatched {field}.")
    if data["object"].get("orbit_id") != orbit["orbit_id"]:
        raise ValueError("Object and orbit solution ids disagree.")
    datetime.fromisoformat(orbit["soln_date"])
    date.fromisoformat(manifest["retrieved_on"])
    if (
        orbit["equinox"] != "J2000"
        or manifest.get("frame") != FRAME
        or manifest.get("field_definitions_source") != SBDB_DOC
    ):
        raise ValueError("Missing or unsupported documented reference frame.")
    epoch = _number(orbit["epoch"], "epoch")
    if epoch <= 0:
        raise ValueError("Invalid epoch.")
    elements = {item["name"]: item for item in orbit["elements"]}
    if len(elements) != len(orbit["elements"]):
        raise ValueError("Duplicate orbital element names.")
    numbers = {}
    for name, unit in {"e": None, "q": "au", "a": "au", "i": "deg"}.items():
        element = elements[name]
        if element.get("units") != unit:
            raise ValueError(f"Unexpected units for {name}.")
        numbers[name] = _number(element.get("value"), name)
        numbers[f"sigma_{name}"] = _number(element.get("sigma"), f"sigma_{name}")
        if numbers[f"sigma_{name}"] <= 0:
            raise ValueError(f"Missing positive uncertainty for {name}.")
    if numbers["e"] <= 1 or numbers["q"] <= 0 or numbers["a"] >= 0:
        raise ValueError("Outside the signed-a hyperbolic domain.")
    covariance = orbit.get("covariance")
    if (
        not isinstance(covariance, dict)
        or _number(covariance.get("epoch"), "covariance epoch") != epoch
    ):
        raise ValueError("Missing covariance or mismatched covariance epoch.")
    labels = covariance["labels"]
    matrix = covariance["data"]
    if (
        len(set(labels)) != len(labels)
        or len(matrix) != len(labels)
        or any(len(row) != len(labels) for row in matrix)
    ):
        raise ValueError("Invalid covariance shape/labels.")
    ie, iq = labels.index("e"), labels.index("q")
    cee = _number(matrix[ie][ie], "C_ee")
    cqq = _number(matrix[iq][iq], "C_qq")
    ceq = _number(matrix[ie][iq], "C_eq")
    cqe = _number(matrix[iq][ie], "C_qe")
    if (
        cee <= 0
        or cqq <= 0
        or not math.isclose(ceq, cqe, rel_tol=1e-12, abs_tol=0)
        or ceq * ceq > cee * cqq
    ):
        raise ValueError("Invalid e/q covariance submatrix.")
    for variance, sigma in [(cee, numbers["sigma_e"]), (cqq, numbers["sigma_q"])]:
        if not math.isclose(math.sqrt(variance), sigma, rel_tol=1e-4, abs_tol=0):
            raise ValueError("Covariance diagonal disagrees with rounded element sigma.")
    e, q = numbers["e"], numbers["q"]
    de, dq = q / (1 - e) ** 2, 1 / (1 - e)
    variance_a = de * de * cee + dq * dq * cqq + 2 * de * dq * ceq
    if variance_a <= 0:
        raise ValueError("Non-positive propagated variance.")
    return {
        **numbers,
        "derived_a": q / (1 - e),
        "derived_sigma_a": math.sqrt(variance_a),
        "epoch": epoch,
        "orbit_id": orbit["orbit_id"],
        "source_digest": digest,
        "model_parameters": orbit.get("model_pars", []),
    }


def check_candidate_binding(node: dict[str, Any], solution: dict[str, Any]) -> list[str]:
    """Require the candidate's quantities and context to match the pinned fit."""
    errors = []
    quantities = node.get("quantities", [])
    entries = {item["name"]: item for item in quantities}
    if len(entries) != len(quantities):
        errors.append("Duplicate candidate quantities.")
    for name, key, unit in [
        ("eccentricity", "e", "1"),
        ("perihelion_distance", "q", "AU"),
        ("semimajor_axis", "a", "AU"),
        ("inclination", "i", "deg"),
    ]:
        item = entries.get(name, {})
        if (
            item.get("value") != solution[key]
            or item.get("uncertainty") != solution[f"sigma_{key}"]
            or item.get("unit") != unit
        ):
            errors.append(f"Candidate {name} value, unit or uncertainty differs from source.")
        reference = item.get("reference", "")
        if (
            SBDB_URL not in reference
            or solution["source_digest"] not in reference
            or f'JPL solution {solution["orbit_id"]};' not in reference
        ):
            errors.append(f"Candidate {name} lacks the source binding.")
    if node.get("reference_frame") != FRAME:
        errors.append("Candidate reference frame mismatch.")
    if f'Osculating epoch: JD {solution["epoch"]} TDB.' not in node.get("definitions", []):
        errors.append("Candidate epoch/time-scale mismatch.")
    return errors
