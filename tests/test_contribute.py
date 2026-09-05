import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from upi.contribute.server import STREAM_OVERFLOW, ContributionApp, make_handler
from upi.contribute.service import (
    DNA_MINNE_ADDRESS,
    ContributionError,
    ContributionService,
)
from upi.contribute.store import ContributionStore

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    ("configured", "supplied", "evidence", "expected"),
    [
        ("", "", True, 403),
        ("review-test", "", True, 403),
        ("review-test", "wrong", True, 403),
        ("review-test", "review-test", False, 400),
        ("review-test", "review-test", True, 200),
    ],
)
def test_http_promotion_boundary(configured, supplied, evidence, expected) -> None:
    """verification_type: software_test; token possession is not physical evidence."""
    service = make_service()
    seeded = service.seed()
    if evidence:
        service.store.update_payload(
            seeded.address, {**seeded.payload, "primary_sources": ["test fixture"]}
        )
    app = ContributionApp(service, review_token=configured)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        request = Request(
            f"http://{host}:{port}/api/promote",
            data=json.dumps({"address": seeded.address}).encode(),
            headers={"Content-Type": "application/json", "X-UPI-Review-Token": supplied},
        )
        try:
            with urlopen(request, timeout=2) as response:
                observed = response.status
        except HTTPError as error:
            observed = error.code
            error.close()
        assert observed == expected
        assert service.get_node(seeded.address)["status"] == (
            "EST" if expected == 200 else "SYM"
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.store.close()


def test_invalid_content_length_returns_json_error() -> None:
    service = make_service()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(ContributionApp(service)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        request = Request(
            f"http://{host}:{port}/api/nodes",
            data=b"{}",
            headers={"Content-Length": "invalid"},
        )
        with pytest.raises(HTTPError) as rejected:
            urlopen(request, timeout=2)
        with rejected.value as response:
            assert response.code == 400
            assert json.load(response)["errors"] == ["invalid Content-Length"]
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.store.close()


def make_service() -> ContributionService:
    store = ContributionStore("sqlite:///:memory:")
    return ContributionService(store)


def test_seed_inserts_dna_minne() -> None:
    service = make_service()
    seeded = service.seed()
    assert seeded.address == DNA_MINNE_ADDRESS
    assert seeded.status == "SYM"
    assert service.seed().content_hash == seeded.content_hash
    node = service.get_node(DNA_MINNE_ADDRESS)
    assert node is not None
    assert node["payload"]["quantities"][0]["value"] == 7.834
    assert node["payload"]["claims_experimental_verification"] is False


def test_public_est_is_rejected() -> None:
    service = make_service()
    try:
        service.submit(
            {
                "address": "UPI<physics,1,classical,mass>",
                "title": "Mass",
                "description": "Public EST attempt",
                "status": "EST",
            }
        )
    except ContributionError as exc:
        assert any("EST" in error for error in exc.errors)
    else:
        raise AssertionError("EST must be rejected from the public API")


def test_hyp_requires_boundary_fields() -> None:
    service = make_service()
    payload = {
        "address": "UPI<physics,1,test,live_hyp>",
        "title": "Live hypothesis",
        "description": "A public hypothesis submitted through the UI.",
        "status": "HYP",
        "evidence": [{"type": "other", "source": "contributor note"}],
        "primary_sources": ["contributor note"],
        "falsification_conditions": ["A measured mismatch of the declared variable."],
        "information_layer": "PUBLIC",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
    }
    stored = service.submit(payload)
    assert stored.status == "HYP"


def test_duplicate_address_conflicts() -> None:
    service = make_service()
    service.seed()
    try:
        service.submit(service.get_node(DNA_MINNE_ADDRESS)["payload"])  # type: ignore[index]
    except ContributionError as exc:
        assert exc.status_code == 409
    else:
        raise AssertionError("duplicate address must conflict")


def test_full_live_queue_trips_explicit_replay_instead_of_silent_drop() -> None:
    service = make_service()
    app = ContributionApp(service, subscriber_queue_size=1)
    subscriber = app.subscribe()
    try:
        app.publish({"kind": "contribution", "address": "first"})
        app.publish({"kind": "contribution", "address": "second"})

        assert subscriber.overflowed is True
        assert subscriber.events.get_nowait()["kind"] == STREAM_OVERFLOW
        assert subscriber.events.empty()
    finally:
        app.unsubscribe(subscriber)
        service.store.close()


def test_http_get_and_post() -> None:
    service = make_service()
    service.seed()
    app = ContributionApp(service)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base = f"http://{host}:{port}"
    try:
        with urlopen(f"{base}/api/health", timeout=2) as response:
            health = json.load(response)
        assert health["ok"] is True
        with urlopen(f"{base}/", timeout=2) as response:
            html = response.read().decode("utf-8")
        assert "dna_minne_7.834" in html
        payload = {
            "address": "UPI<symbolic,1,memory,ui_probe>",
            "title": "UI probe",
            "description": "Submitted through the HTTP API.",
            "status": "SYM",
            "information_layer": "PUBLIC",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "confusion_guard": "Software test only.",
        }
        request = Request(
            f"{base}/api/nodes",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            created = json.load(response)
        assert created["address"] == payload["address"]
        est = {
            "address": "UPI<physics,1,classical,ui_est>",
            "title": "Forbidden EST",
            "description": "Must fail.",
            "status": "EST",
        }
        bad = Request(
            f"{base}/api/nodes",
            data=json.dumps(est).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(bad, timeout=2)
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("public EST must return 400")
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.store.close()
