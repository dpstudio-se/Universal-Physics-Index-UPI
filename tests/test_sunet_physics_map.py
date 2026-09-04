import json
from pathlib import Path

from upi.graph import UPIGraph
from upi.index import bridge_from_json, node_from_json


ROOT = Path(__file__).parents[1]
OPTICAL = "UPI<infrastructure_physics,1,optical_network,sunet_optical_transmission>"
MONITOR = "UPI<infrastructure_physics,1,optical_measurement,sunet_alm_otdr_monitoring>"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_sunet_nodes_and_typed_relations_load() -> None:
    graph = UPIGraph()
    for path in (
        "data/established/electromagnetism_maxwell.json",
        "data/infrastructure_physics/sunet_optical_transmission.json",
        "data/infrastructure_physics/sunet_alm_otdr_monitoring.json",
    ):
        graph.add_node(node_from_json(read_json(path)))
    for path in (
        "data/bridges/sunet_optics_from_maxwell.json",
        "data/bridges/sunet_optical_link_measured_by_alm.json",
    ):
        graph.add_bridge(bridge_from_json(read_json(path)))

    relations = {
        (str(edge.source), str(edge.target), edge.relation.value)
        for edge in graph.get_all_bridges()
    }
    assert (
        OPTICAL,
        "UPI<ELECTROMAGNETISM,1,FIELD,MAXWELL_EQUATIONS>",
        "DERIVED_FROM",
    ) in relations
    assert (OPTICAL, MONITOR, "MEASURED_BY") in relations
    assert graph.validate_graph_consistency() == []


def test_sunet_source_manifest_is_bounded_and_auditable() -> None:
    manifest = read_json("data/sources/sunet_optical_physics.json")
    assert manifest["scope"]["maximum_records"] == 4
    assert len(manifest["records"]) == 4
    assert manifest["claims_experimental_verification"] is False
    hashed = [record for record in manifest["records"] if record["content_hash"].startswith("sha256:")]
    assert len(hashed) == 3
    stopped = [record for record in manifest["records"] if record["upi_status"] == "STOP"]
    assert len(stopped) == 1
    assert stopped[0]["stop_reason"]
    assert stopped[0]["smallest_next_observation"]
