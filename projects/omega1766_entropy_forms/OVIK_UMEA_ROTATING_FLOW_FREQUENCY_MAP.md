# Örnsköldsvik → Högakustenbron → Umeå — Frequency / Antenna / Rotating-Flow Map

Status: DER/HYP research map specification.

## Purpose

This artifact maps the corridor as a multiscale physical network for UPI analysis:
- hydrology and rotating-flow structure;
- geological and geophysical properties;
- structural/mechanical length scales;
- electromagnetic wavelengths and antenna scales;
- distributed SWARM observations;
- synchronized time-series verification.

It is a model specification, not a measured field map and not evidence of a universal 7.834125 Hz carrier.

## Canonical model

For electromagnetic propagation in free space:
lambda = c / f

For a simple quarter-wave antenna:
L_qw = lambda / 4

For an idealized longitudinal mechanical mode:
f_n ~= n v_p / (2 L)

For flow vorticity:
omega_vec = curl(v_vec)

For a rotating component:
v_theta = Omega R

For cross-node verification:
S_ij(f) = X_i(f) X_j*(f)
gamma_ij^2(f) = |S_ij(f)|^2 / (S_ii(f) S_jj(f))

A high coherence value alone does not prove causality; phase, delay, geometry, source discrimination and uncertainty must also be recorded.

## Reference frequencies: 2–9 Hz

| f (Hz) | lambda = c/f |
|---:|---:|
| 2 | 149,896 km |
| 3 | 99,931 km |
| 4 | 74,948 km |
| 5 | 59,958 km |
| 6 | 49,965 km |
| 7 | 42,827 km |
| 7.834125 | 38,268 km |
| 8 | 37,474 km |
| 9 | 33,310 km |

For the 7.834125 Hz / 8 Hz comparison:
Delta_f = 0.165875 Hz
Delta_f / 8 = 2.0734375 %
T_beat = 1 / Delta_f = 6.028636 s

These are mathematical frequency comparisons only.

## Mechanical length scale at 7.834125 Hz

Using:
L = v_p / (2 f)

| v_p | L |
|---:|---:|
| 3,000 m/s | 191 m |
| 4,000 m/s | 255 m |
| 5,000 m/s | 319 m |
| 5,500 m/s | 351 m |
| 6,000 m/s | 383 m |
| 6,500 m/s | 415 m |

This defines a search window of roughly 190–415 m for structures whose simple longitudinal mode could lie near 7.834125 Hz. It is a DER search criterion, not a detected resonance.

## Radio / antenna scales

| System | f | lambda | lambda/4 |
|---|---:|---:|---:|
| NMT 450 | 450 MHz | 66.62 cm | 16.66 cm |
| 900 MHz | 900 MHz | 33.31 cm | 8.33 cm |
| GSM 1800 | 1,800 MHz | 16.66 cm | 4.16 cm |
| UMTS 2100 | 2,100 MHz | 14.28 cm | 3.57 cm |
| Wi-Fi 2.4 GHz | 2,400 MHz | 12.49 cm | 3.12 cm |
| LTE 2600 | 2,600 MHz | 11.53 cm | 2.88 cm |
| 5G 3500 | 3,500 MHz | 8.57 cm | 2.14 cm |
| Wi-Fi 5 GHz | 5,000 MHz | 6.00 cm | 1.50 cm |
| Wi-Fi 6 GHz | 6,000 MHz | 5.00 cm | 1.25 cm |
| 5G mmWave | 26 GHz | 1.153 cm | 2.88 mm |
| WiGig | 60 GHz | 4.997 mm | 1.249 mm |

Real antenna dimensions depend on substrate, dielectric environment, loading, topology and matching, so lambda/4 is only a first-order reference.

## Hydrodynamic layer

The corridor should use:
v(x,y,z,t) = (v_x, v_y, v_z)
omega_vec = curl(v)

with local characteristic scale:
f_vort ~ U / (2 pi R_v)

The earlier Skorped scaling used an illustrative flow estimate of about 4.3 m^3/s and U ~ 0.1–1 m/s. These are not direct local measurements and must remain marked DER/ESTIMATE until replaced by measured discharge and cross-sections.

For an example U = 0.29 m/s:
- R_v = 100 m -> f_vort ~ 4.6e-4 Hz
- R_v = 10 m -> f_vort ~ 4.6e-3 Hz
- R_v = 1 m -> f_vort ~ 4.6e-2 Hz

The Reynolds number for h = 1 m is approximately Re ~ 2.9e5, indicating turbulent flow for that illustrative case.

## Corridor graph

Nodes should include, where data exist:
- Skorped
- Stor-Åbodsjön
- Sidensjö
- Örnsköldsvik
- Bjästa
- Högakustenbron
- Nordmaling
- Umeå
- relevant lakes, tributaries, bridges, masts and geophysical anomalies.

Edges represent documented physical or information coupling:
- river/water flow;
- road/rail infrastructure;
- electrical infrastructure;
- optical-fiber routes;
- radio links;
- geological continuity;
- measured cross-spectral coupling.

Do not infer an edge solely from geographic proximity.

## Geological / geophysical layer

For each geological cell or anomaly, retain:
rho, v_p, v_s, sigma, mu, B, gamma, gravity, elevation

where available.

Material occurrence labels must distinguish indication/prospecting data from proven economic deposits. Graphite, sulfides and Li-Ta-Sn-W indicators are separate attributes, not one combined "frequency material".

## 7.834125 Hz electromagnetic penetration

For a conductor:
delta = sqrt(2 / (omega mu sigma))
omega = 2 pi f

At 7.834125 Hz, omega ~= 49.224 rad/s.

Skin-depth examples are parameter studies only. They must not be interpreted as measured conductivities of a particular Skorped outcrop.

## SWARM verification loop

OBSERVE -> SYNCHRONIZE -> FFT -> CROSS-SPECTRUM -> COHERENCE -> PHASE/DELAY -> COMPARE -> UPDATE

Use a common UTC-traceable time reference such as UTC(SP) where available.

For each node record:
N_i = (x_i,y_i,z_i,t,signal,f,phase,uncertainty,source_class)

Source classes should separate:
- hydrodynamic;
- seismic/mechanical;
- power/rail ELF;
- radio/mobile/Wi-Fi;
- geophysical natural field;
- instrumental/environmental noise.

## Falsification controls

A proposed coupling must survive:
1. independent sensors;
2. synchronized timestamps;
3. source-frequency discrimination;
4. phase and delay consistency;
5. geometry/material compatibility;
6. comparison against null models;
7. uncertainty propagation;
8. repeat measurements.

If these fail, the proposed coupling is rejected or downgraded from HYP.

## UPI status labels

- EST: established equation or measured source fact.
- DER: calculation derived from EST inputs.
- HYP: proposed physical coupling requiring measurement.
- SYM: project notation/visualization.
- ERR: known error or invalid inference.
- STOP: claim blocked because evidence is insufficient.

## Key correction

7.834125 Hz must not be assigned to the bulk rotation of a lake or the whole corridor. For a characteristic lake radius of about 409 m, treating 7.834125 Hz as rigid bulk rotation gives v_theta ~ 20.1 km/s, which is physically incompatible with an ordinary lake flow. The frequency should therefore remain a test frequency for local mechanical, surface-wave, electromagnetic or coupled phenomena until measurements identify a mechanism.

## Data provenance targets

Preferred authoritative inputs:
- SGU: geology, geophysics, mineral resources and geochemical data.
- SMHI: discharge, water level and hydrological time series.
- Lantmäteriet: terrain models, orthophotos and historical geographic material.
- Trafikverket/NVDB: roads, bridges and transport infrastructure.
- PTS: Swedish spectrum allocations and coverage data.
- Teracom: terrestrial broadcast infrastructure where applicable.
- UTC(SP)/traceable timing: synchronization reference.

## Acceptance criterion

No frequency or antenna "match" is promoted to physical resonance unless:
measured signal + reproducible geometry + plausible mechanism + phase/coherence + uncertainty + independent repetition
are all documented.
