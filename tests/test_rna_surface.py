from upi.rna_surface import classify_rna_surface


def test_new_domain_node_uses_generic_surfaces():
    record = {
        "address": "UPI<infrastructure_physics,1,optical_network,sunet>",
        "title": "SUNET",
        "description": "Typed",
        "status": "DER",
    }
    assert classify_rna_surface(record)[0] == "Catalog/Graph (auto)"


def test_stop_node_uses_correction_desk():
    record = {
        "address": "UPI<open-problems,1,symbolic,runic>",
        "title": "Runic",
        "description": "Open",
        "status": "STOP",
    }
    assert classify_rna_surface(record)[0] == "Catalog + STOP desk (auto)"


def test_source_manifest_uses_provenance_docs():
    assert (
        classify_rna_surface({"operation": "upi_external_source_map"})[0]
        == "Provenance docs (auto)"
    )


def test_unknown_shape_needs_review():
    assert classify_rna_surface({"status": "DER"})[0] == "needs-surface"


def test_bridge_uses_graph():
    record = {"source": "UPI<a,1,b,c>", "target": "UPI<a,1,b,d>", "relation": "DERIVED_FROM"}
    assert classify_rna_surface(record)[0] == "Graph/Catalog (auto)"
