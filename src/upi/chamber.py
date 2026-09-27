"""CIP v1: read-only verification against a separately supplied trust anchor.

This module is not an OS sandbox or an independent attestation service. Its caller
must protect the anchor, validator code and callbacks from the candidate writer.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from jsonschema import validators

from .feedback import CheckResult, DomainCheck

PROTOCOL = "upi-cip-v1"


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def serialize(value: Any) -> bytes:
    """CIP Python JSON profile, not RFC 8785 or scientific equivalence.

    Ignores whitespace/key order; preserves array order, types and numeric spelling
    distinctions such as 1 versus 1.0 after parsing. Non-finite numbers are invalid.
    """
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def parse(content: bytes) -> dict[str, Any]:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    value = json.loads(content, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    serialize(value)  # Reject NaN and infinity, including overflowed numeric literals.
    return value


def draft_manifest(
    chamber: str,
    content: bytes,
    schema: bytes,
    invariants: bytes,
    dependencies: Mapping[str, bytes],
    *,
    schema_version: str,
    parent_sha256: str | None = None,
) -> bytes:
    """Prepare an UNTRUSTED proposal; never create/update an approval or trust anchor."""
    node = parse(content)
    return serialize(
        {
            "protocol": PROTOCOL,
            "chamber": chamber,
            "version": node["version"],
            "status": node["status"],
            "schema_version": schema_version,
            "content_sha256": sha256(content),
            "semantic_sha256": sha256(serialize(node)),
            "schema_sha256": sha256(schema),
            "invariant_sha256": sha256(invariants),
            "parent_sha256": parent_sha256,
            "dependencies": {name: sha256(data) for name, data in dependencies.items()},
        }
    )


@dataclass(frozen=True)
class TrustAnchor:
    # Supply from a protected service/configuration, NEVER from the review request.
    chamber: str
    manifest_sha256: str
    schema_version: str
    validator_version: str


@dataclass(frozen=True)
class ChamberReview:
    chamber: str
    manifest_sha256: str
    semantic_sha256: str | None
    validator_version: str
    checks: Mapping[str, CheckResult]

    def as_check(self) -> CheckResult:
        failed = [
            f"{name}: {check.detail}"
            for name, check in self.checks.items()
            if check.outcome != "PASS"
        ]
        return CheckResult(
            "FAIL" if failed else "PASS",
            "; ".join(failed)
            if failed
            else f"CIP manifest {self.manifest_sha256}; validator {self.validator_version}; "
            "integrity/schema/declared domain checks passed; no promotion authorized.",
            "Inspect the named mismatch against the protected anchor; review a repair in a "
            "work chamber. Never refresh expected hashes to silence a mismatch."
            if failed
            else "",
        )

    @property
    def decision_state(self) -> str:
        return "AWAITING_HUMAN_REVIEW" if self.as_check().outcome == "PASS" else "STOP"


def verify_chamber(
    *,
    anchor: TrustAnchor,
    manifest: bytes,
    content: bytes,
    schema: bytes,
    invariants: bytes,
    dependencies: Mapping[str, bytes],
    history: Mapping[str, bytes],
    validator_version: str,
    domain_check: Callable[[dict[str, Any]], CheckResult],
) -> ChamberReview:
    """Verify supplied immutable byte snapshots; no filesystem writes or promotions.

    History is an object store keyed by exact manifest byte hashes. Every predecessor
    is checked to genesis. The protected head prevents rewriting/replacing the chain.
    Domain callback and deployed version are supplied by trusted application code.
    """
    checks: dict[str, CheckResult] = {}
    semantic = None

    def require(name: str, condition: bool, detail: str) -> None:
        checks[name] = CheckResult(
            "PASS" if condition else "FAIL",
            detail,
            "" if condition else "Inspect the protected manifest and input.",
        )

    try:
        require(
            "anchor",
            sha256(manifest) == anchor.manifest_sha256,
            f"Expected {anchor.manifest_sha256}; current {sha256(manifest)}.",
        )
        require(
            "validator",
            validator_version == anchor.validator_version,
            "Deployed validator identity must match the protected policy.",
        )
        record = parse(manifest)
        require(
            "identity",
            record["protocol"] == PROTOCOL
            and record["chamber"] == anchor.chamber
            and record["schema_version"] == anchor.schema_version,
            "Chamber/schema identity.",
        )
        node = parse(content)
        semantic = sha256(serialize(node))
        require(
            "bytes",
            record["content_sha256"] == sha256(content),
            f"Expected {record['content_sha256']}; current {sha256(content)}.",
        )
        require(
            "semantic",
            record["semantic_sha256"] == semantic,
            f"Expected {record['semantic_sha256']}; current {semantic}.",
        )
        require(
            "status_version",
            record["version"] == node["version"]
            and record["status"] == node["status"]
            and node["status"] in {"EST", "DER", "HYP", "STOP", "ERR", "SYM"},
            "Manifest must preserve candidate version and scientific status.",
        )
        require("schema_hash", record["schema_sha256"] == sha256(schema), "Schema byte identity.")
        require(
            "invariant_hash",
            record["invariant_sha256"] == sha256(invariants),
            "Declared invariant specification byte identity.",
        )
        require(
            "dependencies",
            record["dependencies"] == {name: sha256(data) for name, data in dependencies.items()},
            "Exact dependency names and byte hashes; no scientific status inheritance.",
        )
        seen = {sha256(manifest)}
        parent = record["parent_sha256"]
        while parent is not None:
            if not isinstance(parent, str) or parent in seen or parent not in history:
                raise ValueError("Missing or cyclic manifest predecessor")
            seen.add(parent)
            previous = history[parent]
            if sha256(previous) != parent:
                raise ValueError("Altered manifest predecessor")
            prior = parse(previous)
            if prior["chamber"] != anchor.chamber or prior["protocol"] != PROTOCOL:
                raise ValueError("Cross-chamber history")
            parent = prior["parent_sha256"]
        require(
            "history",
            True,
            "Hash chain checked to genesis; acceptance requires protected anchoring.",
        )
        # Never run candidate-selected schemas or callbacks after an integrity failure.
        if all(check.outcome == "PASS" for check in checks.values()):
            schema_node = parse(schema)

            def local_refs(value):
                if isinstance(value, dict):
                    for key, item in value.items():
                        if key in {"$ref", "$dynamicRef", "$recursiveRef"} and (
                            not isinstance(item, str) or not item.startswith("#")
                        ):
                            raise ValueError("External schema reference not allowed")
                        local_refs(item)
                elif isinstance(value, list):
                    for item in value:
                        local_refs(item)

            local_refs(schema_node)
            validator = validators.validator_for(schema_node)
            validator.check_schema(schema_node)
            errors = list(validator(schema_node).iter_errors(node))
            require("schema", not errors, "Candidate schema validation.")
            if not errors:
                result = domain_check(parse(content))
                require(
                    "domain",
                    isinstance(result, CheckResult) and result.outcome == "PASS",
                    result.detail if isinstance(result, CheckResult) else "Invalid domain result.",
                )
    except Exception:
        # Do not expose source data or callback exception text to the review client.
        require(
            "input_or_verifier",
            False,
            "Malformed/missing input, broken history or verifier failure.",
        )
    return ChamberReview(anchor.chamber, sha256(manifest), semantic, validator_version, checks)


def promotion_check(load_review: Callable[[], ChamberReview]) -> DomainCheck:
    """Reload trusted snapshots on every review/review-before-write invocation."""

    def check(node, evidence):
        review = load_review()
        if review.semantic_sha256 != sha256(serialize(node)):
            return CheckResult(
                "FAIL",
                "CIP reviewed content differs from promotion target.",
                "Review the exact target against a protected CIP manifest.",
            )
        return review.as_check()

    return check
