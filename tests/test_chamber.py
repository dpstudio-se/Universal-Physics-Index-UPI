"""verification_type: software_test; synthetic anchors are not deployed trust roots."""

import json
from dataclasses import replace

import pytest

from upi.chamber import (
    TrustAnchor,
    draft_manifest,
    parse,
    promotion_check,
    serialize,
    sha256,
    verify_chamber,
)
from upi.feedback import CheckResult
from upi.orbital_review import check_signed_periapsis_equation


@pytest.fixture
def chamber():
    content = serialize(
        {
            "version": "1",
            "status": "HYP",
            "equations": ["epsilon=v^2/2-mu/r", "epsilon=-mu/(2a)", "v_p=sqrt(mu(2/q-1/a))"],
        }
    )
    schema = serialize(
        {
            "type": "object",
            "required": ["version", "status", "equations"],
            "properties": {"equations": {"type": "array"}},
        }
    )
    invariants = b"signed-a osculating identity; e>1, q>0; not long-term propagation"
    deps = {"mechanics": b"frozen fixture dependency"}
    manifest = draft_manifest("orbit", content, schema, invariants, deps, schema_version="1")
    return {
        "anchor": TrustAnchor("orbit", sha256(manifest), "1", "fixture-validator-1"),
        "manifest": manifest,
        "content": content,
        "schema": schema,
        "invariants": invariants,
        "dependencies": deps,
        "history": {},
        "validator_version": "fixture-validator-1",
        "domain_check": lambda node: check_signed_periapsis_equation(
            node, eccentricity=6.14, periapsis=1.3565
        ),
    }


def test_valid_chamber_only_awaits_review_and_preserves_hyp(chamber):
    result = verify_chamber(**chamber)
    assert result.decision_state == "AWAITING_HUMAN_REVIEW"
    assert parse(chamber["content"])["status"] == "HYP"
    assert result.as_check().verification_type == "software_test"


@pytest.mark.parametrize("field", ["content", "schema", "invariants", "manifest"])
def test_changed_bytes_block_without_running_domain(chamber, field):
    chamber[field] += b" "
    chamber["domain_check"] = lambda node: pytest.fail("Untrusted input reached callback")
    assert verify_chamber(**chamber).decision_state == "STOP"


def test_format_only_change_has_equal_semantics_but_fails_byte_integrity(chamber):
    chamber["content"] = json.dumps(parse(chamber["content"]), indent=2).encode()
    result = verify_chamber(**chamber)
    assert result.checks["semantic"].outcome == "PASS"
    assert result.checks["bytes"].outcome == "FAIL"


def test_rehashing_bad_content_cannot_replace_protected_anchor(chamber):
    node = parse(chamber["content"])
    node["status"] = "EST"
    chamber["content"] = serialize(node)
    chamber["manifest"] = draft_manifest(
        "orbit",
        chamber["content"],
        chamber["schema"],
        chamber["invariants"],
        chamber["dependencies"],
        schema_version="1",
    )
    assert verify_chamber(**chamber).checks["anchor"].outcome == "FAIL"


def test_even_matching_manifest_cannot_pass_wrong_vis_viva(chamber):
    chamber["content"] = chamber["content"].replace(b"2/q-1/a", b"2/q+1/a")
    chamber["manifest"] = draft_manifest(
        "orbit",
        chamber["content"],
        chamber["schema"],
        chamber["invariants"],
        chamber["dependencies"],
        schema_version="1",
    )
    chamber["anchor"] = replace(chamber["anchor"], manifest_sha256=sha256(chamber["manifest"]))
    result = verify_chamber(**chamber)
    assert result.checks["domain"].outcome == "FAIL"
    assert result.decision_state == "STOP"


@pytest.mark.parametrize("mutation", ["missing", "changed", "extra"])
def test_exact_dependencies_required(chamber, mutation):
    deps = chamber["dependencies"]
    if mutation == "missing":
        deps.clear()
    elif mutation == "changed":
        deps["mechanics"] = b"changed"
    else:
        deps["unknown"] = b"extra"
    assert verify_chamber(**chamber).checks["dependencies"].outcome == "FAIL"


@pytest.mark.parametrize("mutation", ["intact", "missing", "changed", "other_chamber"])
def test_parent_chain_checked_against_protected_head(chamber, mutation):
    parent = chamber["manifest"]
    if mutation == "other_chamber":
        record = parse(parent)
        record["chamber"] = "elsewhere"
        parent = serialize(record)
    parent_hash = sha256(parent)
    chamber["manifest"] = draft_manifest(
        "orbit",
        chamber["content"],
        chamber["schema"],
        chamber["invariants"],
        chamber["dependencies"],
        schema_version="1",
        parent_sha256=parent_hash,
    )
    chamber["anchor"] = replace(chamber["anchor"], manifest_sha256=sha256(chamber["manifest"]))
    chamber["history"] = (
        {}
        if mutation == "missing"
        else {parent_hash: parent + b" " if mutation == "changed" else parent}
    )
    assert verify_chamber(**chamber).decision_state == (
        "AWAITING_HUMAN_REVIEW" if mutation == "intact" else "STOP"
    )


@pytest.mark.parametrize("data", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":1e999}', b"[]"])
def test_ambiguous_or_nonfinite_json_rejected(data):
    with pytest.raises(ValueError):
        parse(data)


@pytest.mark.parametrize("outcome", ["UNKNOWN", "FAIL", "bogus"])
def test_nonpass_domain_blocks(chamber, outcome):
    chamber["domain_check"] = lambda node: CheckResult(outcome, "Domain unresolved", "Observe X")
    assert verify_chamber(**chamber).decision_state == "STOP"


def test_validator_identity_and_exception_fail_closed(chamber):
    chamber["validator_version"] = "different"
    assert verify_chamber(**chamber).decision_state == "STOP"
    chamber["validator_version"] = chamber["anchor"].validator_version

    def broken(node):
        raise RuntimeError("private fixture secret")

    chamber["domain_check"] = broken
    result = verify_chamber(**chamber)
    assert result.decision_state == "STOP"
    assert "private fixture secret" not in result.as_check().detail


def test_promotion_adapter_binds_exact_target_and_reloads(chamber):
    check = promotion_check(lambda: verify_chamber(**chamber))
    node = parse(chamber["content"])
    assert check(node, ()).outcome == "PASS"
    assert check({**node, "status": "EST"}, ()).outcome == "FAIL"
    chamber["dependencies"]["mechanics"] = b"changed after review"
    assert check(node, ()).outcome == "FAIL"


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "object", "required": ["absent"]},
        {"$ref": "https://example.invalid/schema"},
        {"type": "invalid-schema-type"},
    ],
)
def test_schema_gate_cannot_be_replaced_by_matching_hash(chamber, schema):
    chamber["schema"] = serialize(schema)
    chamber["manifest"] = draft_manifest(
        "orbit",
        chamber["content"],
        chamber["schema"],
        chamber["invariants"],
        chamber["dependencies"],
        schema_version="1",
    )
    chamber["anchor"] = replace(chamber["anchor"], manifest_sha256=sha256(chamber["manifest"]))
    chamber["domain_check"] = lambda node: pytest.fail("Invalid schema reached domain callback")
    assert verify_chamber(**chamber).decision_state == "STOP"
