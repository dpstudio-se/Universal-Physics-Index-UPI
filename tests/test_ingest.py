import json
from pathlib import Path

from upi.contribute.service import ContributionError, ContributionService
from upi.contribute.store import ContributionStore

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples" / "batches" / "upi-remote-batch.example.json"


def make_service() -> ContributionService:
    return ContributionService(ContributionStore("sqlite:///:memory:"))


def test_example_batch_checks_clean() -> None:
    service = make_service()
    batch = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    report = service.check_batch(batch)
    assert report["ok"] is True
    assert report["verification_type"] == "software_test"
    assert report["inserted"] == 0


def test_example_batch_inserts_then_rejects_duplicate() -> None:
    service = make_service()
    batch = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    first = service.insert_batch(batch)
    assert first["ok"] is True
    assert first["inserted"] == 1
    second = service.insert_batch(batch)
    assert second["ok"] is False
    assert second["rejected"] == 1


def test_public_batch_cannot_insert_est() -> None:
    service = make_service()
    batch = {
        "format": "upi-contribution-batch",
        "version": "0.1.0",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "records": [
            {
                "record_type": "node",
                "payload": {
                    "address": "UPI<physics,1,classical,est_probe>",
                    "title": "Forbidden",
                    "description": "EST from a remote LLM",
                    "status": "EST",
                },
            }
        ],
    }
    report = service.check_batch(batch)
    assert report["ok"] is False
    assert any("EST" in error for error in report["records"][0]["errors"])


def test_submit_record_check_does_not_write() -> None:
    service = make_service()
    payload = {
        "address": "UPI<symbolic,1,memory,check_only>",
        "title": "Check only",
        "description": "Must not persist.",
        "status": "SYM",
        "information_layer": "PUBLIC",
        "verification_type": "software_test",
        "claims_experimental_verification": False,
    }
    assert service.submit_record("node", payload, write=False) is None
    assert service.get_node(payload["address"]) is None
    stored = service.submit_record("node", payload, write=True)
    assert stored is not None
    try:
        service.submit_record("node", payload, write=True)
    except ContributionError as exc:
        assert exc.status_code == 409
    else:
        raise AssertionError("duplicate must conflict")
