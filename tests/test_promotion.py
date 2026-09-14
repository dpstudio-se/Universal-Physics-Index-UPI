"""verification_type: software_test; synthetic policy is not physical evidence."""

import hashlib
import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from upi.contribute.promotion import REQUIRED_PROMOTION_CHECKS, PromotionInputs, PromotionPolicy
from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionError, ContributionService
from upi.contribute.store import ContributionStore
from upi.feedback import CheckResult, EvidenceArtifact, Quantity

TOKEN = "local-test-token"


@pytest.fixture
def setup():
    state = {"bytes": b"2", "outcome": "PASS", "missing": None}

    def prepare(target):
        assert target["status"] == "EST"  # Review the exact promoted target, not the old DER.
        content = state["bytes"]
        artifact = EvidenceArtifact("fixture:scalar", content, hashlib.sha256(content).hexdigest())
        return PromotionInputs(
            Quantity(2, "1", "synthetic"),
            (artifact,),
            lambda evidence: Quantity(float(evidence[0].content), "1", "synthetic"),
            {
                name: (
                    lambda node, evidence: CheckResult(
                        state["outcome"],
                        "Synthetic policy check.",
                        "" if state["outcome"] == "PASS" else "Inspect synthetic fixture.",
                    )
                )
                for name in REQUIRED_PROMOTION_CHECKS
                if name != state["missing"]
            },
        )

    service = ContributionService(
        ContributionStore("sqlite:///:memory:"),
        promotion_policy=PromotionPolicy("synthetic-v1", prepare),
    )
    item = service.submit(
        {
            "address": "UPI<mathematics,1,test,promotion>",
            "title": "Synthetic scalar",
            "description": "Promotion software control.",
            "status": "DER",
            "evidence": [{"type": "calculation", "source": "fixture:scalar"}],
        }
    )
    yield service, item.address, state
    service.store.close()


def prepare_review(service, address):
    return service.prepare_promotion(address, TOKEN, TOKEN, human_intent="Review this scalar.")


def approve(service, address, review):
    return service.promote(
        address, TOKEN, TOKEN, review_id=review["review_id"], human_decision="approve"
    )


def test_success_requires_review_and_explicit_decision_and_records_audit(setup):
    service, address, _ = setup
    review = prepare_review(service, address)
    assert review["report"]["promotion_gate"] == "AWAITING_HUMAN_REVIEW"
    assert service.store.get(address).status == "DER"
    with pytest.raises(ContributionError):
        service.promote(address, TOKEN, TOKEN, review_id=review["review_id"])
    assert approve(service, address, review).status == "EST"
    events = [event for event in service.store.events_since() if event["kind"] == "promotion"]
    assert len(events) == 1
    assert events[0]["human_decision"] == "approve"
    assert events[0]["target_hash"] == service.store.get(address).content_hash
    assert TOKEN not in json.dumps(events)
    with pytest.raises(ContributionError):
        approve(service, address, review)


@pytest.mark.parametrize("outcome", ["FAIL", "UNKNOWN"])
def test_failed_or_unknown_check_issues_no_receipt(setup, outcome):
    service, address, state = setup
    state["outcome"] = outcome
    review = prepare_review(service, address)
    assert review["review_id"] is None
    assert review["report"]["decision"] == "STOP"
    with pytest.raises(ContributionError):
        service.promote(address, TOKEN, TOKEN, review_id="forged", human_decision="approve")
    assert service.store.get(address).status == "DER"


@pytest.mark.parametrize("name", REQUIRED_PROMOTION_CHECKS)
def test_missing_required_policy_check_blocks(setup, name):
    service, address, state = setup
    state["missing"] = name
    assert prepare_review(service, address)["review_id"] is None


@pytest.mark.parametrize("change", ["payload", "evidence", "policy", "expiry", "failure"])
def test_stale_review_is_rejected(setup, change):
    service, address, state = setup
    review = prepare_review(service, address)
    if change == "payload":
        item = service.store.get(address)
        service.store.update_payload(address, {**item.payload, "title": "Changed"})
    elif change == "evidence":
        state["bytes"] = b"2.0"  # Same number, different evidence bytes must invalidate approval.
    elif change == "policy":
        service.promotion_policy = PromotionPolicy("synthetic-v2", service.promotion_policy.prepare)
    elif change == "expiry":
        service._promotion_reviews[review["review_id"]]["expires"] = 0
    else:
        state["outcome"] = "FAIL"
    with pytest.raises(ContributionError):
        approve(service, address, review)
    assert service.store.get(address).status == "DER"


def test_no_policy_or_crashing_policy_fails_closed(setup):
    service, address, _ = setup
    service.promotion_policy = None
    with pytest.raises(ContributionError, match="policy is unavailable"):
        prepare_review(service, address)

    def broken(target):
        raise RuntimeError("private source")

    service.promotion_policy = PromotionPolicy("broken", broken)
    with pytest.raises(ContributionError) as result:
        prepare_review(service, address)
    assert "private source" not in str(result.value)
    assert service.store.get(address).status == "DER"


def test_atomic_compare_rejects_change_during_review(setup, monkeypatch):
    service, address, _ = setup
    review = prepare_review(service, address)
    original = service.store.promote_reviewed

    def race(address, payload, **kwargs):
        item = service.store.get(address)
        service.store.update_payload(
            address, {**item.payload, "description": "Concurrent revision"}
        )
        return original(address, payload, **kwargs)

    monkeypatch.setattr(service.store, "promote_reviewed", race)
    with pytest.raises(ContributionError, match="changed during review"):
        approve(service, address, review)
    assert service.store.get(address).status == "DER"
    assert not any(event["kind"] == "promotion" for event in service.store.events_since())


def test_http_cannot_skip_review_or_forge_report(setup):
    service, address, _ = setup
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(ContributionApp(service, review_token=TOKEN))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def post(path, payload, token=TOKEN):
        request = Request(
            f"http://127.0.0.1:{server.server_port}{path}",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "X-UPI-Review-Token": token,
            },
        )
        with urlopen(request, timeout=3) as response:
            return json.load(response)

    try:
        with pytest.raises(HTTPError) as unauthorized:
            post("/api/promotion-review", {"address": address, "human_intent": "review"}, "wrong")
        assert unauthorized.value.code == 403
        with pytest.raises(HTTPError) as rejected:
            post(
                "/api/promote",
                {
                    "address": address,
                    "human_decision": "approve",
                    "report": {"promotion_gate": "AWAITING_HUMAN_REVIEW"},
                },
            )
        assert rejected.value.code == 409
        review = post("/api/promotion-review", {"address": address, "human_intent": "review"})
        assert service.store.get(address).status == "DER"
        result = post(
            "/api/promote",
            {"address": address, "review_id": review["review_id"], "human_decision": "approve"},
        )
        assert result["status"] == "EST"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_audit_write_failure_rolls_back_promotion(setup):
    service, address, _ = setup
    review = prepare_review(service, address)
    service.store._execute(
        "CREATE TRIGGER reject_promotion_audit BEFORE INSERT ON events "
        "WHEN NEW.kind = 'promotion' BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END",
        (),
    )
    with pytest.raises(sqlite3.IntegrityError):
        approve(service, address, review)
    assert service.store.get(address).status == "DER"
    assert not any(event["kind"] == "promotion" for event in service.store.events_since())
