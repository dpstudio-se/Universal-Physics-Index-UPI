import math

import pytest

from upi.spiral_flow import (
    NavierMode,
    dynamic_reference_points,
    frequency_state,
    integrate_phase,
    navier_stokes_residual,
    rigid_vortex_curl,
    rigid_vortex_velocity,
    select_mode,
)


def test_reference_frequencies() -> None:
    state = frequency_state(1.766)
    assert state.period_s == pytest.approx(1.0 / 1.766)
    assert state.angular_frequency_rad_s == pytest.approx(2 * math.pi * 1.766)

    points = {point.label: point for point in dynamic_reference_points()}
    assert points["resonance_7.834125"].period_s == pytest.approx(1 / 7.834125)
    assert points["gen_pulse_0.126s"].frequency_hz == pytest.approx(1 / 0.126)
    assert points["target_8Hz"].period_s == pytest.approx(0.125)


def test_phase_is_integrated_not_recomputed_from_f_times_t() -> None:
    phase = integrate_phase([1.0, 2.0, 3.0], 0.1)
    assert phase == pytest.approx([0.0, 1.2566370614, 3.1415926536])


def test_rigid_vortex_curl() -> None:
    curl = rigid_vortex_curl(1.766)
    assert curl == pytest.approx((0.0, 0.0, 4 * math.pi * 1.766))


def test_rigid_vortex_velocity() -> None:
    vx, vy, vz = rigid_vortex_velocity(1.0, 0.0, 1.766)
    assert vx == pytest.approx(0.0)
    assert vy == pytest.approx(2 * math.pi * 1.766)
    assert vz == pytest.approx(0.0)


def test_navier_stokes_zero_residual_control() -> None:
    residual = navier_stokes_residual(
        (1.0, 2.0, 3.0),
        (2.0, 1.0, 0.0),
        (-3.0, -3.0, 0.0),
        (0.0, 0.0, 0.0),
        density=1.0,
        viscosity=0.0,
        force=(0.0, 0.0, 3.0),
    )
    assert residual == pytest.approx((0.0, 0.0, 0.0))


def test_mode_switch_preserves_cycle() -> None:
    assert select_mode(0) is NavierMode.VELOCITY
    assert select_mode(1) is NavierMode.VORTICITY
    assert select_mode(2) is NavierMode.NAVIER_STOKES_RESIDUAL
    assert select_mode(3) is NavierMode.VELOCITY
