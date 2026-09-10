"""verification_type: software_test; legal effects depend on supplied facts and sources."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

import pytest

from upi.legal_catalog import StatuteParser
from upi.legal_flow import (
    DocumentFacts,
    LegalFlow,
    classify_document,
    publication_boundary,
    review_routes,
)
from upi.legal_tags import TAGS, provision_tags
from upi.legal_workload import lifecycle, render_html

ROOT = Path(__file__).parents[1]


def base_facts():
    return DocumentFacts(authority=True, document=True, stored=True, received=True,
                         drawn_up=False, exception="none", secrecy="none",
                         provenance=("synthetic assessed facts",))


def test_every_source_paragraph_has_tags_and_honest_history_boundary():
    catalog = json.loads((ROOT / "examples/legal/tf-workload.json").read_text(encoding="utf-8"))
    records = catalog["provisions"]
    assert len(records) == 193
    assert sum(r["lifecycle"]["active"] is True for r in records) == 189
    assert {r["id"] for r in records} == set(provision_tags())
    assert {r["chapter"] for r in records} == set(range(1, 15))
    for record in records:
        assert record["tags"] and set(record["tags"]) <= TAGS
        assert record["text_sha256"] == hashlib.sha256(record["text"].encode()).hexdigest()
        trace = record["root_trace"]
        assert trace["confirmed_tag"] is None
        assert trace["stop_reason"] and trace["next_observation"]
    with ZipFile(ROOT / "examples/legal/source-snapshots.zip") as archive:
        for source in catalog["sources"]:
            raw = archive.read(source["statute"].lower() + ".html")
            assert hashlib.sha256(raw).hexdigest() == source["source_sha256"]


def test_parser_retains_misformatted_heading_inside_a_provision():
    parser = StatuteParser()
    parser.feed('<a class="paragraf" name="K7P16"><b>16 §</b></a> A '
                '<h4>continued clause</h4> with more text.'
                '<h4>Next heading</h4><a class="paragraf" name="K7P17">17 §</a> B')
    parser.flush()
    assert parser.records[0]["text"] == "16 § A continued clause with more text."
    assert "Next heading" not in parser.records[0]["text"]
    assert parser.records[1]["heading"] == "Next heading"


def test_stale_root_reset_is_rejected_and_prior_assessments_survive():
    flow = LegalFlow("example", {"observed": "refusal"})
    root = flow.token
    flow.apply("TF 2:3", {"value": True, "provenance": ["fixture"]}, expected=root)
    with pytest.raises(ValueError, match="stale state"):
        flow.apply("TF 2:4", {"value": True, "provenance": ["fixture"]}, expected=root)
    flow.apply("TF 2:4", {"value": True, "provenance": ["fixture"]}, expected=flow.token)
    assert len(flow.chain.active.state["assessments"]) == 2
    assert flow.chain.anchor.state["assessments"] == {}
    assert flow.chain.validate_all() == []


def test_unknown_is_not_no_and_allman_is_not_fully_public():
    assert classify_document(DocumentFacts())["status"] == "STOP"
    full = classify_document(replace(base_facts(), secrecy="full", secrecy_basis="assessed OSL provision"))
    assert full["allman"] is True
    assert full["outcome"] == "REFUSAL_REVIEW"
    partial = classify_document(replace(base_facts(), secrecy="partial", secrecy_basis="assessed OSL provision"))
    assert partial["outcome"] == "PARTIAL_ACCESS"
    assert classify_document(replace(base_facts(), secrecy="full"))["status"] == "STOP"


def test_digital_compilation_requires_routine_measures_and_legal_authority():
    facts = replace(base_facts(), digital=True, compilation=True, accessible=True,
                    routine_actions=True, personal_data=True, compilation_permitted=False)
    assert classify_document(facts)["outcome"] == "NOT_ALLMAN"
    assert classify_document(replace(facts, compilation_permitted=None))["status"] == "STOP"
    assert classify_document(replace(facts, compilation_permitted=True))["outcome"] == "ACCESS"
    assert classify_document(replace(facts, compilation_permitted=True, routine_actions=False))["outcome"] == "NOT_ALLMAN"


def test_archive_and_substantive_fact_exceptions_are_not_flattened():
    facts = replace(base_facts(), received=False, drawn_up=False, exception="memo",
                    archived=False, dispatched=False, adds_facts=False)
    assert classify_document(facts)["outcome"] == "NOT_ALLMAN"
    assert classify_document(replace(facts, archived=True))["outcome"] == "ACCESS"
    assert classify_document(replace(facts, adds_facts=True))["outcome"] == "PORTION_REVIEW"
    assert classify_document(replace(facts, exception="backup_only"))["outcome"] == "NOT_ALLMAN"


def test_future_and_historical_rules_cannot_be_applied_as_current():
    assert lifecycle("1 § /Träder i kraft I:2027-01-01/ new rule")["active"] is False
    assert lifecycle("7 § Har upphävts genom lag (1976:955).")["tag"] == "REPEALED"
    assert lifecycle("6 § Har betecknats 4 § genom lag (1976:955).")["active"] is False
    assert classify_document(replace(base_facts(), as_of="1766-12-02"))["status"] == "STOP"


@pytest.mark.parametrize(("actor", "remedy"), [
    ("minister", "GOVERNMENT"), ("authority", "ADMINISTRATIVE_APPEAL_COURT"),
    ("government", "NO_ORDINARY_APPEAL"), ("supreme_court", "NO_ORDINARY_APPEAL"),
    ("supreme_administrative_court", "NO_ORDINARY_APPEAL"),
])
def test_review_is_a_set_of_distinct_routes(actor, remedy):
    result = review_routes(actor, issue="disclosure")
    targets = {r["target"] for r in result["routes"]}
    assert remedy in targets
    if actor in {"minister", "government"}:
        assert "KU" in targets and "JO" not in targets
    else:
        assert "JO" in targets


def test_employee_refusal_and_court_jurisdiction():
    routes = review_routes("official", issue="disclosure", decision_level="employee_refusal")["routes"]
    assert {r["target"] for r in routes} == {"JO", "AUTHORITY_DECISION"}
    assert review_routes("district_court", issue="disclosure")["status"] == "STOP"
    routes = review_routes("district_court", issue="disclosure", court_activity="judicial")["routes"]
    assert "APPEAL_COURT" in {r["target"] for r in routes}
    assert review_routes("parliament_agency", issue="disclosure")["status"] == "STOP"


def test_boundary_unknown_and_private_action_do_not_become_public_censorship():
    assert publication_boundary(tf_applies=None, public_actor=True, pre_review=True,
                                content_obstruction=False)["status"] == "STOP"
    result = publication_boundary(tf_applies=True, public_actor=False, pre_review=True,
                                  content_obstruction=False)
    assert result["outcome"] == "OUTSIDE_PUBLIC_PREBLOCK_GATE"


def test_jo_statement_does_not_silently_reverse_refusal():
    flow = LegalFlow("case", {"disclosure": "refused"})
    flow.feedback("JO", "fixture statement", "criticism", expected=flow.token)
    assert flow.chain.active.state["raw_input"]["disclosure"] == "refused"
    assert flow.chain.active.state["corrections"] == []
    flow.verify_correction("fixture statement", "fixture follow-up", "disclosed", "refused",
                           expected=flow.token)
    assert not flow.chain.active.state["corrections"][0]["closed"]
    flow.verify_correction("fixture statement", "second fixture follow-up", "disclosed", "disclosed",
                           expected=flow.token)
    assert len(flow.chain.active.state["corrections"]) == 2
    assert flow.chain.active.state["corrections"][1]["closed"]


def test_html_treats_source_text_as_inert():
    catalog = json.loads((ROOT / "examples/legal/tf-workload.json").read_text(encoding="utf-8"))
    catalog["provisions"][0]["text"] = "<script>alert(1)</script>"
    rendered = render_html(catalog)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
