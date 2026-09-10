"""verification_type: software_test; no event or particle discovery assertions."""

import hashlib
import json
import math
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import jsonschema
import pytest

from upi.adversarial_physics import oden_checks, read_verified, sensitivity, write_once
from upi.constants import C, H
from upi.dark_matter_candidate import (
    GEV_KG,
    KEV_J,
    Halo,
    frequency_chain,
    helm_squared,
    inverse_speed,
    mean_inverse_speed,
    rate_coefficient,
    recoil,
    reduced_mass,
    target_mass,
)
from upi.index import bridge_from_json
from upi.validation import validate_record_boundaries

ROOT = Path(__file__).resolve().parents[1]
CHI = float(frequency_chain()["mass_equivalent_kg"])
TARGET = target_mass()


def test_exact_chain_and_independent_rational_inverse():
    r = frequency_chain()
    assert Fraction(r["f_N_Hz"]) == Fraction(7834, 1000)*2**84
    assert Fraction(r["energy_J"]) == Fraction(662607015, 10**42)*Fraction(r["f_N_Hz"])
    assert Fraction(r["mass_exact_rational_kg"])*299792458**2 == Fraction(r["energy_J"])
    assert r["rational_inverse_residual_Hz"] == "0"
    for k in ("existing_api_mass_relative_residual", "existing_api_energy_relative_residual",
              "existing_api_inverse_relative_residual"):
        assert abs(r[k]) < 1e-12
    assert r["status"] == "DER"
    assert r["scope"].endswith("remain HYP")


def test_sensitive_inputs_are_preserved_and_scale_linearly():
    a, b, c = sensitivity()
    assert [r["f0_Hz"] for r in (a,b,c)] == ["7.83", "7.834", "8.0"]
    for r in (a,b,c):
        assert Fraction(r["delta_f84_Hz"]) == Fraction(r["delta_f0_Hz"])*2**84
    assert float(a["mass_equivalent_kg"]) < CHI < float(c["mass_equivalent_kg"])
    assert Fraction(frequency_chain(n=85)["energy_J"]) == 2*Fraction(b["energy_J"])
    assert Fraction(b["energy_J"])/Fraction(frequency_chain(n=7)["energy_J"]) == 2**77


@pytest.mark.parametrize("f,n", [("NaN",84),("Infinity",84),("-1",84),("1",True),("1",84.5)])
def test_invalid_scale_domain(f,n):
    with pytest.raises(ValueError):
        frequency_chain(f,n)


@pytest.mark.parametrize("speed", [0, 220000, 361000, 600000, 776000])
def test_lab_conservation_inverse_and_natural_units(speed):
    r = recoil(CHI,TARGET,speed)
    q = r["q_kg_m_s"]
    target_v = q/TARGET
    final_v = speed-q/CHI
    assert CHI*speed == pytest.approx(CHI*final_v+TARGET*target_v, rel=1e-13, abs=1e-40)
    assert .5*CHI*speed**2 == pytest.approx(.5*CHI*final_v**2+.5*TARGET*target_v**2, rel=1e-13,abs=1e-40)
    assert inverse_speed(r["recoil_keV"]*KEV_J,CHI,TARGET) == pytest.approx(speed, rel=1e-13)
    mu_gev = 1/(1/(CHI/GEV_KG)+1/(TARGET/GEV_KG))
    natural_kev = 2*mu_gev**2/(TARGET/GEV_KG)*(speed/C)**2*1e6
    assert r["recoil_keV"] == pytest.approx(natural_kev, rel=1e-13)


def test_angle_limits_and_nonunique_inverse():
    assert recoil(CHI,TARGET,600000,1)["recoil_keV"] == 0
    assert recoil(CHI,TARGET,600000,0)["recoil_keV"] == pytest.approx(recoil(CHI,TARGET,600000)["recoil_keV"]/2)
    for mass in (CHI/2,CHI,CHI*2):
        v = inverse_speed(248*KEV_J,mass,TARGET)
        assert v < Halo().vesc_m_s+Halo().earth_m_s
        assert recoil(mass,TARGET,v)["recoil_keV"] == pytest.approx(248)
    assert reduced_mass(CHI*1e10,TARGET) == pytest.approx(TARGET, rel=1e-9)
    with pytest.raises(ValueError):
        recoil(CHI,TARGET,.01*C)
    with pytest.raises(ValueError):
        recoil(CHI,TARGET,600000,1.1)


def numeric_eta(vmin, halo, count=16000):
    """Independent quadrature of angular-integrated speed density, not eta formula."""
    v0,ve,esc=halo.v0_m_s,halo.earth_m_s,halo.vesc_m_s
    z=esc/v0
    normalization=math.pi**1.5*v0**3*(math.erf(z)-2*z*math.exp(-z*z)/math.sqrt(math.pi))
    step=(esc+ve-vmin)/count
    total=0.
    for i in range(count):
        v=vmin+(i+.5)*step
        upper=min(1.,(esc**2-v**2-ve**2)/(2*v*ve))
        if upper > -1:
            angular=v0**2/(2*v*ve)*(math.exp(-(v-ve)**2/v0**2)-math.exp(-(v*v+ve*ve+2*v*ve*upper)/v0**2))
            total+=2*math.pi*v*angular/normalization*step
    return total


@pytest.mark.parametrize("vmin", [0, 100000, 312000, 361000, 700000])
def test_halo_eta_against_independent_quadrature(vmin):
    assert mean_inverse_speed(vmin,Halo()) == pytest.approx(numeric_eta(vmin,Halo()), rel=2e-7)


def test_spectrum_units_cutoff_density_and_form_factor():
    halo=Halo()
    a=rate_coefficient(50,CHI,halo)
    b=rate_coefficient(50,CHI,replace(halo,rho_GeV_cm3=.6))
    assert b["rate_per_sigma_A_m2"] == pytest.approx(2*a["rate_per_sigma_A_m2"])
    assert helm_squared(0) == 1
    endpoint=recoil(CHI,TARGET,halo.vesc_m_s+halo.earth_m_s)["recoil_keV"]
    assert rate_coefficient(endpoint+1,CHI)["rate_per_sigma_A_m2"] == 0
    assert mean_inverse_speed(halo.vesc_m_s+halo.earth_m_s,halo) == 0
    assert mean_inverse_speed(halo.vesc_m_s,replace(halo,earth_m_s=0)) == 0
    assert a["cross_section"].endswith("unknown parameter")
    # Integrating dσ/dE for point contact F=1 at fixed speed must return σ.
    speed=220000
    mu=reduced_mass(CHI,TARGET)
    ermax=recoil(CHI,TARGET,speed)["recoil_keV"]*KEV_J
    assert TARGET/(2*mu**2*speed**2)*ermax == pytest.approx(1)


def test_freeze_tamper_and_overwrite_rejected(tmp_path):
    p=tmp_path/'prediction.json'
    write_once(p,{"status":"HYP","sigma":None})
    assert read_verified(p)["status"] == "HYP"
    with pytest.raises(FileExistsError):
        write_once(p,{"status":"EST"})
    p.write_text('{"status":"EST"}',encoding='utf-8')
    with pytest.raises(ValueError,match="hash mismatch"):
        read_verified(p)


def test_existing_oden_engine_receives_derivation_only():
    result=oden_checks({"arithmetic":frequency_chain()})
    assert result["status"] == "DER"
    assert result["verification_type"] == "software_test"
    assert len(result["controls"]) == 2
    assert all(c["status"] == "DER" for c in result["controls"])


def test_existing_anchors_unchanged_and_new_graph_valid():
    inputs=read_verified(ROOT/'examples/adversarial_physics/input-freeze.json')
    for p,digest in inputs["reused_sha256"].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest
    for folder,schema_name in (("open-problems","node"),("bridges","bridge")):
        paths=list((ROOT/'data'/folder).glob('octave_recoil_*.json'))
        assert paths
        for p in paths:
            data=json.loads(p.read_text(encoding='utf-8'))
            schema=json.loads((ROOT/'schemas'/f'{schema_name}.schema.json').read_text())
            jsonschema.validate(data,schema)
            assert data["status"] in ("DER","HYP","STOP","ERR")
            assert validate_record_boundaries(data) == []
            if schema_name == "bridge":
                assert bridge_from_json(data).falsification_conditions == data.get("falsification_conditions", [])


def test_zero_quantum_number_is_not_zero_frequency_and_geometry_not_operator():
    assert Decimal(frequency_chain("0")["mass_equivalent_kg"]) == 0
    omega=2*math.pi*7.834
    e0=.5*(H/(2*math.pi))*omega
    assert e0 > 0
    # Two trajectories on the same unit circle are different evolution operators.
    t=.3
    a=(math.cos(t),math.sin(t))
    b=(math.cos(2*t),math.sin(2*t))
    assert sum(x*x for x in a) == pytest.approx(sum(x*x for x in b))
    assert a != b
    # Same f->E/c² function cannot identify two carriers (e.g. two photon states).
    carriers=[{"id":"left-polarized", "frequency":7.834}, {"id":"right-polarized", "frequency":7.834}]
    assert carriers[0] != carriers[1]
    assert frequency_chain(str(carriers[0]["frequency"])) == frequency_chain(str(carriers[1]["frequency"]))
