from upi.taurus import TaurusDelta, TaurusState, advance_taurus

def test_taurus_continues_on_verified_delta():
    report = advance_taurus(TaurusState(generation=3, dna_revision="r3"), verified_delta=TaurusDelta(added=("node:new",)))
    assert report.decision == "CONTINUE"
    assert report.next_state.generation == 4
    assert report.next_state.last_delta.has_verified_change

def test_taurus_preserves_shadow_and_stops_without_frontier():
    report = advance_taurus(TaurusState(generation=3, shadow=("old:branch",)), verified_delta=TaurusDelta(unresolved=("open:question",)))
    assert report.decision == "STOP"
    assert report.next_state.generation == 3
    assert report.next_state.shadow == ("old:branch", "open:question")