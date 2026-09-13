"""verification_type: software_test; bounded controls, not Millennium proofs."""

import json
from fractions import Fraction
from pathlib import Path

import pytest

from upi.rna_surface import classify_rna_surface

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "node_file,bridge_file",
    [
        ("e8_forced_inverse_stop", "e8_stops_at_forced_inverse"),
        ("compactification_27_11_stop", "frequency_mass_stops_at_27_11"),
        ("omega_golay_scale_stop", "golay_stops_at_omega_scale"),
    ],
)
def test_issue_12_real_triad_routes_without_status_promotion(node_file, bridge_file):
    node = json.loads((ROOT / f"data/open-problems/{node_file}.json").read_bytes())
    bridge = json.loads((ROOT / f"data/bridges/{bridge_file}.json").read_bytes())
    assert node["status"] == "STOP"
    assert classify_rna_surface(node)[0] == "Catalog + STOP desk (auto)"
    assert bridge["relation"] == "STOPS_AT"
    assert bridge["target"] == node["address"]
    assert classify_rna_surface(bridge)[0] == "Graph/Catalog (auto)"


def test_issue_17_symmetry_does_not_localize_to_strip_or_line():
    # P(s)=((s-1/2)^2-9/4) is real and invariant under s -> 1-s,
    # yet roots -1 and 2 are outside the critical strip. It is NOT zeta or xi.
    def polynomial(s):
        return (s - Fraction(1, 2)) ** 2 - Fraction(9, 4)

    for s in [Fraction(-1), Fraction(0), Fraction(1, 3), Fraction(2)]:
        assert polynomial(s) == polynomial(1 - s)
    assert polynomial(Fraction(-1)) == polynomial(Fraction(2)) == 0


def test_issue_8_decimal_arithmetic_does_not_supply_counting_rule():
    assert Fraction(1600, 162) == Fraction(800, 81)
    assert Fraction(786, 162000) == Fraction(131, 27000)
    node = json.loads((ROOT / "data/open-problems/indaleko_160tb_payload_stop.json").read_bytes())
    assert node["status"] == "STOP"


def test_issue_21_exact_local_point_counts_are_not_rank():
    # E: y^2=x^3-x, discriminant 64: these odd primes have good reduction.
    counts = {
        p: 1 + sum((y * y - x * x * x + x) % p == 0 for x in range(p) for y in range(p))
        for p in [3, 5, 7]
    }
    assert counts == {3: 4, 5: 8, 7: 8}
    assert {p: p + 1 - n for p, n in counts.items()} == {3: 0, 5: -2, 7: 0}


def test_published_atlas_case_is_scoped_stop():
    published = json.loads((ROOT / "data/examples/3i_atlas_upi_case.json").read_bytes())
    candidate = json.loads(
        (ROOT / "examples/feedback/candidates/3i_atlas_upi_case.json").read_bytes()
    )
    assert published == candidate
    assert published["status"] == "STOP"
