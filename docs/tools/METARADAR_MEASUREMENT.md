# MetaRadar measurement tool

## Purpose

MetaRadar is registered in UPI as an external measurement/acquisition tool for real-world BLE radio observations. It is an instrument/data-source entry, not a physical theory and not evidence for Ω1766 by itself.

Source repository: BLE-Research-Group/MetaRadar.

## Measurement capabilities

According to the upstream project documentation, MetaRadar can:

- scan nearby Bluetooth Low Energy (BLE) devices;
- record/analyze BLE advertising traffic and device metadata;
- apply flexible filters;
- inspect available GATT services;
- classify device type from metadata;
- estimate approximate device distance.

The project documentation states that processing is performed locally/offline and that personal data or geolocation are not shared by the application.

## UPI measurement pipeline

MetaRadar observations can enter the UPI evidence pipeline as:

BLE observation → timestamp/sample → signal/device fingerprint → temporal series → recurrence/trajectory analysis → hypothesis test → FL/FL-V verification → evidence record

Potential measured variables include RSSI / received-signal strength, advertising packet metadata, device/service identifiers where legitimately observable, GATT metadata available to the application, estimated distance, time of observation, and repeated observations.

The exact variables exported by a given MetaRadar version must be verified from the implementation before assigning a schema or quantitative interpretation.

## Ω1766 / FL use

MetaRadar may serve as the physical observation layer for testing whether an observed signal series contains reproducible transport, boundary/interaction and response structure:

X_t → transport/observation → boundary or interaction condition → X_(t+1)

This is a test architecture. It does not establish that BLE dynamics are governed by Ω1766.

FL remains the verification loop. FL-M can be used where an independent mirror measurement or reconstruction is available.

## Evidence classification

- EST: BLE measurements and quantities directly supported by the instrument and documented protocol semantics.
- DER: numerical quantities calculated from recorded measurements under declared assumptions.
- TEST: preregistered predictions compared with independent BLE observations.
- HYP: proposed Ω1766 interpretation of a recurring BLE pattern.
- STOP: missing calibration, missing export field, unresolved confounder, insufficient independent data, or an unproved physical identification.
- SYM: architectural mapping between MetaRadar data flow and UPI/Ω1766.

A self-consistent reconstruction or inverse loop is not, by itself, experimental confirmation.

## Privacy and research boundary

Use only observations and device data that are lawful and appropriate to collect. UPI should store the minimum data needed for the research question. Raw identifiers should not be promoted to canonical scientific records unless there is a clear research need and lawful basis.

## Upstream

MetaRadar is maintained separately from UPI. UPI records it as a measurement tool and does not imply endorsement of every implementation detail or release.
