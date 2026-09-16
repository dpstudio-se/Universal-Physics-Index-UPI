from upi.tf1766_axis import DEFAULT_AXIS, MirrorOperator, TFAxis, mirror_involution_holds


def test_default_axis_is_ordered_and_current_is_unique() -> None:
    axis = TFAxis(DEFAULT_AXIS)
    assert [node.year for node in axis.nodes] == [1766, 1809, 1949, 1974, 1992, 1994, 2026]
    assert axis.current().status == "EST_CURRENT"
    assert axis.current().label == "CURRENT"


def test_historical_nodes_do_not_become_current() -> None:
    axis = TFAxis(DEFAULT_AXIS)
    assert all(node.status != "EST_CURRENT" for node in axis.nodes[:-1])
    assert axis.nodes[0].status == "HIST"
    assert axis.nodes[1].status == "HIST"
    assert axis.nodes[2].status == "HIST"
    assert axis.nodes[3].status == "HIST"
    assert axis.nodes[4].status == "HIST"
    assert axis.nodes[5].status == "EST_SOURCE"


def test_mirror_index_is_involution() -> None:
    axis = TFAxis(DEFAULT_AXIS)
    assert [axis.mirror_index(i) for i in range(7)] == [6, 5, 4, 3, 2, 1, 0]
    for i in range(7):
        assert axis.mirror_index(axis.mirror_index(i)) == i


def test_mirror_operator_squares_to_identity() -> None:
    axis = TFAxis(DEFAULT_AXIS)
    mirror = MirrorOperator(axis)
    vector = ("1766", "1809", "1949", "1974", "1992", "1994", "2026")
    assert mirror.square(vector) == vector
    assert mirror_involution_holds(axis)


def test_current_law_is_selected_by_status_not_origin_year() -> None:
    axis = TFAxis(DEFAULT_AXIS)
    current = axis.current()
    assert current.year == 2026
    assert current.source_type == "current_consolidated_law"

from upi.tf1766_axis import (
    ANALOG,
    DIGITAL,
    FORWARD,
    OFF,
    REVERSE,
    RNAFuse,
    RNAMotorState,
)


def test_rna_motor_switch_and_direction() -> None:
    state = RNAMotorState(enabled=True, direction=FORWARD, mode=ANALOG)
    assert state.signed_omega == 1
    assert state.step().phase_deg == 72.0
    state = state.switch(direction=REVERSE, mode=DIGITAL)
    assert state.signed_omega == -1
    assert state.mode == DIGITAL
    assert state.step().phase_deg == 0.0


def test_rna_motor_off_freezes_phase() -> None:
    state = RNAMotorState(enabled=False, direction=FORWARD, phase_index=3)
    assert state.signed_omega == 0
    assert state.step().phase_index == 3


def test_rna_fuse_shadow_stops_nonzero_residual() -> None:
    fuse = RNAFuse(MirrorOperator(TFAxis(DEFAULT_AXIS)))
    fuse.set_motor(enabled=True, direction=FORWARD, mode=DIGITAL)
    assert fuse.gate(rsym_zero=False) is False
    assert fuse.shadow_log[-1].reason == "shadow_stop_nonzero_rsym"


def test_rna_fuse_allows_closed_loop_in_both_directions() -> None:
    fuse = RNAFuse(MirrorOperator(TFAxis(DEFAULT_AXIS)))
    fuse.set_motor(enabled=True, direction=FORWARD)
    assert fuse.gate(rsym_zero=True) is True
    fuse.set_motor(enabled=True, direction=REVERSE)
    assert fuse.gate(rsym_zero=True) is True


def test_rna_fuse_off_is_safe_freeze() -> None:
    fuse = RNAFuse(MirrorOperator(TFAxis(DEFAULT_AXIS)))
    fuse.set_motor(enabled=False)
    assert fuse.gate(rsym_zero=False) is True
    assert fuse.shadow_log[-1].reason == "motor_off_freeze"
