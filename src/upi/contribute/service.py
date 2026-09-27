"""Validate public contributions before they enter the live index."""

from __future__ import annotations

import hmac
import json
import secrets
import threading
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from upi.evidence_lens import status_through_lens
from upi.feedback import review_node
from upi.schema_resources import schema_path
from upi.validation import validate_bridge_json, validate_json_schema, validate_node_json

from .promotion import REQUIRED_PROMOTION_CHECKS, PromotionPolicy
from .store import Contribution, ContributionStore, content_hash

DNA_MINNE_ADDRESS = "UPI<symbolic,1,memory,dna_minne_7.834>"

DNA_MINNE_NODE: dict[str, Any] = {
    "address": DNA_MINNE_ADDRESS,
    "title": "DNA-minne 7.834 Hz",
    "description": (
        "Symbolic memory-organization coordinate at 7.834 Hz. "
        "'DNA' is Functional DNA: a collaboration architecture, not biology. "
        "'Minne' is inspectable memory of classified claims. "
        "7.834 Hz is a configurable reference frequency alongside 8.000 and 8.200 Hz."
    ),
    "status": "SYM",
    "quantities": [
        {
            "name": "reference_frequency",
            "value": 7.834,
            "unit": "Hz",
            "reference": "Configurable alternative to 8.000 Hz and 8.200 Hz",
        }
    ],
    "definitions": [
        "dna_minne_7.834 is a named memory slot for symbolic collaboration state",
        "nu_ref = 7.834 Hz in this declared normalization context",
    ],
    "assumptions": [
        "The frequency is a declared coordinate, not a measured rest-mass frequency",
        "Memory here means auditable record state, not neural or genomic memory",
    ],
    "information_layer": "PUBLIC",
    "verification_type": "software_test",
    "claims_experimental_verification": False,
    "confusion_guard": (
        "Not biological DNA, not a medical frequency, not a universal physical constant. "
        "Numerical agreement with 7.834 Hz does not prove physical equivalence."
    ),
    "tags": ["dna_minne", "7.834", "memory", "SYM"],
    "version": "0.1.0",
}

PUBLIC_STATUSES = {"HYP", "STOP", "SYM", "DER", "ERR"}
MAX_BODY_BYTES = 256_000


class ContributionError(ValueError):
    """Rejected contribution."""

    def __init__(self, errors: list[str], status_code: int = 400):
        super().__init__("; ".join(errors))
        self.errors = errors
        self.status_code = status_code


class ContributionService:
    """Validate, persist, and list live index records."""

    def __init__(
        self, store: ContributionStore, *, promotion_policy: PromotionPolicy | None = None
    ):
        self.store = store
        self.promotion_policy = promotion_policy
        self._promotion_lock = threading.Lock()
        self._promotion_reviews: dict[str, dict[str, Any]] = {}

    def seed(self) -> Contribution:
        """Insert dna_minne_7.834 when the live index is empty of that address."""
        existing = self.store.get(DNA_MINNE_ADDRESS)
        if existing is not None:
            return existing
        return self.store.insert("node", DNA_MINNE_NODE)

    def load_repo_records(self, data_root: Path) -> int:
        """Copy valid repo JSON records into the live store if missing."""
        loaded = 0
        if not data_root.exists():
            return loaded
        for path in sorted(data_root.rglob("*.json")):
            if path.name.startswith("invalid_"):
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict) or "address" not in payload:
                continue
            address = str(payload["address"])
            if self.store.get(address) is not None:
                continue
            record_type = "bridge" if {"source", "target", "relation"} <= payload.keys() else "node"
            if record_type != "node":
                continue
            try:
                self.submit(payload, allow_est=True)
                loaded += 1
            except ContributionError:
                continue
        return loaded

    def submit(self, payload: dict[str, Any], *, allow_est: bool = False) -> Contribution:
        """Validate and append a public node contribution."""
        stored = self.submit_record("node", payload, allow_est=allow_est, write=True)
        if stored is None:
            raise ContributionError(["insert returned no record"])
        return stored

    def list_nodes(
        self,
        limit: int = 200,
        *,
        query: str | None = None,
        status: str | None = None,
        evidence_lens: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = [_public_view(item) for item in self.store.list_all(limit=max(limit, 500))]
        for row in rows:
            row["status_view"] = status_through_lens(row["payload"], evidence_lens)
        if status:
            rows = [row for row in rows if row["status"] == status]
        if query:
            needle = query.lower()
            rows = [
                row
                for row in rows
                if needle in row["address"].lower()
                or needle in row["title"].lower()
                or needle in str(row["payload"].get("description", "")).lower()
            ]
        return rows[:limit]

    def get_node(self, address: str) -> dict[str, Any] | None:
        item = self.store.get(address)
        return _public_view(item) if item else None

    def check_batch(self, batch: dict[str, Any], *, allow_est: bool = False) -> dict[str, Any]:
        """Validate a remote LLM batch without writing."""
        return self._run_batch(batch, insert=False, allow_est=allow_est)

    def insert_batch(self, batch: dict[str, Any], *, allow_est: bool = False) -> dict[str, Any]:
        """Validate a remote LLM batch and insert records that pass."""
        return self._run_batch(batch, insert=True, allow_est=allow_est)

    def _run_batch(self, batch: dict[str, Any], *, insert: bool, allow_est: bool) -> dict[str, Any]:
        ok, schema_errors = validate_json_schema(batch, schema_path("contribution-batch"))
        results: list[dict[str, Any]] = []
        inserted = 0
        rejected = 0
        if not ok:
            return {
                "operation": "upi_ingest",
                "mode": "insert" if insert else "check",
                "ok": False,
                "inserted": 0,
                "rejected": 0,
                "errors": schema_errors,
                "records": [],
                "verification_type": "software_test",
                "claims_experimental_verification": False,
            }
        for index, record in enumerate(batch.get("records", [])):
            record_type = record.get("record_type")
            payload = record.get("payload")
            if not isinstance(payload, dict):
                results.append(
                    {"index": index, "ok": False, "errors": ["payload must be an object"]}
                )
                rejected += 1
                continue
            try:
                stored = self.submit_record(record_type, payload, allow_est=allow_est, write=insert)
            except ContributionError as exc:
                results.append(
                    {
                        "index": index,
                        "ok": False,
                        "address": payload.get("address"),
                        "errors": exc.errors,
                    }
                )
                rejected += 1
                continue
            results.append(
                {
                    "index": index,
                    "ok": True,
                    "address": stored.address if stored else payload.get("address"),
                    "inserted": stored is not None,
                    "errors": [],
                }
            )
            if stored is not None:
                inserted += 1
        return {
            "operation": "upi_ingest",
            "mode": "insert" if insert else "check",
            "ok": rejected == 0,
            "inserted": inserted,
            "rejected": rejected,
            "errors": [],
            "records": results,
            "verification_type": "software_test",
            "claims_experimental_verification": False,
        }

    def submit_record(
        self,
        record_type: str,
        payload: dict[str, Any],
        *,
        allow_est: bool = False,
        write: bool = True,
    ) -> Contribution | None:
        """Validate a node or bridge. Write only when *write* is true."""
        if record_type == "node":
            errors = _precheck(payload, allow_est=allow_est)
            if errors:
                raise ContributionError(errors)
            ok, schema_errors = validate_node_json(payload, schema_path("node"))
            if not ok:
                raise ContributionError(schema_errors)
            payload.setdefault("verification_type", "software_test")
            payload.setdefault("claims_experimental_verification", False)
            payload.setdefault("information_layer", "PUBLIC")
            address = str(payload["address"])
        elif record_type == "bridge":
            errors = _precheck(payload, allow_est=allow_est)
            if errors:
                raise ContributionError(errors)
            ok, schema_errors = validate_bridge_json(payload, schema_path("bridge"))
            if not ok:
                raise ContributionError(schema_errors)
            address = f"{payload.get('source')}->{payload.get('target')}:{payload.get('relation')}"
        else:
            raise ContributionError([f"unknown record_type: {record_type}"])
        existing = self.store.get(address)
        if existing is not None:
            raise ContributionError([f"Address already exists: {address}"], status_code=409)
        if not write:
            return None
        if record_type == "node":
            payload = {**payload, "address": address}
        else:
            payload = {**payload, "address": address, "title": payload.get("relation", address)}
        return self.store.insert(record_type, payload)

    def supersede(self, old_address: str, payload: dict[str, Any]) -> Contribution:
        """Insert a replacement and mark the old record superseded."""
        old = self.store.get(old_address)
        if old is None:
            raise ContributionError([f"not found: {old_address}"], status_code=404)
        payload = {**payload, "replaces": old_address}
        stored = self.submit(payload)
        old_payload = {**old.payload, "superseded_by": stored.address, "status": "ERR"}
        self.store.update_payload(old_address, old_payload)
        return stored

    @staticmethod
    def _authorize_review(token: str, expected_token: str) -> None:
        if not expected_token or not hmac.compare_digest(
            token.encode("utf-8"), expected_token.encode("utf-8")
        ):
            raise ContributionError(["review token rejected"], status_code=403)

    def _promotion_target(self, address: str) -> tuple[Contribution, dict[str, Any]]:
        item = self.store.get(address)
        if item is None:
            raise ContributionError([f"not found: {address}"], status_code=404)
        if item.record_type != "node" or item.status == "EST":
            raise ContributionError(
                ["promotion requires a non-EST node candidate"], status_code=409
            )
        payload = {
            **item.payload,
            "status": "EST",
            "source_status": item.payload.get("source_status") or "unknown",
        }
        if not payload.get("evidence") and not payload.get("primary_sources"):
            raise ContributionError(["EST promotion requires evidence or primary_sources"])
        return item, payload

    def _review_promotion(self, payload: dict[str, Any], intent: str) -> dict[str, Any]:
        policy = self.promotion_policy
        if policy is None or not policy.version.strip():
            raise ContributionError(
                [
                    "STOP: promotion policy is unavailable; configure server-owned physics, canonical, "
                    "software_tests and status_promotion checks before requesting review."
                ],
                status_code=409,
            )
        try:
            inputs = policy.prepare(deepcopy(payload))
            report = review_node(
                payload,
                human_intent=intent,
                expected=inputs.expected,
                evidence=inputs.evidence,
                derive_from_evidence=inputs.derive_from_evidence,
                checks=inputs.checks,
                required_checks=REQUIRED_PROMOTION_CHECKS,
                absolute_tolerance=inputs.absolute_tolerance,
            ).as_dict()
        except Exception as exc:
            raise ContributionError(
                [
                    f"STOP: promotion review could not execute ({type(exc).__name__}); repair the policy and rerun."
                ],
                status_code=409,
            ) from None
        return {"policy_version": policy.version, "report": report}

    def prepare_promotion(
        self, address: str, token: str, expected_token: str, *, human_intent: str
    ) -> dict[str, Any]:
        """Execute feedback and return a server-issued, short-lived review receipt."""
        self._authorize_review(token, expected_token)
        if not isinstance(human_intent, str) or not human_intent.strip():
            raise ContributionError(["human_intent is required"])
        with self._promotion_lock:
            item, payload = self._promotion_target(address)
            review = self._review_promotion(payload, human_intent)
            now = time.monotonic()
            self._promotion_reviews = {
                key: value
                for key, value in self._promotion_reviews.items()
                if value["expires"] > now
            }
            review_id = None
            if review["report"]["promotion_gate"] == "AWAITING_HUMAN_REVIEW":
                review_id = secrets.token_urlsafe(32)
                # Bound memory; eviction safely requires a new review.
                if len(self._promotion_reviews) >= 256:
                    self._promotion_reviews.pop(next(iter(self._promotion_reviews)))
                self._promotion_reviews[review_id] = {
                    "address": address,
                    "source_hash": item.content_hash,
                    "review_hash": content_hash(review),
                    "intent": human_intent,
                    "expires": now + 900,
                }
            return {
                **deepcopy(review),
                "review_id": review_id,
                "expires_in_seconds": 900 if review_id else 0,
            }

    def promote(
        self,
        address: str,
        token: str,
        expected_token: str,
        *,
        review_id: str = "",
        human_decision: str = "",
    ) -> Contribution:
        """Require an explicit decision on a server-reviewed, unchanged target."""
        self._authorize_review(token, expected_token)
        with self._promotion_lock:
            item, payload = self._promotion_target(address)
            receipt = self._promotion_reviews.get(review_id)
            if human_decision != "approve" or receipt is None:
                raise ContributionError(
                    [
                        "STOP: request feedback review first, then supply its review_id and human_decision=approve after human review."
                    ],
                    status_code=409,
                )
            if (
                receipt["expires"] <= time.monotonic()
                or receipt["address"] != address
                or receipt["source_hash"] != item.content_hash
            ):
                self._promotion_reviews.pop(review_id, None)
                raise ContributionError(
                    ["STOP: review is expired or candidate changed; request a new review."],
                    status_code=409,
                )
            review = self._review_promotion(payload, receipt["intent"])
            if (
                review["report"]["promotion_gate"] != "AWAITING_HUMAN_REVIEW"
                or content_hash(review) != receipt["review_hash"]
            ):
                self._promotion_reviews.pop(review_id, None)
                raise ContributionError(
                    ["STOP: evidence, policy or checks changed; request a new review."],
                    status_code=409,
                )
            try:
                stored = self.store.promote_reviewed(
                    address,
                    payload,
                    expected_hash=item.content_hash,
                    audit={
                        "review_id": review_id,
                        "human_decision": human_decision,
                        "review_hash": receipt["review_hash"],
                        "policy_version": review["policy_version"],
                        "source_hash": item.content_hash,
                        "target_hash": content_hash(payload),
                        "reviewer": "authenticated_review_token_holder",
                        "verification_type": "software_test",
                    },
                )
            except ValueError:
                raise ContributionError(
                    ["STOP: candidate changed during review; request a new review."],
                    status_code=409,
                ) from None
            self._promotion_reviews.pop(review_id, None)
            return stored


def _precheck(payload: dict[str, Any], *, allow_est: bool) -> list[str]:
    errors: list[str] = []
    encoded = json.dumps(payload).encode("utf-8")
    if len(encoded) > MAX_BODY_BYTES:
        errors.append("Payload exceeds 256 KiB")
    status = payload.get("status")
    if status == "EST" and not allow_est:
        errors.append("Public contributions cannot write EST; use HYP, SYM, DER, STOP, or ERR")
    if status not in PUBLIC_STATUSES | ({"EST"} if allow_est else set()):
        errors.append("status must be HYP, SYM, DER, STOP, ERR, or EST with allow_est")
    return errors


def _public_view(item: Contribution) -> dict[str, Any]:
    return {
        "address": item.address,
        "record_type": item.record_type,
        "status": item.status,
        "title": item.title,
        "created_at": item.created_at,
        "content_hash": item.content_hash,
        "payload": item.payload,
        "verification_type": "software_test",
    }
