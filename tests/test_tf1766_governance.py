from upi.tf1766_governance import TF1766Governance

def test_tf1766_profile_keeps_historical_and_current_law_distinct():
    p = TF1766Governance().policy_record()
    assert p["historical_reference"] == "1766 års tryckfrihetsförordning"
    assert "Tryckfrihetsförordning (1949:105)" in p["current_law_references"]
    assert "Yttrandefrihetsgrundlag (1991:1469)" in p["current_law_references"]

def test_tf1766_profile_requires_traceability_and_preserves_disagreement():
    g = TF1766Governance()
    assert g.preserve_provenance
    assert g.preserve_disagreement
    assert g.prohibit_silent_ai_suppression