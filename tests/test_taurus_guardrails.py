from upi.taurus import (
    TaurusDelta, TaurusMirror, TaurusObservation, TaurusState,
    advance_taurus, rollback_taurus,
)


def test_independent_mirror_and_delta_gate():
    s = TaurusState(dna_revision="r0")
    r = advance_taurus(
        s,
        verified_delta=TaurusDelta(added=("n1",)),
        mirror=TaurusMirror("A", "M", True, 0.01, 0.02),
    )
    assert r.decision == "CONTINUE"
    assert r.next_state.generation == 1


def test_failed_mirror_stops():
    r = advance_taurus(
        TaurusState(),
        verified_delta=TaurusDelta(added=("n1",)),
        mirror=TaurusMirror("A", "M", False, 0.0, 0.1),
    )
    assert r.decision == "STOP"


def test_required_next_observation_is_enforced():
    r = advance_taurus(
        TaurusState(),
        verified_delta=TaurusDelta(added=("n1",)),
        next_observations=(TaurusObservation("measure-x"),),
    )
    assert r.decision == "STOP"


def test_checkpoint_and_rollback_preserve_history():
    r = advance_taurus(
        TaurusState(dna_revision="r0"),
        verified_delta=TaurusDelta(added=("n1",)),
    )
    cp = r.next_state.checkpoints[-1]
    rolled = rollback_taurus(r.next_state, cp)
    assert rolled.status == "ROLLBACK"
    assert "ROLLBACK:" in rolled.history[-1]
