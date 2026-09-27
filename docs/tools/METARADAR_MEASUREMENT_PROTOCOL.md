# MetaRadar measurement protocol

MetaRadar is treated as an external BLE observation instrument. This protocol defines how its observations enter UPI without conflating measurement, derivation, or physical interpretation.

## Measurement record

Minimum record:

- observation_id
- timestamp_utc
- instrument_id
- instrument_model
- Android_version
- BLE/scanner implementation version when available
- RSSI
- advertised packet metadata available to the instrument
- manufacturer/service metadata when legitimately observable
- Tx power when available
- estimated distance when available
- scan interval / sampling information
- packet detection status and missing-sample information
- experiment/environment metadata
- raw-data reference or cryptographic hash

Optional geometry metadata:

- known reference distance
- device orientation
- movement state
- environmental obstacles
- nearby radio sources

## Measurement model

Represent an observed quantity as

M = X + epsilon_instrument + epsilon_environment + epsilon_sampling

where X is the latent signal of interest. The error terms must not be silently absorbed into the Ω1766 interpretation.

For RSSI-based distance, preserve the original RSSI and the model/assumptions used for any distance estimate. An estimated distance is a derived quantity, not an independent measurement.

## Sampling and packet loss

Every time-series experiment should record:

- nominal sampling/scan interval;
- actual observation timestamps;
- missed or rejected packets when detectable;
- scan-window duration;
- device advertising interval when known.

Frequency/period claims must account for irregular sampling and possible aliasing. Absence of a packet must not automatically be interpreted as absence of the physical signal.

## Calibration

Where possible, run a known-reference experiment:

1. fixed transmitter;
2. controlled distance(s);
3. fixed orientation;
4. repeated measurements;
5. repeated sessions and, where possible, a second instrument.

Store calibration parameters separately from raw observations.

## Environmental controls

Record relevant confounders such as body proximity, obstacles, device movement/orientation, other nearby BLE sources and major environmental changes. The minimum required metadata depends on the research question.

## Mirror verification

FL-M may compare MetaRadar against an independent phone/scanner or another independent measurement path.

A second measurement is not automatically independent. Shared hardware, software, environment or data processing must be documented.

## Evidence promotion

EST: directly observed instrument data and established BLE/protocol semantics.

DER: calculations performed from recorded observations under declared assumptions.

TEST: preregistered quantitative prediction compared against independent observations.

HYP: Ω1766 interpretation or causal mechanism not independently established.

STOP: missing calibration, insufficient sampling information, unresolved packet loss, confounding, non-independent mirror, or missing mathematical/physical link.

SYM: architectural correspondence only.

A successful inverse reconstruction, recurrence, spectral peak or FL closure is not by itself proof of an Ω1766 physical law.

## Provenance

Keep the chain:

raw observation → normalized record → derived data → analysis → result → evidence classification.

Raw identifiers should be minimized and retained only when necessary and lawful.