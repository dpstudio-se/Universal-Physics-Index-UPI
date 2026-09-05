import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from upi.resilience import (
    CONTROL_CLOCK_HZ,
    TF1766_ANCHOR_ID,
    RecoveryChain,
    ResilienceController,
    ResilienceMode,
    TemporalMirrorGate,
    TemporalMirrorState,
    VerificationReceipt,
)
from upi.workflow import validate_recovery_chain

T0 = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).parents[1]


def make_chain() -> RecoveryChain:
    chain = RecoveryChain(
        {"role": "recovery-root", "revision": 0},
        recorded_at=T0,
    )
    chain.append({"revision": 1}, recorded_at=T0 + timedelta(seconds=1))
    chain.append({"revision": 2}, recorded_at=T0 + timedelta(seconds=2))
    return chain


def receipt(
    proposal_hash: str,
    verifier_id: str,
    offset_s: float,
    *,
    approved: bool = True,
) -> VerificationReceipt:
    return VerificationReceipt.create(
        proposal_hash=proposal_hash,
        evidence={"verifier": verifier_id, "offset": offset_s},
        verifier_id=verifier_id,
        decided_at=T0 + timedelta(seconds=offset_s),
        approved=approved,
    )


def test_checkpoint_chain_steps_back_to_tf1766_without_deleting_history() -> None:
    chain = make_chain()

    assert chain.anchor.anchor_id == TF1766_ANCHOR_ID
    assert chain.anchor.control_clock_hz == CONTROL_CLOCK_HZ
    assert chain.active.sequence == 2
    assert chain.validate_active_lineage() == []

    activated = chain.rewind_to_anchor()

    assert [checkpoint.sequence for checkpoint in activated] == [1, 0]
    assert chain.at_anchor is True
    assert chain.active.state["role"] == "recovery-root"
    assert chain.validate_active_lineage() == []


def test_checkpoint_ledger_round_trips_after_backtracking() -> None:
    chain = make_chain()
    chain.step_back()

    restored = RecoveryChain.restore(chain.to_dict())

    assert restored.active.checkpoint_hash == chain.active.checkpoint_hash
    assert restored.anchor.checkpoint_hash == chain.anchor.checkpoint_hash
    assert restored.active.state == {"revision": 1}
    assert restored.validate_all() == []
    assert validate_recovery_chain(restored.to_dict()) == []


def test_public_and_packaged_recovery_schemas_are_identical() -> None:
    public = json.loads(
        (ROOT / "schemas" / "recovery-chain.schema.json").read_text(encoding="utf-8")
    )
    packaged = json.loads(
        (ROOT / "src" / "upi" / "schemas" / "recovery-chain.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert public == packaged


def test_temporal_mirror_requires_same_hash_new_verifier_and_later_tick() -> None:
    proposal_hash = "a" * 64
    gate = TemporalMirrorGate(proposal_hash, minimum_interval_s=0.125)

    assert gate.submit(receipt(proposal_hash, "verifier-a", 0.0)) == []
    assert gate.state == TemporalMirrorState.FIRST_RATIFIED
    assert "independent" in gate.submit(
        receipt(proposal_hash, "verifier-a", 0.125)
    )[0]
    assert "temporal" in gate.submit(
        receipt(proposal_hash, "verifier-b", 0.1)
    )[0]
    assert "different" in gate.submit(
        receipt("b" * 64, "verifier-b", 0.125)
    )[0]

    assert gate.submit(receipt(proposal_hash, "verifier-b", 0.125)) == []
    assert gate.verified is True
    assert gate.state == TemporalMirrorState.SECOND_RATIFIED
    audit = gate.to_dict()
    assert audit["first"]["receipt_hash"] != audit["second"]["receipt_hash"]
    assert audit["proposal_hash"] == proposal_hash


def test_trip_throttles_without_rewinding() -> None:
    chain = make_chain()
    controller = ResilienceController(chain)
    active_hash = chain.active.checkpoint_hash

    decision = controller.sample_load(0.80, 0.20)

    assert decision.mode == ResilienceMode.THROTTLED
    assert decision.action == "TRIP_THROTTLE"
    assert decision.accepting_input is False
    assert decision.external_connection_allowed is True
    assert chain.active.checkpoint_hash == active_hash


def test_trull_steps_back_once_per_control_tick_and_mirror_reconnects() -> None:
    chain = make_chain()
    controller = ResilienceController(chain)

    decision = controller.sample_load(0.96, 0.20)
    assert decision.mode == ResilienceMode.BACKTRACKING
    assert decision.accepting_input is False
    assert controller.control_period_s == 0.125

    assert controller.tick().action == "STEP_BACK"
    assert chain.active.sequence == 1
    assert controller.tick().action == "STEP_BACK"
    assert chain.at_anchor is True
    assert controller.tick().action == "HOLD_ANCHOR"

    pending = controller.sample_load(0.20, 0.20)
    assert pending.mode == ResilienceMode.RECOVERY_PENDING
    assert pending.external_connection_allowed is False

    proposal_hash = chain.active.checkpoint_hash
    first = controller.submit_recovery_receipt(
        receipt(proposal_hash, "verifier-a", 0.0)
    )
    assert first.action == "WAIT_SECOND_VERIFICATION"
    assert first.external_connection_allowed is False

    second = controller.submit_recovery_receipt(
        receipt(proposal_hash, "verifier-b", 0.125)
    )
    assert second.action == "RECONNECT"
    assert second.mode == ResilienceMode.RUNNING
    assert second.accepting_input is True
    assert second.external_connection_allowed is True


def test_trap_isolates_both_saturated_lanes_and_keeps_heartbeat_alive() -> None:
    chain = make_chain()
    controller = ResilienceController(chain)

    trapped = controller.sample_load(0.96, 0.97)

    assert trapped.mode == ResilienceMode.ISOLATED
    assert trapped.action == "TRAP_ISOLATE"
    assert trapped.external_connection_allowed is False
    assert chain.at_anchor is True
    heartbeat = controller.tick()
    assert heartbeat.action == "HEARTBEAT_ISOLATED"
    assert heartbeat.control_tick == 1

    still_blocked = controller.sample_load(0.80, 0.20)
    assert still_blocked.mode == ResilienceMode.RECOVERY_PENDING
    assert still_blocked.action == "WAIT_SAFE_LOAD"
    assert still_blocked.external_connection_allowed is False


def test_rejected_recovery_decision_never_reopens_connection() -> None:
    chain = make_chain()
    controller = ResilienceController(chain)
    controller.sample_load(1.0, 1.0)
    controller.sample_load(0.0, 0.0)

    rejected = controller.submit_recovery_receipt(
        receipt(chain.active.checkpoint_hash, "verifier-a", 0.0, approved=False)
    )

    assert rejected.action == "REJECT_RECEIPT"
    assert rejected.external_connection_allowed is False
    assert rejected.mode == ResilienceMode.RECOVERY_PENDING
