from __future__ import annotations

import math
import struct

import pytest

from upi.swedish_live_feed import (
    NTP_EPOCH_OFFSET,
    NTP_FRACTION_SCALE,
    SmhiObservationClient,
    SwedishLiveFeed,
    WeatherTarget,
    _decode_ntp_response,
    _ntp_request_packet,
    _ntp_to_unix,
    _unix_to_ntp,
)


def ntp_timestamp(unix_time: float) -> bytes:
    seconds = math.floor(unix_time) + NTP_EPOCH_OFFSET
    fraction = int((unix_time - math.floor(unix_time)) * NTP_FRACTION_SCALE)
    return struct.pack("!II", seconds & 0xFFFFFFFF, fraction)


def ntp_response(request_transmit: bytes, receive: float, transmit: float) -> bytes:
    packet = bytearray(48)
    packet[0] = 0x24
    packet[1] = 2
    packet[24:32] = request_transmit
    packet[32:40] = ntp_timestamp(receive)
    packet[40:48] = ntp_timestamp(transmit)
    return bytes(packet)


def test_ntp_offset_and_delay_are_derived_from_four_timestamps() -> None:
    t1, t2, t3, t4 = 1_800_000_000.0, 1_800_000_000.1, 1_800_000_000.11, 1_800_000_000.03
    request_transmit = ntp_timestamp(t1)
    result = _decode_ntp_response(
        ntp_response(request_transmit, t2, t3),
        request_transmit,
        t1,
        t4,
    )
    assert result["offset_s"] == pytest.approx(0.09)
    assert result["round_trip_delay_s"] == pytest.approx(0.02)


def test_ntp_rejects_wrong_origin_timestamp_and_unsynchronized_server() -> None:
    request_transmit = ntp_timestamp(1_800_000_000.0)
    wrong_origin = bytearray(ntp_response(request_transmit, 1_800_000_000.1, 1_800_000_000.11))
    wrong_origin[24] ^= 1
    with pytest.raises(ValueError, match="originate timestamp"):
        _decode_ntp_response(bytes(wrong_origin), request_transmit, 1_800_000_000.0, 1_800_000_000.03)

    unsynchronized = bytearray(ntp_response(request_transmit, 1_800_000_000.1, 1_800_000_000.11))
    unsynchronized[0] |= 0xC0
    with pytest.raises(ValueError, match="unsynchronized"):
        _decode_ntp_response(bytes(unsynchronized), request_transmit, 1_800_000_000.0, 1_800_000_000.03)


def test_ntp_timestamp_round_trip_in_current_era() -> None:
    timestamp = 1_800_000_000.25
    assert _ntp_to_unix(_unix_to_ntp(timestamp), timestamp) == pytest.approx(timestamp, abs=1e-7)
    assert len(_ntp_request_packet(_unix_to_ntp(timestamp))) == 48


def test_smhi_selects_nearest_current_station_and_preserves_provenance() -> None:
    now_s = 1_800_000_000.0

    def fetch_json(url: str) -> dict:
        assert "/parameter/1/" in url
        return {
            "updated": int(now_s * 1000),
            "parameter": {"unit": "celsius"},
            "station": [
                {
                    "key": "north-station",
                    "name": "North station",
                    "owner": "SMHI",
                    "latitude": 65.6,
                    "longitude": 22.1,
                    "value": [{"date": int((now_s - 600) * 1000), "value": "4.5", "quality": "G"}],
                },
                {
                    "key": "south-station",
                    "name": "South station",
                    "owner": "SMHI",
                    "latitude": 55.61,
                    "longitude": 13.0,
                    "value": [{"date": int((now_s - 600) * 1000), "value": "12.0", "quality": "G"}],
                },
            ],
        }

    client = SmhiObservationClient(
        targets=(
            WeatherTarget("north", "Luleå", 65.5848, 22.1547),
            WeatherTarget("south", "Malmö", 55.605, 13.0038),
        ),
        fetch_json=fetch_json,
        now=lambda: now_s,
    )
    result = client._parameter_observations("air_temperature", 1)
    assert [row["station_id"] for row in result] == ["north-station", "south-station"]
    assert [row["value"] for row in result] == [4.5, 12.0]
    assert all(row["status"] == "available" for row in result)
    assert all(row["quality"] == "G" for row in result)
    assert all("source_url" in row for row in result)


def test_smhi_marks_old_observations_stale() -> None:
    now_s = 1_800_000_000.0

    def fetch_json(_: str) -> dict:
        return {
            "updated": int(now_s * 1000),
            "parameter": {"unit": "celsius"},
            "station": [
                {
                    "key": "old",
                    "name": "Old station",
                    "latitude": 65.6,
                    "longitude": 22.1,
                    "value": [{"date": int((now_s - 9000) * 1000), "value": "4.5", "quality": "Y"}],
                }
            ],
        }

    client = SmhiObservationClient(
        targets=(WeatherTarget("north", "Luleå", 65.5848, 22.1547),),
        fetch_json=fetch_json,
        now=lambda: now_s,
    )
    assert client._parameter_observations("air_temperature", 1)[0]["status"] == "stale"


def test_live_feed_refreshes_weather_slower_than_ntp() -> None:
    class FakeNtp:
        calls = 0

        def poll(self) -> dict:
            self.calls += 1
            return {
                "results": [{"region": "north"}, {"region": "south"}],
                "errors": [],
            }

    class FakeWeather:
        calls = 0

        def poll(self) -> dict:
            self.calls += 1
            return {
                "observations": [
                    {"region": region, "status": "available"}
                    for region in ("north", "south")
                ],
                "errors": [],
            }

    clock = [0.0]
    ntp, weather = FakeNtp(), FakeWeather()
    feed = SwedishLiveFeed(
        ntp_client=ntp,
        weather_client=weather,
        monotonic=lambda: clock[0],
        wall_time=lambda: 1_800_000_000.0 + clock[0],
    )
    first = feed.poll_once()
    clock[0] = 60.0
    second = feed.poll_once()
    assert first["status"] == second["status"] == "LIVE"
    assert ntp.calls == 2
    assert weather.calls == 1
    assert feed.next_poll_delay_s() == pytest.approx(60.0)
