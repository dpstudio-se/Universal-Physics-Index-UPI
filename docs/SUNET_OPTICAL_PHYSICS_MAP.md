# SUNET optical-network physics map

## Scope

This bounded pass maps physics explicitly exposed by SUNET's public network
material: photons and optical carriers, guided propagation in fibre,
wavelength/polarization information channels, transceivers, and ALM/OTDR
time-of-flight monitoring. It does not treat every SUNET-connected institution
as part of the SUNET corpus.

## UPI map

| SUNET layer | Physical interpretation | Status | Relation |
|---|---|---:|---|
| Optical fibre and wavelength services | Guided electromagnetic propagation; carrier frequency and wavelength satisfy `c0 = lambda0 f` in vacuum notation | DER | `DERIVED_FROM` Maxwell equations |
| Optical transceiver | Electrical/optical conversion and modulation | DER | Included in optical-transmission node |
| Polarization and wavelength | Degrees of freedom used to encode or multiplex information | DER | Included in optical-transmission node |
| ALM / OTDR | Round-trip optical delay and scattering/reflection localize link events | DER | Optical link `MEASURED_BY` monitoring node |
| Fibre disturbance or break | Operational event inferred from a calibrated trace | DER | Not automatically a diagnosis of physical cause |

## Source observations

- **EST:** SUNET exposes a current public network page and historical technical
  PDFs about photons and optical transceivers. Their retrieved payload hashes
  are recorded in `data/sources/sunet_optical_physics.json`.
- **EST:** SUNET's embedded public page data described ALM as continuous fibre
  measurement and OTDR as an on-site troubleshooting instrument.
- **STOP:** A later direct retrieval of the legacy ALM article failed.
  `stop_reason`: canonical bytes and publication time could not be recaptured.
  Smallest next observation: one successful direct response with a payload hash.

## Attached chamber workflow

The supplied chamber/spring workflow is **SYM**, not a physical model. Its
Planck-to-cosmic chamber names can serve as navigation labels, but the numeric
scales, entropy thresholds and target resonances have no units, measurement
procedure or SUNET source. They are therefore not mapped into the two physical
nodes. In addition, its `verify()` method sets verification to true without
measuring resonance; a green software run would establish control flow only.

## Reproduction and control

1. Retrieve each URL listed in the source manifest.
2. SHA-256 hash the response bytes without storing raw content.
3. Compare the three available hashes and byte counts.
4. Load the UPI graph and confirm both new nodes and both typed bridges exist.
5. Control: remove or change a bridge endpoint; graph consistency must fail.

`verification_type: software_test`. These checks verify repository structure
and captured provenance, not optical experiments or SUNET deployment state.

## Falsification boundary

The corpus map is falsified if the cited documents do not contain the named
optical topics. Quantitative OTDR localization fails when
`distance = v_g delta_t / 2` disagrees with controlled reflector positions
outside declared timing, group-index and calibration uncertainty.
