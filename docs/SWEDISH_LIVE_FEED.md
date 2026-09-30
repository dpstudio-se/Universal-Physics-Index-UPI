# Swedish live time and weather feed

UPI includes a read-only polling process for two live public data sources:

1. **Swedish time diagnostics:** two Netnod Swedish Distributed Time Service
   endpoints in Luleå (north) and two in Malmö (south).
2. **Weather observations:** hourly SMHI station observations nearest to Luleå
   and Malmö for air temperature, wind direction, wind speed and relative
   humidity.

## Why Netnod, not SUNET-hosted clocks

The national public Swedish time service is operated by Netnod, monitored by
RISE and financed by PTS. SUNET provides the university network; it is not the
operator of the regional public time nodes used by this integration. Current
official server details are listed by [Netnod](https://www.netnod.se/ntp/connect-to-ntp-servers)
and the [Swedish Distributed Time Service](https://www.netnod.se/swedish-distributed-time-service).

Configured endpoints:

- North: `lul1.ntp.netnod.se`, `lul2.ntp.netnod.se`
- South: `mmo1.ntp.netnod.se`, `mmo2.ntp.netnod.se`

The collector queries NTP over UDP/123 using IPv4 or IPv6 and reports each
server's offset estimate and round-trip delay separately. The implementation
does **not** use Network Time Security (NTS), does not authenticate NTP
responses, and never changes the computer's clock. Treat the values as
diagnostic estimates, not secure time synchronization or proof of a physical
frequency/resonance. Do not use this collector as a security or authorization
clock.

## Weather observation data

The collector uses SMHI's public
[Meteorological Observations API](https://opendata-download-metobs.smhi.se/api.json)
and its `station-set/all/period/latest-hour` feeds:

| Measurement | SMHI parameter | Unit |
|---|---:|---|
| Air temperature | 1 | Celsius |
| Wind direction | 3 | degrees |
| Wind speed | 4 | metres per second |
| Relative humidity | 6 | percent |

Each measurement records station ID/name/owner, coordinates, measurement
timestamp, age, quality flag, source URL and provider update time. The nearest
station is selected independently for each measurement and target region; the
measurements can therefore come from different stations. Values older than two
hours are marked `stale`, and significantly future-dated values are marked
`future_timestamp`. Missing samples and provider errors are returned explicitly.

The SMHI endpoint offers hourly/latest-hour observations for these parameters.
Polling it every five minutes does not make the underlying station sensors
sample every five minutes. This is near-real-time polling of published hourly
observations, not direct access to raw sensors. SMHI data reuse must follow the
provider's current terms and attribution requirements.

## Run

Install UPI in the active Python environment, then run once:

```powershell
upi-live-feed --once
```

Run continuously, emitting one JSON snapshot per line:

```powershell
upi-live-feed
```

Defaults are NTP every 60 seconds and SMHI every 300 seconds. SMHI polling
intervals below 60 seconds are rejected; changing the polling interval never
changes the upstream sampling resolution. To retain a local JSON Lines record:

```powershell
upi-live-feed | Tee-Object -FilePath .tmp\swedish-live-feed.jsonl -Append
```

The snapshot has `LIVE`, `DEGRADED` or `UNAVAILABLE` status and retains source
errors and stale values instead of substituting defaults. A live status requires
successful northern and southern time results and available northern and
southern weather observations. No output is written to canonical `data/` and
there is no automatic scientific-status promotion.

## Scope and verification

This is a command-line feed; it does not currently add a public UPI web endpoint,
persist to a database, alert on outages, or control a system clock. Network
availability, outbound DNS/UDP/123, SMHI availability, deployment scheduling
and public hosting have not been established by unit tests. A one-off live
smoke test during implementation reached all four configured Netnod servers
(stratum 1) and returned eight SMHI observations (four parameters for two
regions) without source errors. Those SMHI samples were about 41 minutes old at
collection time, illustrating why the per-observation timestamps and ages must
be read rather than interpreting `LIVE` as sub-minute sensor freshness.

Arithmetic on a server's NTP response is software-derived from that response.
Weather records are provider observations with provenance. Neither source is
evidence for a universal 7.61, 7.834125 or 8 Hz coupling. Compare any proposed
frequency hypothesis against the actual time-stamped observations and suitable
control data.
