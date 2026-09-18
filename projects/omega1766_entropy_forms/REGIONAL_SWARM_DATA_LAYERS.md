# Regional SWARM Data Layers — Örnsköldsvik / Högakustenbron / Umeå

Status: EST/DER/HYP layered research specification.

## Goal

Build one geographically indexed, multiscale observation graph for the corridor:

Skorped → Stor-Åbodsjön → Sidensjö → Örnsköldsvik → Bjästa → Högakustenbron → Nordmaling → Umeå

The graph is an analysis framework. Geographic proximity is not treated as physical coupling.

## Layer 00 — Coordinate and time reference

Canonical:
- SWEREF 99 TM for Swedish GIS geometry where appropriate.
- WGS84 latitude/longitude for external interchange.
- UTC-traceable timestamps; use UTC(SP) where available.

Every observation:
id, x, y, z, timestamp, source, uncertainty, quality_flag

## Layer 01 — Terrain

Variables:
- elevation z
- slope
- aspect
- curvature
- drainage direction
- local relief
- terrain roughness

Derived:
grad(z), curvature(z), hydraulic slope

Use Lantmäteriet terrain models and geodata.

## Layer 02 — Water / hydrology

Variables:
- river network
- lakes
- catchments
- discharge Q
- water level H
- velocity U where measured
- precipitation
- snowmelt proxy
- groundwater
- temperature

Derived:
Re = U L / nu
Fr = U / sqrt(g L)
vorticity = curl(v)

SMHI provides measured and modelled discharge; the Stugusjön station in Nätraån is an important anchor with observations extending from 1999 onward.

## Layer 03 — Geological bedrock

Variables:
- lithology
- contacts
- faults/deformation zones
- strike/dip
- rock density
- elastic properties
- seismic velocities vp, vs

Derived mechanical scale:
f_n ~= n vp / (2L)

Keep rock-unit identity separate from inferred resonance.

## Layer 04 — Quaternary geology / sediment

Variables:
- till
- glaciofluvial deposits
- clay/silt/sand
- eskers
- terraces
- ravines
- soil depth
- erodibility

Important because channel geometry and water storage can be controlled by unconsolidated material.

## Layer 05 — Magnetic field

Variables:
- total magnetic field anomaly
- gradients
- lineaments
- magnetic susceptibility where available

Use SGU airborne magnetic products.

Interpretation:
magnetic anomalies can indicate contrasts in rock units and sometimes structural boundaries. They are not automatically electromagnetic transmitters.

## Layer 06 — Gravity

Variables:
- Bouguer/free-air or available SGU gravity products
- local gravity anomaly
- gradients

Use for density contrasts, bedrock structure and regional geometry.

## Layer 07 — Electrical conductivity / resistivity

Variables:
- conductivity sigma
- apparent resistivity rho_a
- depth sensitivity
- phase/amplitude for EM survey products

Relevant targets include:
- water-bearing fracture zones
- graphite horizons
- sulfide-bearing horizons
- conductive soils/clay

Do not convert conductivity directly into a "frequency" without a defined physical model.

## Layer 08 — Natural radioactivity

Variables:
- K-40
- U-238
- Th-232
- gamma dose-related products where available

Use as geological/material indicators. Radioactivity is a separate layer from RF frequency.

## Layer 09 — Mineral resources / geochemistry

Variables:
- mineral occurrence
- exploration permit
- mineral indicator
- geochemical concentration
- drill core
- sample location

Keep:
indication != deposit != economic ore

Potential Skorped attributes from source data should remain separate, e.g. graphite, sulfides, Cu/Zn, Li-Ta-Sn-W indicators.

## Layer 10 — Water / geology coupling

Candidate relations:
- fracture zone ↔ groundwater
- sediment thickness ↔ channel position
- slope ↔ flow acceleration
- conductivity ↔ water/graphite/sulfide contrasts
- erosion ↔ channel migration

Derived residual:
r_geo_hydro = observed_channel - predicted_channel

This is a testable coupling layer, not an assumed causal chain.

## Layer 11 — Roads, rail and bridges

Variables:
- road geometry
- road class
- bridge/tunnel
- rail geometry
- grade
- curvature
- traffic/load metadata where available

Use Trafikverket NVDB.

For a structure:
f_n ~= n v / (2L)
but use measured structural properties or engineering documentation before assigning a resonance.

Historical road evolution:
compare current NVDB/Lantmäteriet geometry with historical orthophotos.

## Layer 12 — Radio / antenna infrastructure

Separate systems:
- NMT/450-class
- 700/800/900 MHz
- GSM/1800-class
- 2100 MHz
- LTE/2600
- 5G/3500
- 5G/mmWave where documented
- FM/DAB/TV
- Wi-Fi only where local measurement exists

For free-space wavelength:
lambda = c/f

Reference antenna scale:
L_qw ~= lambda/4

Do not infer antenna phase or transmitted power when metadata are unavailable.

## Layer 13 — Fiber / optical communications

Fiber is an optical waveguide, not an RF antenna.

Record:
- route geometry where legitimately available
- network node
- wavelength/channel where documented
- optical equipment
- timestamp/telemetry if available

Do not treat fiber as a 450 MHz / Wi-Fi conductor.

## Layer 14 — Electrical grid

Record only verified infrastructure:
- voltage level
- line/cable geometry
- substation
- transformer
- switching station
- power frequency

Sweden's grid is fundamentally 50 Hz AC, but harmonics and transient spectra may be present.

Power/rail sources must be treated as possible ELF interference sources when interpreting low-frequency magnetic measurements.

## Layer 15 — Seismic / vibration

Variables:
- seismic stations
- accelerometers
- bridge vibration sensors
- structural vibration
- traffic-induced vibration
- frequency spectra

For each sensor:
x(t), PSD(f), phase(f), coherence(f)

Distinguish ambient vibration from driven vibration.

## Layer 16 — Meteorology

Variables:
- wind speed/direction
- pressure
- precipitation
- temperature
- humidity
- snow/ice

Meteorology is essential for separating environmental forcing from intrinsic oscillation.

## Layer 17 — Coastal / marine

Variables:
- coastline
- bathymetry
- sea level
- waves
- currents
- salinity/temperature where available

For the Högakustenbron–Bottenhavet segment, distinguish freshwater river flow from marine circulation.

## Layer 18 — Historical landscape

Variables:
- historical orthophoto year
- road geometry by year
- shoreline position
- land-use change
- forest/agriculture
- settlement
- historical place names

Lantmäteriet GeoLex is the primary discovery tool for historical aerial imagery and orthophotos.

For 1960 and 1975 historical orthophotos, record that source products can contain imagery from more than one flight year; preserve metadata and uncertainty.

## Layer 19 — Cultural heritage

Variables:
- Fornsök ID
- type
- geometry
- dating
- protection status
- documentation quality

Examples in the regional study include hällmålningar and other recorded cultural sites.

Cultural sites are observations of human history, not evidence of physical antennas or resonators.

## Layer 20 — Frequency reference layers

### Low-frequency reference

For free-space EM:
lambda = c/f

2 Hz → 149,896 km
3 Hz → 99,931 km
4 Hz → 74,948 km
5 Hz → 59,958 km
6 Hz → 49,965 km
7 Hz → 42,827 km
7.834125 Hz → 38,268 km
8 Hz → 37,474 km
9 Hz → 33,310 km

### Radio reference

450 MHz → 66.62 cm
900 MHz → 33.31 cm
1800 MHz → 16.66 cm
2100 MHz → 14.28 cm
2400 MHz → 12.49 cm
2600 MHz → 11.53 cm
3500 MHz → 8.57 cm
5 GHz → 6.00 cm
6 GHz → 5.00 cm
26 GHz → 1.153 cm
60 GHz → 4.997 mm

These are free-space reference wavelengths.

## Layer 21 — SWARM graph

G = (V,E)

Node classes:
- hydrology
- geology
- geophysics
- infrastructure
- radio
- vibration
- cultural heritage
- environmental sensor
- time reference

Edge classes:
- water flow
- geological continuity
- infrastructure connection
- radio link
- optical link
- measured coherence
- documented causal/engineering relation

Every edge gets:
edge_type, evidence_level, uncertainty, source

## Layer 22 — ECHO / time-domain analysis

For two observables:
C_xy(tau)

Dominant delay:
tau* = argmax C_xy(tau)

For periodic signals:
phi_ij(f) = arg S_ij(f)

Approximate delay:
tau = phi / (2 pi f)

Only use phase-derived delay where phase unwrapping and source conditions make it valid.

## Layer 23 — Spectral / coherence analysis

For each node:
- PSD
- FFT
- STFT
- cross-spectrum
- coherence
- phase
- delay
- confidence interval

Coherence:
gamma_ij^2(f) = |S_ij(f)|^2 / (S_ii(f) S_jj(f))

A spectral peak without spatial/temporal replication is not enough to establish a regional phenomenon.

## Layer 24 — Null models

Mandatory comparisons:
1. shuffled timestamps
2. phase-randomized surrogate
3. spatially displaced nodes
4. independent frequency bands
5. seasonal subsets
6. weather-conditioned subsets
7. traffic/power source windows
8. instrument-noise baselines

A coupling claim must outperform appropriate null models.

## Layer 25 — Source discrimination

Before interpreting any peak:
- check power-grid frequency/harmonics;
- railway traction frequencies where relevant;
- radio transmitters;
- local machinery;
- traffic/bridge vibration;
- seismic events;
- wind/water forcing;
- sensor electronics.

This prevents a local anthropogenic signal from being mislabeled as a natural regional resonance.

## Layer 26 — 7.834125 Hz test layer

Status: HYP.

Test:
f_test = 7.834125 Hz

Do not assign this frequency to:
- bulk lake rotation;
- the entire Skorped landscape;
- the whole Örnsköldsvik–Umeå corridor;
- a geological material merely because it is conductive or magnetic.

Allowed tests:
- local mechanical resonance;
- surface-wave response;
- ELF magnetic/electric response;
- coupled structural response;
- reproducible cross-node coherence.

Acceptance requires:
measured signal + plausible mechanism + geometry + synchronized timing + phase/coherence + uncertainty + independent repetition.

## Layer 27 — Historical drift / evolution

For each year t:
G(t) = {roads, shoreline, channels, vegetation, buildings, cultural markers}

Register all datasets to stable control points.

Drift:
Delta r(t) = r_feature(t) - r_reference(t)

Separate:
- real physical change;
- mapping/georeferencing error;
- imagery mosaic differences;
- marker/POI relocation.

This layer is the correct place to test whether a Google Maps marker follows a physical object or is merely a cartographic point.

## Layer 28 — Provenance and confidence

Every value receives:
source_id, acquisition_date, processing_level, uncertainty, status

Status:
- EST
- DER
- HYP
- SYM
- ERR
- STOP

No inferred physical relationship may be promoted to EST.

## Primary source targets

SGU:
geology, geophysics, mineral resources, geochemistry, groundwater, historical shorelines, soil depth and petrophysics.

SMHI:
discharge, water level, hydrology and meteorology.

Lantmäteriet:
terrain, orthophotos, historical aerial imagery and geographic reference data.

Trafikverket/NVDB:
roads, bridges, tunnels and transport infrastructure.

PTS:
frequency allocation and communications-spectrum information.

RAÄ/Fornsök:
registered cultural heritage.

## UPI processing order

INGEST → GEOREGISTER → CLASSIFY → NORMALIZE → DERIVE → CROSS-CORRELATE → NULL-TEST → SCORE EVIDENCE → VISUALIZE → ARCHIVE

The evidence score must not be a political or subjective "truth score"; it is a technical provenance/quality field with documented inputs and uncertainty.

## Deliverable

The regional map should ultimately expose these layers independently and as controlled combinations:

1. terrain
2. water
3. geology
4. sediment
5. magnetics
6. gravity
7. conductivity/resistivity
8. radioactivity
9. minerals/geochemistry
10. hydrology-geology coupling
11. roads/rail/bridges
12. radio/antenna
13. fiber
14. electrical grid
15. vibration/seismic
16. meteorology
17. coastal/marine
18. historical landscape
19. cultural heritage
20. frequency/wavelength
21. SWARM graph
22. ECHO timing
23. spectra/coherence
24. null models
25. source discrimination
26. 7.834125 Hz test
27. historical drift
28. provenance/confidence
