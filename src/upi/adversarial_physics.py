"""Freeze a conditional prediction before calculating the supplied recoil comparison.

Run from the repository: python -m upi.adversarial_physics --output <new-directory>.
Existing freeze files are never overwritten. No external observations are fetched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, replace
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path

from .constants import C
from .dark_matter_candidate import (
    GEV_KG,
    KEV_J,
    Halo,
    frequency_chain,
    inverse_speed,
    rate_coefficient,
    recoil,
    target_mass,
)
from .knot import analyze
from .knot_model import Observation, PathTrace, Step, Tolerance
from .models import ScientificStatus
from .physics import frequency_from_mass


def write_once(path: Path, record: dict) -> str:
    raw = (json.dumps(record, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
    digest = hashlib.sha256(raw).hexdigest()
    with path.with_suffix(".sha256").open("x", encoding="ascii") as stream:
        stream.write(digest+"\n")
    return digest


def read_verified(path: Path) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != path.with_suffix(".sha256").read_text().strip():
        raise ValueError("frozen record hash mismatch")
    result: dict = json.loads(raw)
    return result


def sensitivity() -> list[dict]:
    with localcontext() as ctx:
        ctx.prec = 80
        baseline = frequency_chain()
        rows = []
        for f0 in ("7.83", "7.834", "8.0"):
            row = frequency_chain(f0)
            delta = Decimal(f0)-Decimal("7.834")
            row.update(delta_f0_Hz=str(delta), relative_difference=str(delta/Decimal("7.834")),
                       delta_f84_Hz=str(delta*Decimal(2)**84),
                       delta_mass_GeV_c2=str(Decimal(row["mass_equivalent_GeV_c2"])-Decimal(baseline["mass_equivalent_GeV_c2"])))
            rows.append(row)
        return rows


def oden_checks(frozen: dict) -> dict:
    """Reuse ODEN with common-law provenance; two code paths are not two experiments."""
    chi = float(frozen["arithmetic"]["mass_equivalent_kg"])
    nucleus = target_mass()
    f = float(frozen["arithmetic"]["f_N_Hz"])
    reconstructed_v = inverse_speed(recoil(chi,nucleus,600000)["recoil_keV"]*KEV_J,chi,nucleus)
    results = []
    for key, unit, a, b in (("frequency-roundtrip", "Hz", f, frequency_from_mass(chi)),
                            ("recoil-roundtrip", "m/s", 600000., reconstructed_v)):
        left = Observation(key+"-a", key, "conditional physics", "model snapshot", "calculation",
                           "common lab frame", key, "algebraic inverse control", "direct SI",
                           1., a, unit, ("frozen prediction",), coordinate="SI lab",
                           source_group="shared physical laws and inputs", status=ScientificStatus.DER)
        right = replace(left,id=key+"-b",raw_value=b,source="inverse reconstruction",
                        provenance=("independent inverse implementation; same assumptions",))
        paths = tuple(PathTrace(obs.id,(Step(key,obs,"DERIVED_FROM","declared inverse","root",True,True,"",True),))
                      for obs in (left,right))
        tolerance = Tolerance(abs(a)*1e-12,unit,abs(a)*1e-14)
        results.append({"status": "DER", "checkpoint": key,
                        "report": analyze(paths,{key:tolerance})})
    return {"status": "DER", "verification_type": "software_test", "controls": results,
            "scope": "ODEN algebraic comparison only; source laws and assumptions are shared"}


def prediction(input_record: dict) -> dict:
    if (input_record["f0_Hz"], input_record["N_nodes"], input_record["steps_per_node"],
        input_record["N"]) != ("7.834", 7, 12, 84):
        raise ValueError("inputs differ from reviewed version 0.1.0")
    chain = frequency_chain(input_record["f0_Hz"], input_record["N"])
    chi = float(chain["mass_equivalent_kg"])
    nucleus = target_mass()
    halo = Halo()
    endpoint = recoil(chi, nucleus, halo.vesc_m_s+halo.earth_m_s)["recoil_keV"]
    grid = [float(e) for e in range(0, math.ceil(endpoint)+1, 10)] + [endpoint, endpoint+1]
    return {"status": "HYP", "model_version": "octave-recoil-0.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "code_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (Path("src/upi/dark_matter_candidate.py"), Path("src/upi/adversarial_physics.py"))},
            "verification_type": "software_test", "claims_experimental_verification": False,
            "input_record": input_record, "f0_Hz": input_record["f0_Hz"], "N": input_record["N"],
            "arithmetic": chain,
            "H_OCTAVE_84": {"status": "HYP", "state": "OPEN", "missing": "Independent physical mechanism requiring 84 doublings"},
            "H_DM": {"status": "HYP", "state": "OPEN", "candidate_GeV_c2": chain["mass_equivalent_GeV_c2"],
                     "missing": "Independent evidence for massive dark matter degree of freedom"},
            "assumptions": {"halo": asdict(halo), "halo_status": "HYP", "target": "pure Xe-131, stationary free nucleus",
                            "target_mass_kg": nucleus, "target_mass_GeV_c2": nucleus/GEV_KG,
                            "target_approximation": "atomic mass minus 54 electron masses; total electron binding omitted",
                            "interaction": "spin-independent elastic contact, sigma_A(0) unknown, no nucleon identification",
                            "form_factor": "Helm: R=1.2 A^(1/3) fm, skin=0.9 fm; phenomenological benchmark",
                            "rate_normalization": "per kg pure isotope, per day, per keV, per sigma_A in m²",
                            "detector": "no exposure, efficiency, response kernel or background supplied"},
            "predicted_range_keV": [0, endpoint],
            "predicted_spectrum_per_sigma_A": [rate_coefficient(e, chi, halo) for e in sorted(set(grid))],
            "velocity_sweep": [recoil(chi, nucleus, v*1000) for v in range(0, 776, 25)] + [recoil(chi, nucleus, 776000)],
            "frequency_sensitivity": sensitivity(),
            "uncertainty": {"status": "STOP", "stop_reason": "No measured f0 uncertainty, N-generating model, coupling or halo posterior",
                            "next_observation": "Supply independent f0 measurement with uncertainty and timestamped N derivation",
                            "conditional_propagation": "dm/m = df0/f0 at fixed integer N; dm/dN=m ln(2) for a continuous diagnostic only",
                            "SI_constants": "h,c,e exact; atomic mass and electron mass measured; ignored binding is systematic",
                            "sensitivity_is_not": "a confidence interval"},
            "falsification_criteria": ["Arithmetic disagrees with independent rational path or inverse relative residual exceeds 1e-12",
                                       "Recoil violates momentum/energy conservation or halo cutoff within declared approximation",
                                       "A dated pre-data mechanism contradicts N=84 or establishes a different step ratio",
                                       "With independently fixed nonzero sigma and calibrated response, a preregistered spectrum test rejects predictions"],
            "comparison_policy": "248 keV and mass/speed ballparks were already supplied. This is not preregistration relative to them. No additional experimental data compared."}


def adversarial_results(frozen: dict, digest: str) -> dict:
    chi = float(frozen["arithmetic"]["mass_equivalent_kg"])
    nucleus = target_mass()
    # The observation is read only after the prediction has been written and hashed.
    raw = frozen["input_record"]["known_before_freeze"]["user_supplied_recoil_keV"]
    energy = float(raw)*KEV_J
    v = inverse_speed(energy, chi, nucleus)
    points = [recoil(chi, nucleus, x) for x in (220000, v, 600000)]
    for row in points:
        speed = row["speed_km_s"]*1000
        recovered = inverse_speed(row["recoil_keV"]*KEV_J, chi, nucleus)
        row["inverse_residual_m_s"] = recovered-speed
        # Lab conservation is checked independently of the reduced-mass expression.
        target_v = row["q_kg_m_s"]/nucleus
        final_chi_v = speed-row["q_kg_m_s"]/chi
        row["energy_conservation_relative_residual"] = (
            (.5*chi*final_chi_v**2 + .5*nucleus*target_v**2)/(.5*chi*speed**2)-1)
    halo = Halo()
    perturbations = []
    for name, values in {"rho_GeV_cm3": (.2, .3, .6), "v0_m_s": (180000,220000,260000),
                         "vesc_m_s": (500000,544000,600000), "earth_m_s": (200000,232000,260000)}.items():
        for value in values:
            h = replace(halo, **{name: value})
            perturbations.append({"status": "DER", "parameter": name, "value": value,
                                  "at_supplied_energy": rate_coefficient(float(raw), chi, h),
                                  "endpoint_keV": recoil(chi, nucleus, h.vesc_m_s+h.earth_m_s)["recoil_keV"]})
    return {"status": "DER", "verification_type": "software_test", "prediction_sha256": digest,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "observation": {"status": "HYP", "raw_value": raw, "unit": "keV", "source": "user request",
                            "provenance": "experiment, event ID, recoil calibration and uncertainty not supplied; unverified observation claim"},
            "observation_boundary": {"status": "STOP", "stop_reason": "No experimental provenance for 248 keV",
                                     "next_observation": "Event/source identifier, nuclear vs electron equivalent energy, uncertainty and calibration"},
            "conditional_outcome": "KINEMATICALLY COMPATIBLE" if v <= halo.vesc_m_s+halo.earth_m_s else "OUTSIDE_DECLARED_HALO_SUPPORT",
            "minimum_speed_km_s": v/1000, "required_points": points,
            "oden_eye": oden_checks(frozen),
            "halo_perturbations": perturbations,
            "octave_perturbations": [frequency_chain("7.834", n) for n in (72,83,84,85,96)],
            "semitone_control": frequency_chain("7.834", 7),
            "isotope_perturbations": [{"status": "DER", "A": a, "mass_kg": target_mass(a),
                                       "minimum_speed_km_s": inverse_speed(energy,chi,target_mass(a))/1000,
                                       "at_600_km_s": recoil(chi,target_mass(a),600000)} for a in (129,131,132,136)],
            "binding_approximation_controls": [{"status": "DER", "assumed_binding_eV": b,
                                                "minimum_speed_km_s": inverse_speed(energy,chi,target_mass(131,b))/1000}
                                               for b in (0,100000,1000000)],
            "angle_perturbations": [recoil(chi,nucleus,600000,c) for c in (-1,-.5,0,.5,1)],
            "mass_perturbations": [{"status": "DER", "factor": factor, "at_600_km_s": recoil(chi*factor,nucleus,600000),
                                    "minimum_speed_km_s": inverse_speed(energy,chi*factor,nucleus)/1000,
                                    "inverse_within_NR_domain": inverse_speed(energy,chi*factor,nucleus) < .01*C,
                                    "within_declared_halo": inverse_speed(energy,chi*factor,nucleus) <= halo.vesc_m_s+halo.earth_m_s}
                                   for factor in (.01,.1,.5,1,2,10,100)],
            "form_factor_perturbations": [{"status": "DER", "radius_factor": r, "skin_fm": s,
                                           "rate": rate_coefficient(float(raw),chi,radius_fm=1.2*131**(1/3)*r,skin_fm=s)}
                                          for r in (.9,1,1.1) for s in (.8,.9,1)],
            "sigma_control": {"status": "DER", "result": "Rate linear in sigma_A; sigma_A=0 gives zero at every energy. No sigma value predicted."},
            "posthoc_control": {"status": "DER", "result": "Every positive recoil admits an inverse speed for every positive mass; halo bounds must then be checked. This closure does not select N or a unique mass."},
            "look_elsewhere": {"status": "STOP", "stop_reason": "No record of all tried frequencies, scales, targets or selection rule",
                               "next_observation": "Dated search history and fixed selection/likelihood protocol; no p-value can be assigned"},
            "additional_experimental_comparisons": []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, default=Path("examples/adversarial_physics/input-freeze.json"))
    args = parser.parse_args()
    inputs = read_verified(args.inputs)
    for name, expected in inputs["reused_sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Existing anchor changed: {name}")
    args.output.mkdir(parents=True, exist_ok=False)
    frozen = prediction(inputs)
    digest = write_once(args.output/"prediction.json", frozen)
    frozen = read_verified(args.output/"prediction.json")
    result = adversarial_results(frozen, digest)
    write_once(args.output/"results.json", result)
    print(json.dumps({"status": "DER", "prediction_sha256": digest,
                      "frequency": frozen["arithmetic"], "minimum_speed_km_s": result["minimum_speed_km_s"],
                      "required_points": result["required_points"]}, indent=2))


if __name__ == "__main__":
    main()
