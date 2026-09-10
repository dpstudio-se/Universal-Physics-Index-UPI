# UPI realtime / analog foundation / multilayer bridge

Status: **DER software/model extension**, with HYP and STOP boundaries.
UPI remains a bounded physics/evidence service. OdinOS, Puter, an LLM core,
physical sensors and VM execution are not implemented by renaming this service.
UI: `/foundation/`. Computation endpoint: `POST /api/foundation`.

## Before implementation: inventory and plan

EST: inspected `23511491daba38fd5664e1929ddb67390c2f0535` on `oden-knot-engine`.
Baseline: **205 tests passed before edits**. The isolated worktree was clean.
The parent checkout's uncommitted files and request were hashed in
[`preflight.json`](../examples/foundation/preflight.json) and left untouched.
No files were moved. The following inventory and additive plan were communicated
before code changes:

| Handoff sections | Before | Existing overlap / additive implementation |
|---|---|---|
| 1 | EXISTING / CONFLICT | Models, quantities, schemas and validation exist. Retain EST/DER/HYP/STOP/ERR/SYM; OPEN is a separate state and rejection a verdict. No automatic VERIFIED promotion. |
| 2–3 | PARTIAL | Resilience reference lane exists, explicitly without analog hardware. Add protected analog actions, immutable complex observations, sampling/reconstruction and MISFIT. |
| 4 | PARTIAL | UPIGraph, realtime ingestion, runtime and HTTP service exist. Add trusted executable projection, Dijkstra, two-sided search and basic CCH. |
| 5, 20 | EXISTING | Reuse constants, physics.py, frequency-mass node and H_DM boundary. Keep 7.834 and 8 distinct. |
| 6–7 | MISSING | Add free-space/Fresnel and AM models; unsupported propagation remains STOP. |
| 8–10 | MISSING | Add Smith/stub, analog mirror, load controls, losses and parameter sweeps. No prior stub robustness implementation was found in inspected paths. |
| 11–15, 25 | MISSING | Add optional multilayer records with lifecycle, coordinate uncertainty and source validation. No invented underground routes. |
| 16–17 | MISSING | Add blinded topology metrics and triangle counts, without inferring incidence or a ternary tree. |
| 18–21 | PARTIAL / HYPOTHESIS | Retain project symbolism; add bounded thermodynamics/representation examples and hypothesis records. |
| 22 | PARTIAL | Quarantine already stores text without execution. Add observation-only capability verdicts; real isolated VM/EMU remains STOP. |
| 23 | EXISTING / PARTIAL | Reuse content hashes and existing recovery/ingest facilities; return copied raw inputs and expanded traces. |
| 24 | MISSING | Add trusted static specialization benchmark and advisory candidate text; no production self-modification. |
| 26 | MISSING | Add six accessible local panels using labels, symbols and line styles. |
| 27–29 | EXISTING / ADDITIVE | Preserve the UPI/OdinOS boundary and export twelve audited artifact groups. |

New modules: `derivation_router.py`, `analog_rf.py`, `multilayer.py`,
`foundation.py`. The existing server receives additive routes only. New static
files: `foundation.html`, `.css`, `.js`. Existing scientific nodes, status enums,
schemas and known-finding baselines are unchanged.

## Derivation routing

DER: trusted scalar primitives contain source/target quantity identities, units,
equation, factor, inverse ID, status, assumptions, cost and provenance. Traces
add inputs, outputs, uncertainty propagation, constraints and test references.
Scientific text is never evaluated as code. This small executable projection
references existing UPI nodes rather than replacing the knowledge graph.

Dijkstra is the reference. Two-sided search explores forward/reverse graphs and
chooses the cheapest meeting point. Basic CCH performs metric-independent chordal
completion, directed lower-triangle customization and two upward searches.
Shortcuts retain ordered original edge IDs and expand before execution.
Source: [Dibbelt, Strasser and Wagner](https://arxiv.org/abs/1402.0402).
No nested-dissection, perfect-customization or road-network performance claim is
made. Tests compare all pairs on twelve seeded directed graphs, shuffled orders
and two metrics per graph.

Positive finite costs express routing preference, not confidence. HYP/STOP/ERR/SYM
edges remain impassable regardless of cost. Fresh customization avoids stale
shortcuts after changed costs. Hz→J→kg returns DER with `E=h*f` and `m_eq=E/c²`;
continuing to dark-matter identity returns STOP with the HYP bridge. Wrong units,
nonpositive/nonfinite input and unrepresentable output fail explicitly. Unknown
uncertainty stays unknown; propagated uncertainty is first order.

## Analog protection and dual representation

The implemented policy requires analog function and forbids automatic removal.
Allowed actions: PRESERVE, TEST, ISOLATE, COMPARE, HUMAN_REVIEW. These are enforced
module/service paths, not a claim that authorized developers cannot edit Python.

`AnalogObservation` preserves complex values, times, uncertainty, unit, source,
status, domain, timestamp and physical-input identity. Measurement records require
a named physical adapter. ANGELICA/EMILIA are representation aliases, not biological
hemispheres. The supplied example is explicitly a continuous **model**, sampled
at 256 Hz and quantized digitally; it is not physical analog acquisition.

DER: maximum sample error ≈0.000636581 relative field units; piecewise-linear
midpoint error ≈0.00494518. A 0.1-radian phase offset produces MISFIT, preserved
values and a test request. Sampling an 8 Hz signal at 8 Hz gives sample agreement
but an aliasing/reconstruction STOP. Nyquist eligibility alone does not specify
the reconstruction filter or remove finite-record boundary effects.

STOP: no ADC or independent analog reference is attached. Next observation:
named acquisition hardware with timing, phase, calibration, uncertainty,
bandwidth and anti-alias filter response.

## RF and slow modulation

DER for a declared 1-km free-space path:

| Carrier | Vacuum wavelength (m) | FSPL (dB) |
|---:|---:|---:|
| 450 MHz | 0.6662054622 | 85.5120335 |
| 900 MHz | 0.3331027311 | 91.5326334 |
| 2.4 GHz | 0.1249135242 | 100.0520081 |
| 5 GHz | 0.0599584916 | 106.4271833 |
| 6 GHz | 0.0499654097 | 108.0108082 |

FSPL=20log10(4πdf/c); differences are 6.020599913 dB for 900/450 MHz and
22.498774732 dB for 6 GHz/450 MHz. Midpoint first Fresnel radius is sqrt(λd/4).
Source: [ITU-R P.525](https://www.itu.int/rec/R-REC-P.525-5-202411-I/en).
The baseline rejects distances below a wavelength; actual far-field distance
also needs aperture dimensions. Terrain, diffraction, reflection, multipath,
atmosphere, building penetration, antenna pattern and polarization need sourced
path observations. No altitude shells or geographic coverage predictions result.

Expanding `[1+m cos(2πf_m t)] cos(2πf_c t)` gives amplitudes 1, m/2 and m/2.
The model bounds ordinary AM to 0≤m≤1. At 900 MHz and 8 Hz the frequencies are
899999992, 900000000 and 900000008 Hz. Common modulation phase does not imply
common carrier phase. 8 Hz remains 125 ms; 7.834 Hz remains ≈127.648711 ms.

## Smith/stub, dimensions and nonideal hardware model

DER: z=Z/Z₀; Γ=(z−1)/(z+1); z=(1+Γ)/(1−Γ). Applying the impedance-form map to
y=1/z gives Γ_z(y)=−Γ_z(z). The **physical reflection of the same load** written
in admittance is Γ_Y(y)=(1−y)/(1+y)=Γ_z(z). Those are distinct uses of the map.

Γ(l)=Γ_L exp(−j4πl/λ_g): half a guided wavelength closes the rotation; a quarter
changes sign. The line coordinate, complex plane, helical 3D lift and C²≅R⁴
representation of V+/V− are labeled by their actual variables and units. They
do not identify a physical torus or extra spacetime dimensions.

The ideal shorted stub has Z_stub=jZ₀tan(βl). Canceling its extra admittance at
α=1 gives |Γ|=0 and VSWR=1 only with the matched 50 Ω base load. With 100 Ω,
|Γ|=1/3 and VSWR=2. With an open base, |Γ|=1 and VSWR is unbounded.
Thus Y_total=0 is not match. Γ=1's infinite-impedance inverse and stub poles are
explicit finite-domain boundaries. Source:
[Ellingson's transmission-line text](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electro-Optics/Book%3A_Electromagnetics_I_%28Ellingson%29/03%3A_Transmission_Lines/3.16%3A_Input_Impedance_for_Open-_and_Short-Circuit_Terminations).

The nonideal calculation uses Zc*tanh((a+jβ)l), conductor/dielectric attenuation
and a declared phenomenological β/(2Q) addition. Connector R/L, junction shunt C,
velocity factor, linear dispersion, thermal expansion, mirror amplitude/phase,
ΔG and ΔB are included. The mirror tracks the ideal design; actual stub losses
remain observable. Frequency/α and robustness sweeps are retained, including a
slow 8 Hz α(t) control. The declared grid gives minimum |Γ|≈0.0195422.

That is a simulation result, not a universal positive hardware floor. Real
circuits can have deep nulls at particular conditions. A negative-admittance
mirror does not prove passive availability, causality or stability over a band.
STOP: next physical evidence is calibrated complex S11 versus frequency/valve,
repeatability, null/control and active-element stability characterization.
No transmitter or valve is actuated by this service.

## Optional multilayer observations, motifs and triangles

Nine layers separate natural water, water supply, sewer, electricity, heating,
fiber, RF, transport and topography. Lifecycle labels are BUILT,
HISTORICALLY_PLANNED_NOT_BUILT, UNDER_CONSTRUCTION, PROPOSED and UNKNOWN.
Coordinates require CRS and uncertainty. Cross-layer FORM_SIMILAR edges cannot
silently become shared physical mechanisms.

EST scope: [Miva](https://miva.se/vatten-och-avlopp) supports water/sewer service
identity; [Övik Energi](https://www.ovikenergi.se/) supports electricity/heating/
fiber services. These sources supply no exact underground routes here.
[SSA](https://www.ssa.se/distrikt3/om/medlemsklubbar-smcb/) supports SK3LH /
Gullängets Radioklubb as a public club/callsign identity. A historical
[Sveriges Radio report](https://www.sverigesradio.se/artikel/5330316) describes
Skyttis activity. Its search excerpt was available but direct fetching failed;
publication date remains unresolved and present facility state is not inferred.
No private antenna owner or communication is identified.

Åsberget, Skyttis, Gullänget, Bonäset and the hospital area remain candidate
observation areas. The template has **no invented geographic edges or coordinates**.
RF observation fields preserve frequency/band, ARFCN/EARFCN, PCI, RSRP, RSRQ,
SINR, azimuth, time and location uncertainty; they are not collapsed to GOOD/BAD.
Natural hydrology is separate from engineered pipes. Δp=ρgΔh is calculated for
declared inputs; P=ρgQΔh remains STOP without Q. Supply a sourced flow observation.

Topology controls compute degree, normalized shortest-path betweenness, corrected
closeness, cycle rank/redundancy, articulation, reachable path length and vertex
removal robustness. Connected components define the reported partition and its
modularity; this is not optimized community detection. Synthetic relabeling
checks blind signatures, not actual infrastructure equivalence. Reservoir,
valve, switch and feedback roles additionally require functional/dynamical data.

Triangle counts are 1,3,9,27,81; cumulative counts 1,4,13,40,121. G4 spans
41–121 with selected {41,42}. Shared vertices/edges/state and parent incidence
remain STOP. No ternary-tree edges are invented from those counts.

## Thermodynamic, biological and capability boundaries

DER example: k_B T ln2 at 300 K for resetting one unbiased bit in an isothermal,
logically irreversible operation. Actual cost may exceed it. Subsystem entropy
reduction needs environmental accounting; total isolated entropy does not decrease.
[Landauer](https://research.ibm.com/publications/the-physical-nature-of-information).
TF1766/Φ1766 stay SYM information/provenance operators, not thermodynamic laws.

Schumann resonances are an established Earth–ionosphere phenomenon;
[NASA research](https://ntrs.nasa.gov/api/citations/20120000051/downloads/20120000051.pdf).
They do not establish fixed project frequencies, global cognition/phase lock,
1024 Hz biological lock or DNA coherence at 0.0123 Hz. Those stay HYP/OPEN;
only the declared period 1/0.0123≈81.300813 s is derived.

`inspect_text` returns hashes and capability requests but executes, grants and
commits nothing. Deny policy for network/secrets/host writes/tools is not proof
that a VM exists. Isolated EMU/VM execution remains STOP pending a separately
audited adapter and explicit grants. UI/sensor shell and core observer are not
executors. Remote text does not inherit authority.

The benchmark compares existing mass conversion to a trusted static `(h/c²)*f`
specialization, reporting relative error, IEEE-754 XOR, operations, local timing
and traced allocations. Generated source text is advisory and never eval/exec'd.
Maximum example relative error is ≈1.44×10⁻¹⁶. Precomputing the factor saves a
per-query division; timings are not guarantees and traced allocations are not
hardware memory. Computational energy is STOP without measurement. No candidate
automatically replaces production; future execution requires isolated evaluation
and the human/commit gate.

The HTTP endpoint is stateless and does not modify the index. It copies raw
input and returns its hash plus the expanded trace. Durable observation storage
must use existing authorized ingest/recovery facilities; no hidden journal is
claimed. “Realtime” means request-time computation, not hard real-time scheduling.

## Artifacts, UI, reproduction and verification

The artifact command creates twelve JSON groups: derivation, analog_digital,
rf, smith_stub, geographic_multilayer, motif, triangle, hydrology, thermodynamics,
remote_observation, optimization and hypotheses, plus a byte-hash manifest.
Every envelope answers observed/derived/assumed/tested/failed/open. Nested
MISFIT/STOP/HYP entries are collected. Unknown uncertainty stays null.
Timestamps and local benchmark measurements vary across runs.

The six-panel UI uses statuses as text, line styles, symbols, control labels and
keyboard focus. Smith Γ is a model plot, not sensor data. Multilayer records are
an observational list, not an invented map. No color-only status encoding.

```powershell
$env:PYTHONPATH = 'src'
python -m upi.cli serve --host 127.0.0.1 --port 8094 --database sqlite:///:memory:
# Open http://127.0.0.1:8094/foundation/
# Another terminal:
python -m upi.foundation --output dist/foundation-new-run
python -m pytest -q
python -m ruff check src tests
python -m mypy src/upi --ignore-missing-imports
```

With Playwright and Edge installed: `python tests/smoke_foundation.py`.
EST verification: baseline 205; final suite **222 passed**, Ruff passes, mypy
checks 44 files. Edge checks all six panels at 1440/390 pixels with no console
errors. Python 3.14.7, pytest 9.1.1, Ruff 0.16.6, mypy 2.3.1, Playwright 1.62.0.
`verification_type: software_test`; stub sweeps separately say `simulation`.
Initial new-code type annotation errors were corrected without status changes.

Falsification conditions: CCH/Dijkstra disagreement; lost shortcut provenance;
executed HYP edge; mutated raw observation; removed analog function; lost phase
MISFIT; open circuit labeled matched; proposal shown as built; invented triangle
incidence; or remote text granted authority. Tests exercise these boundaries.

Remaining STOPs: physical acquisition, path propagation inputs, circuit stability,
surveyed geography/flow, triangle incidence, isolated execution adapters and
measured computation energy. Software/UI success does not establish those layers.
No external deployment, production self-modification or merge to main occurred.
