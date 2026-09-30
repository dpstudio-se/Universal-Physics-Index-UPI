"""Read-only live diagnostics for Swedish time and weather observations.

This module never changes the host clock. NTP is queried without NTS, so its
offsets are diagnostic estimates rather than authenticated time authority.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import struct
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Protocol
from urllib.request import Request, urlopen

NTP_EPOCH_OFFSET = 2_208_988_800
NTP_FRACTION_SCALE = 1 << 32
SMHI_BASE_URL = "https://opendata-download-metobs.smhi.se/api/version/latest"
MAX_SMHI_RESPONSE_BYTES = 8 * 1024 * 1024
WEATHER_MAX_AGE_S = 2 * 60 * 60


@dataclass(frozen=True)
class TimeServer:
    region: str
    location: str
    host: str


@dataclass(frozen=True)
class WeatherTarget:
    region: str
    location: str
    latitude: float
    longitude: float


TIME_SERVERS = (
    TimeServer("north", "Luleå", "lul1.ntp.netnod.se"),
    TimeServer("north", "Luleå", "lul2.ntp.netnod.se"),
    TimeServer("south", "Malmö", "mmo1.ntp.netnod.se"),
    TimeServer("south", "Malmö", "mmo2.ntp.netnod.se"),
)

WEATHER_TARGETS = (
    WeatherTarget("north", "Luleå", 65.5848, 22.1547),
    WeatherTarget("south", "Malmö", 55.6050, 13.0038),
)

WEATHER_PARAMETERS = {
    "air_temperature": 1,
    "wind_direction": 3,
    "wind_speed": 4,
    "relative_humidity": 6,
}


class TimePoller(Protocol):
    def poll(self) -> dict[str, Any]: ...


class WeatherPoller(Protocol):
    def poll(self) -> dict[str, Any]: ...


def _utc_iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def _unix_to_ntp(timestamp: float) -> bytes:
    if not math.isfinite(timestamp):
        raise ValueError("timestamp must be finite")
    seconds = math.floor(timestamp)
    fraction = int((timestamp - seconds) * NTP_FRACTION_SCALE)
    return struct.pack(
        "!II",
        (seconds + NTP_EPOCH_OFFSET) & 0xFFFFFFFF,
        fraction,
    )


def _ntp_to_unix(raw: bytes, reference_unix: float) -> float:
    if len(raw) != 8:
        raise ValueError("NTP timestamp must be exactly 8 bytes")
    seconds, fraction = struct.unpack("!II", raw)
    reference_ntp = reference_unix + NTP_EPOCH_OFFSET
    era = round((reference_ntp - seconds) / NTP_FRACTION_SCALE)
    full_seconds = seconds + era * NTP_FRACTION_SCALE - NTP_EPOCH_OFFSET
    return full_seconds + fraction / NTP_FRACTION_SCALE


def _ntp_request_packet(transmit_timestamp: bytes) -> bytes:
    if len(transmit_timestamp) != 8:
        raise ValueError("transmit timestamp must be exactly 8 bytes")
    packet = bytearray(48)
    packet[0] = 0x23  # LI=0, VN=4, client mode
    packet[40:48] = transmit_timestamp
    return bytes(packet)


def _decode_ntp_response(
    packet: bytes,
    request_transmit: bytes,
    t1_unix: float,
    t4_unix: float,
) -> dict[str, Any]:
    if len(packet) < 48:
        raise ValueError("NTP response shorter than 48 bytes")
    leap = packet[0] >> 6
    version = (packet[0] >> 3) & 0x07
    mode = packet[0] & 0x07
    stratum = packet[1]
    if leap == 3:
        raise ValueError("NTP server reports unsynchronized clock")
    if version not in (3, 4) or mode != 4:
        raise ValueError("NTP response has invalid version or server mode")
    if not 1 <= stratum <= 15:
        raise ValueError(f"NTP server returned invalid stratum {stratum}")
    if packet[24:32] != request_transmit:
        raise ValueError("NTP originate timestamp does not match request")
    if packet[32:40] == bytes(8) or packet[40:48] == bytes(8):
        raise ValueError("NTP server omitted receive or transmit timestamp")

    reference = t4_unix
    t2_unix = _ntp_to_unix(packet[32:40], reference)
    t3_unix = _ntp_to_unix(packet[40:48], reference)
    offset = ((t2_unix - t1_unix) + (t3_unix - t4_unix)) / 2
    delay = (t4_unix - t1_unix) - (t3_unix - t2_unix)
    if not math.isfinite(offset) or not math.isfinite(delay):
        raise ValueError("NTP response produced non-finite offset or delay")
    root_delay_fixed = struct.unpack("!i", packet[4:8])[0]
    root_dispersion_fixed = struct.unpack("!I", packet[8:12])[0]
    return {
        "leap_indicator": leap,
        "stratum": stratum,
        "offset_s": offset,
        "round_trip_delay_s": delay,
        "root_delay_s": root_delay_fixed / (1 << 16),
        "root_dispersion_s": root_dispersion_fixed / (1 << 16),
        "estimated_server_utc": _utc_iso(t4_unix + offset),
        "sampled_at_utc": _utc_iso(t4_unix),
    }


class NtpDiagnosticClient:
    """Query NTP servers for per-server offset estimates without clock changes."""

    def __init__(
        self,
        servers: tuple[TimeServer, ...] = TIME_SERVERS,
        timeout_s: float = 1.5,
    ) -> None:
        if not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("timeout_s must be finite and positive")
        self._servers = servers
        self._timeout_s = timeout_s

    def query(self, server: TimeServer) -> dict[str, Any]:
        addresses = socket.getaddrinfo(
            server.host,
            123,
            type=socket.SOCK_DGRAM,
        )
        last_error: OSError | None = None
        for family, socktype, protocol, _, address in addresses:
            try:
                with socket.socket(family, socktype, protocol) as client:
                    client.settimeout(self._timeout_s)
                    request_time = time.time()
                    request_transmit = _unix_to_ntp(request_time)
                    client.sendto(
                        _ntp_request_packet(request_transmit),
                        address,
                    )
                    response, peer_address = client.recvfrom(512)
                response_time = time.time()
                result = _decode_ntp_response(
                    response,
                    request_transmit,
                    request_time,
                    response_time,
                )
                return {
                    "provider": "Netnod Swedish Distributed Time Service",
                    "region": server.region,
                    "location": server.location,
                    "host": server.host,
                    "resolved_address": peer_address[0],
                    "transport": "NTPv4/UDP, unauthenticated",
                    **result,
                }
            except OSError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise OSError(f"DNS returned no UDP address for {server.host}")

    def poll(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        for server in self._servers:
            try:
                results.append(self.query(server))
            except (OSError, ValueError, OverflowError) as exc:
                errors.append(
                    {
                        "host": server.host,
                        "region": server.region,
                        "error": str(exc),
                    }
                )
        return {"results": results, "errors": errors}


def _fetch_json(url: str, timeout_s: float = 15.0) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "UPI-Swedish-Live-Feed/1.0",
        },
    )
    with urlopen(request, timeout=timeout_s) as response:
        body = response.read(MAX_SMHI_RESPONSE_BYTES + 1)
    if len(body) > MAX_SMHI_RESPONSE_BYTES:
        raise ValueError("SMHI response exceeds configured size limit")
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("SMHI response must be a JSON object")
    return payload


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )
    return radius_km * 2 * math.asin(math.sqrt(min(1.0, value)))


def _latest_value(station: dict[str, Any]) -> dict[str, Any] | None:
    values = station.get("value")
    if not isinstance(values, list):
        return None
    valid: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        try:
            timestamp_ms = int(item["date"])
            value = float(item["value"])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            valid.append(
                {
                    "timestamp_ms": timestamp_ms,
                    "value": value,
                    "quality": str(item.get("quality", "unknown")),
                }
            )
    return max(valid, key=lambda item: item["timestamp_ms"], default=None)


class SmhiObservationClient:
    """Fetch latest hourly national station observations and select nearest stations."""

    def __init__(
        self,
        targets: tuple[WeatherTarget, ...] = WEATHER_TARGETS,
        fetch_json: Callable[[str], dict[str, Any]] = _fetch_json,
        now: Callable[[], float] = time.time,
    ) -> None:
        self._targets = targets
        self._fetch_json = fetch_json
        self._now = now

    def _parameter_observations(self, name: str, parameter_id: int) -> list[dict[str, Any]]:
        url = (
            f"{SMHI_BASE_URL}/parameter/{parameter_id}/station-set/all/"
            "period/latest-hour/data.json"
        )
        payload = self._fetch_json(url)
        stations = payload.get("station")
        if not isinstance(stations, list):
            raise ValueError(f"SMHI parameter {parameter_id} has no station list")
        parameter = payload.get("parameter")
        if not isinstance(parameter, dict):
            raise ValueError(f"SMHI parameter {parameter_id} metadata is missing")
        unit = parameter.get("unit")
        provider_updated_ms = payload.get("updated")
        updated_at = (
            _utc_iso(int(provider_updated_ms) / 1000)
            if provider_updated_ms is not None
            else None
        )
        now = self._now()
        observations: list[dict[str, Any]] = []
        for target in self._targets:
            candidates: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
            for station in stations:
                if not isinstance(station, dict):
                    continue
                try:
                    lat, lon = float(station["latitude"]), float(station["longitude"])
                except (KeyError, TypeError, ValueError):
                    continue
                value = _latest_value(station)
                if value is not None:
                    candidates.append(
                        (_distance_km(target.latitude, target.longitude, lat, lon), station, value)
                    )
            if not candidates:
                observations.append(
                    {
                        "region": target.region,
                        "location": target.location,
                        "measurement": name,
                        "status": "unavailable",
                    }
                )
                continue
            distance_km, station, value = min(candidates, key=lambda item: item[0])
            observed_at = value["timestamp_ms"] / 1000
            age_s = now - observed_at
            if age_s < -300:
                status = "future_timestamp"
            elif age_s > WEATHER_MAX_AGE_S:
                status = "stale"
            else:
                status = "available"
            observations.append(
                {
                    "provider": "SMHI Open Data, Meteorological Observations",
                    "region": target.region,
                    "target_location": target.location,
                    "measurement": name,
                    "value": value["value"],
                    "unit": unit,
                    "status": status,
                    "observed_at_utc": _utc_iso(observed_at),
                    "age_s": age_s,
                    "quality": value["quality"],
                    "station_id": str(station.get("key", "")),
                    "station_name": station.get("name"),
                    "station_owner": station.get("owner"),
                    "latitude": float(station["latitude"]),
                    "longitude": float(station["longitude"]),
                    "distance_from_target_km": distance_km,
                    "provider_updated_at_utc": updated_at,
                    "source_url": url,
                }
            )
        return observations

    def poll(self) -> dict[str, Any]:
        observations: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for name, parameter_id in WEATHER_PARAMETERS.items():
            try:
                observations.extend(self._parameter_observations(name, parameter_id))
            except (OSError, ValueError, OverflowError, TypeError) as exc:
                errors.append(
                    {
                        "measurement": name,
                        "parameter_id": parameter_id,
                        "error": str(exc),
                    }
                )
        return {
            "provider": "SMHI Open Data",
            "sampling_note": "Latest-hour observations; polling does not increase sensor cadence.",
            "observations": observations,
            "errors": errors,
        }


class SwedishLiveFeed:
    """Poll time and weather sources at independent, conservative intervals."""

    def __init__(
        self,
        ntp_client: TimePoller | None = None,
        weather_client: WeatherPoller | None = None,
        time_interval_s: float = 60.0,
        weather_interval_s: float = 300.0,
        monotonic: Callable[[], float] = time.monotonic,
        wall_time: Callable[[], float] = time.time,
    ) -> None:
        if not math.isfinite(time_interval_s) or time_interval_s < 1:
            raise ValueError("time_interval_s must be at least 1 second")
        if not math.isfinite(weather_interval_s) or weather_interval_s < 60:
            raise ValueError("weather_interval_s must be at least 60 seconds")
        self._ntp = ntp_client or NtpDiagnosticClient()
        self._weather = weather_client or SmhiObservationClient()
        self._time_interval_s = time_interval_s
        self._weather_interval_s = weather_interval_s
        self._monotonic = monotonic
        self._wall_time = wall_time
        self._time_due = 0.0
        self._weather_due = 0.0
        self._latest_time: dict[str, Any] | None = None
        self._latest_weather: dict[str, Any] | None = None

    def poll_once(self) -> dict[str, Any]:
        now_mono = self._monotonic()
        if self._latest_time is None or now_mono >= self._time_due:
            self._latest_time = self._ntp.poll()
            self._time_due = now_mono + self._time_interval_s
        if self._latest_weather is None or now_mono >= self._weather_due:
            self._latest_weather = self._weather.poll()
            self._weather_due = now_mono + self._weather_interval_s
        assert self._latest_time is not None
        assert self._latest_weather is not None

        time_success = bool(self._latest_time["results"])
        time_regions = {row["region"] for row in self._latest_time["results"]}
        weather_success = any(
            item.get("status") == "available"
            for item in self._latest_weather["observations"]
        )
        weather_regions = {
            item["region"]
            for item in self._latest_weather["observations"]
            if item.get("status") == "available"
        }
        failures = bool(
            self._latest_time["errors"]
            or self._latest_weather["errors"]
            or any(
                item.get("status") != "available"
                for item in self._latest_weather["observations"]
            )
        )
        status = (
            "LIVE"
            if {"north", "south"} <= time_regions
            and {"north", "south"} <= weather_regions
            and not failures
            else "DEGRADED"
            if time_success or weather_success
            else "UNAVAILABLE"
        )
        return {
            "schema_version": 1,
            "observed_at_utc": _utc_iso(self._wall_time()),
            "status": status,
            "time_source": {
                "owner": "Netnod; Swedish Distributed Time Service, monitored by RISE and financed by PTS",
                "security_note": "Unauthenticated NTP diagnostics only; host clock is never changed.",
                "poll_interval_s": self._time_interval_s,
                **self._latest_time,
            },
            "weather_source": {
                "owner": "SMHI",
                "poll_interval_s": self._weather_interval_s,
                **self._latest_weather,
            },
        }

    def next_poll_delay_s(self) -> float:
        next_due = min(self._time_due, self._weather_due)
        return max(0.1, next_due - self._monotonic())


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Stream read-only Swedish time-server and weather observations as JSON Lines."
    )
    parser.add_argument("--once", action="store_true", help="poll once and exit")
    parser.add_argument("--time-interval", type=float, default=60.0, help="NTP poll interval seconds")
    parser.add_argument(
        "--weather-interval",
        type=float,
        default=300.0,
        help="SMHI poll interval seconds (minimum 60)",
    )
    args = parser.parse_args()
    feed = SwedishLiveFeed(
        time_interval_s=args.time_interval,
        weather_interval_s=args.weather_interval,
    )
    try:
        while True:
            snapshot = feed.poll_once()
            print(json.dumps(snapshot, ensure_ascii=True, allow_nan=False), flush=True)
            if args.once:
                return 2 if snapshot["status"] == "UNAVAILABLE" else 0
            time.sleep(feed.next_poll_delay_s())
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(_main())
