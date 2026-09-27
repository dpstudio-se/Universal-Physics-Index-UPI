from pathlib import Path

from upi.dimensions import check_quantities, dimension_of
from upi.evidence import weighted_mean
from upi.index import export_graph, hypothesis_registry, load_graph
from upi.merge import build_merge_pack
from upi.quarantine import quarantine_hash, store_rejected
from upi.uncertainty import mass_uncertainty_from_frequency

ROOT = Path(__file__).parents[1]


def test_canonical_graph_loads_bridges() -> None:
    graph = load_graph(ROOT / "data")
    exported = export_graph(graph)
    assert exported["stats"]["node_count"] >= 15
    assert exported["stats"]["bridge_count"] >= 3
    assert graph.validate_graph_consistency() == []
    assert "description" in next(iter(exported["nodes"].values()))


def test_hypothesis_registry_lists_hyp() -> None:
    rows = hypothesis_registry(ROOT / "data")
    assert rows
    assert all(row["address"] for row in rows)
    assert all("/bridges/" not in row["path"] for row in rows)


def test_uncertainty_and_dimensions() -> None:
    result = mass_uncertainty_from_frequency(8.0, 0.1)
    assert result["u_mass_kg"] > 0
    assert dimension_of("Hz") == "T-1"
    assert check_quantities([{"unit": "Hz"}]) == []
    assert check_quantities([{"unit": "blarg"}])


def test_evidence_weights() -> None:
    result = weighted_mean([1.0, 3.0], [1.0, 1.0])
    assert result["estimate"] == 2.0
    assert result["verification_type"] == "software_test"


def test_merge_pack_duplicates_canonical_addresses() -> None:
    pack = build_merge_pack(
        [
            {
                "record_type": "node",
                "payload": {
                    "address": "UPI<symbolic,1,memory,dna_minne_7.834>",
                    "title": "x",
                    "description": "y",
                    "status": "SYM",
                },
            }
        ],
        canonical_root=ROOT / "data",
    )
    assert pack["candidates"][0]["decision"] == "duplicate"
    assert pack["approval_required"] is True


def test_quarantine_is_not_executable(tmp_path: Path) -> None:
    path = store_rejected({"hostile": True}, tmp_path, "invalid batch")
    assert path.exists()
    assert quarantine_hash({"hostile": True}) in path.name
