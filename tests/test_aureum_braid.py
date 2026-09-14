import json
from pathlib import Path

from jsonschema import Draft7Validator

from upi import frequency_from_mass, mass_from_frequency

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aureum_braid_keeps_the_eleven_d_binding_open() -> None:
    node = load("data/open-problems/aureum_braid_chamber_cosmology.json")
    boundary = load("data/bridges/aureum_braid_11d_boundary.json")
    bridge = load("data/bridges/aureum_braid_from_frequency_mass_equivalent.json")

    assert node["status"] == "STOP"
    assert node["claims_experimental_verification"] is False
    assert "M_11 = X_4 x Y_7" in node["equations"]
    assert "eleven visible chambers" in node["confusion_guard"]
    assert any(
        definition.startswith("Energy-mass function equivalence")
        for definition in node["definitions"]
    )
    assert bridge["relation"] == "DERIVED_FROM"
    assert bridge["status"] == "DER"
    assert "m = h f / c^2" in bridge["equations"]
    assert "e = h f" in bridge["equations"]
    assert "e = m c^2" in bridge["equations"]
    assert "e = m c^2 = h f" in bridge["equations"]
    assert "m = e / c^2" in bridge["equations"]
    assert "e = m = h f / c^2" not in bridge["equations"]
    assert "f = m c^2 / h" in bridge["equations"]
    assert bridge["target"] == "UPI<information_physics,1,inertia,frequency_mass_equivalent>"
    assert boundary["relation"] == "STOPS_AT"
    assert boundary["status"] == "STOP"
    assert boundary["target"] == "UPI<theories,1,m_theory,eleven_d_brane>"


def test_teax_return_loop_recovers_frequency() -> None:
    for frequency_hz in (1.0, 8.0, 1.0e20):
        recovered_hz = frequency_from_mass(mass_from_frequency(frequency_hz))
        assert recovered_hz == frequency_hz


def test_aureum_braid_records_validate_against_public_schemas() -> None:
    pairs = (
        ("data/open-problems/aureum_braid_chamber_cosmology.json", "schemas/node.schema.json"),
        ("data/bridges/aureum_braid_11d_boundary.json", "schemas/bridge.schema.json"),
        (
            "data/bridges/aureum_braid_from_frequency_mass_equivalent.json",
            "schemas/bridge.schema.json",
        ),
    )
    for record_path, schema_path in pairs:
        errors = list(Draft7Validator(load(schema_path)).iter_errors(load(record_path)))
        assert errors == []
