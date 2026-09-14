"""verification_type: software_test; conditional mathematics, never resonance evidence."""

import json
import math
from pathlib import Path

import pytest

from upi.dimensions import equation_dimensions_match
from upi.dna import DNAReader, Relation, Value, frequency_relations
from upi.physics import (
    angular_frequency,
    frequency_chamber,
    period_from_frequency,
    phase_from_frequency,
    reduced_rotation,
    spiral_time_from_frequency,
)

ROOT = Path(__file__).resolve().parents[1]
FREQUENCIES = [0.1, 0.5, 1.766, 2, 5, 7, 7.834125, 8]


def inputs(f):
    return {
        "f": Value(f, "Hz"),
        "f_ref": Value(0.1, "Hz"),
        "t_ref": Value(10.8, "Gyr"),
        "t": Value(0.25, "s"),
        "phase0": Value(0.3, "rad"),
    }


@pytest.mark.parametrize("f", FREQUENCIES + [13.12345])
def test_all_frequency_paths_and_inverse(f):
    reader = DNAReader(ROOT / "data", frequency_relations())
    report = reader.derive(inputs(f))
    assert report["state"] == "PASS", report["trace"]
    v = report["values"]
    assert v["T"]["value"] * f == pytest.approx(1, rel=1e-12, abs=0)
    assert v["omega"]["value"] / f == pytest.approx(2 * math.pi, rel=1e-12, abs=0)
    assert v["E"]["value"] / f == pytest.approx(6.62607015e-34, rel=1e-12, abs=0)
    assert v["m_eq"]["value"] / v["E"]["value"] == pytest.approx(1 / 299792458**2, rel=1e-12, abs=0)
    assert v["t_model"]["value"] * f == pytest.approx(1.08, rel=1e-12, abs=0)
    assert v["T"]["unit"] == "s" and v["t_model"]["unit"] == "Gyr"
    assert v["phase"]["value"] == pytest.approx(2 * math.pi * f * 0.25 + 0.3)
    assert len(reader.candidate_nodes(report)) == 6
    assert report["promotion"] == "BLOCKED"
    assert report["open_records"]  # Unsupported DNA stays visible, never implicitly executed.


def test_data_matches_engine_and_reference_distinctions():
    reader = DNAReader(ROOT / "data", frequency_relations())
    report = reader.derive(inputs(1.766))
    record = json.loads(
        (ROOT / "data/information_physics/spiral_flow_tf1766_1_766hz.json").read_bytes()
    )
    names = ["f", "T", "omega", "E", "m_eq", "t_model"]
    for name, q in zip(names, record["quantities"], strict=True):
        assert q["value"] == pytest.approx(report["values"][name]["value"], rel=1e-12, abs=0)
    assert 8 - 7.834125 == pytest.approx(0.165875, abs=1e-14)
    assert 7.834125 != 7.834
    assert spiral_time_from_frequency(0.1) == pytest.approx(10.8)
    assert spiral_time_from_frequency(8) == pytest.approx(0.135)
    assert all(
        spiral_time_from_frequency(a) > spiral_time_from_frequency(b)
        for a, b in zip(FREQUENCIES, FREQUENCIES[1:], strict=False)
    )


@pytest.mark.parametrize("f", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_invalid_frequency_rejected(f):
    for function in [period_from_frequency, angular_frequency, spiral_time_from_frequency]:
        with pytest.raises(ValueError):
            function(f)


def test_units_and_equations():
    assert equation_dimensions_match("h*f/c**2", {"f": "Hz"}, "kg")
    assert not equation_dimensions_match("h*f/c", {"f": "Hz"}, "kg")
    assert not equation_dimensions_match("f+t", {"f": "Hz", "t": "s"}, "s")
    assert not equation_dimensions_match("__import__('os').system('x')", {}, "s")
    q = inputs(1.766)
    q["f"] = Value(1.766, "rad/s")
    report = DNAReader(ROOT / "data", frequency_relations()).derive(q)
    assert report["state"] == "STOP"
    assert "E" not in report["values"]


def test_missing_input_conflict_and_hypothesis_propagation():
    reader = DNAReader(ROOT / "data", frequency_relations())
    report = reader.derive({"f": Value(1.766, "Hz", "HYP")})
    assert report["state"] == "STOP"  # missing model references and phase time
    assert report["values"]["m_eq"]["status"] == "HYP"
    q = inputs(1.766)
    q["T"] = Value(42, "s")
    report = reader.derive(q)
    assert report["state"] == "STOP"
    assert report["values"]["T"] == {"value": 42, "unit": "s", "status": "STOP"}


def test_general_reader_accepts_new_nonfrequency_relation_and_blocks_drift(tmp_path):
    address = "UPI<mechanics,1,test,force>"
    node = {
        "address": address,
        "title": "Force",
        "description": "Test input relation",
        "status": "DER",
        "version": "1.0.0",
        "equations": ["F = m*a"],
        "assumptions": ["Inertial SI model"],
        "primary_sources": ["Newton second law"],
    }
    # Acceleration dimensions are represented by an explicit two-step speed/time input.
    node["equations"] = ["F = m*v/t"]
    path = tmp_path / "force.json"
    path.write_text(json.dumps(node))
    adapter = Relation(
        address,
        "F = m*v/t",
        (("m", "kg"), ("v", "m/s"), ("t", "s")),
        ("F", "N"),
        lambda q: q["m"] * q["v"] / q["t"],
        lambda y, q: y * q["t"] / q["v"],
        "m",
        "Inertial SI model",
    )
    q = {"m": Value(3, "kg"), "v": Value(4, "m/s"), "t": Value(2, "s")}
    report = DNAReader(tmp_path, (adapter,)).derive(q)
    assert report["state"] == "PASS" and report["values"]["F"]["value"] == 6
    node["equations"] = ["F = m*v*t"]
    path.write_text(json.dumps(node))
    assert DNAReader(tmp_path, (adapter,)).derive(q)["state"] == "STOP"


@pytest.mark.parametrize(
    "f,index", [(0.1, 0), (0.5, 1), (1.766, 1), (2, 2), (5, 3), (7, 4), (8, 4)]
)
def test_chamber_boundaries(f, index):
    chamber = frequency_chamber(f)
    assert chamber["index"] == index and chamber["phase_deg"] == index * 72
    assert chamber["status"] == "SYM"


def test_chamber_and_numeric_range_boundaries():
    for f in [0.09, 8.01]:
        with pytest.raises(ValueError):
            frequency_chamber(f)
    with pytest.raises(ValueError):
        period_from_frequency(5e-324)
    with pytest.raises(ValueError):
        phase_from_frequency(1e307, 1e307)


def test_reduced_rotation_derivatives_and_pressure_balance():
    f, x, y, rho = 1.766, 0.2, 0.3, 1000
    field = reduced_rotation(f, x, y, rho)
    epsilon = 1e-6
    dx = (
        reduced_rotation(f, x + epsilon, y, rho)["vy_m_s"]
        - reduced_rotation(f, x - epsilon, y, rho)["vy_m_s"]
    ) / (2 * epsilon)
    dy = (
        reduced_rotation(f, x, y + epsilon, rho)["vx_m_s"]
        - reduced_rotation(f, x, y - epsilon, rho)["vx_m_s"]
    ) / (2 * epsilon)
    assert dx - dy == pytest.approx(field["vorticity_z_s_inverse"])
    gradp = (
        reduced_rotation(f, x + epsilon, y, rho)["pressure_above_axis_pa"]
        - reduced_rotation(f, x - epsilon, y, rho)["pressure_above_axis_pa"]
    ) / (2 * epsilon)
    assert -gradp / rho == pytest.approx(field["ax_m_s2"])
    assert reduced_rotation(f, 0, 0, rho)["pressure_above_axis_pa"] == 0
    assert field["model"] == "REDUCED MODEL"
