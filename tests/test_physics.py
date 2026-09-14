import pytest

from upi.physics import (
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    mass_from_frequency,
    normalize_signal,
    spiral_time_from_frequency,
)


def test_eight_hz_reference() -> None:
    assert energy_from_frequency(8.0) == pytest.approx(5.30085612e-33)
    assert mass_from_frequency(8.0) == pytest.approx(5.897997859e-50)
    assert index8_from_frequency(8.0) == pytest.approx(1.0)


def test_round_trip() -> None:
    mass = 9.1093837139e-31
    assert mass_from_frequency(frequency_from_mass(mass)) == pytest.approx(mass)


def test_normalized_match() -> None:
    assert normalize_signal(4 + 2j, 4 + 2j) == 1 + 0j


def test_invalid_reference() -> None:
    with pytest.raises(ZeroDivisionError):
        normalize_signal(1 + 0j, 0 + 0j)


def test_negative_frequency_is_rejected() -> None:
    with pytest.raises(ValueError):
        mass_from_frequency(-1.0)


def test_zero_frequency_follows_current_positive_input_contract() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        mass_from_frequency(0.0)


def test_dimensional_relation_numerically() -> None:
    # h [J s] * f [s^-1] / c^2 [m^2 s^-2] has dimension kg.
    assert mass_from_frequency(1.0) == pytest.approx(6.62607015e-34 / 299792458.0**2)



def test_spiral_flow_tf1766_time_mapping() -> None:
    # Model relation: t(f) = 10.8 Gyr * 0.1 Hz / f.
    assert spiral_time_from_frequency(1.766) == pytest.approx(0.6115515289)


def test_spiral_flow_time_is_not_period() -> None:
    # The model time coordinate and physical period are distinct quantities.
    assert spiral_time_from_frequency(1.766) != pytest.approx(1.0 / 1.766)


def test_spiral_flow_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        spiral_time_from_frequency(0.0)
    with pytest.raises(ValueError):
        spiral_time_from_frequency(1.766, reference_frequency_hz=0.0)
