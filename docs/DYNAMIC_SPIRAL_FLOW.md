# Dynamic Spiral Flow

UPI's existing `spiral_flow.py` now processes supplied frequency samples through
one shared-state verification loop. No frequency must be preregistered in DNA.
The first controls use **already computed f(t)**. They do not involve waveform
frequency-estimation error. All supplied examples are **SYNTHETIC CONTROLS**.

The inspected main baseline was `4772a76d371b395f668e83e9d9dcd7c27146d333`.
Its `__init__.py` contained literal backslash-n sequences in the new import;
this change fixes that syntax and declares the intended exports in `__all__`.

## Core relations

For a declared frequency f:

- T = 1/f
- omega = 2*pi*f
- E = h*f
- m_eq = E/c^2

For a time-varying frequency, phase is accumulated:

phi[n] = phi[n-1] + omega[n] * dt

The implementation deliberately keeps the 0.126 s pulse reference separate from
7.834125 Hz:

- 1 / 0.126 s = 7.9365079365 Hz
- 1 / 7.834125 Hz = 0.1276466740063504 s
- Delta T = 0.126 - T(7.834125) = -0.001646674006350407 s
- Relative to the 7.834125-Hz period: Delta T / T_ref = -0.01290025 = -1.290025%

The gen-pulse reference, resonance-named reference, TF1766 and 8 Hz endpoint remain
distinct. These are declared reference labels, not universal constants or measurements.

## Three shared-state modes

NavierMode.VELOCITY exposes the rigid-vortex control field.

NavierMode.VORTICITY exposes its exact curl.

NavierMode.NAVIER_STOKES_RESIDUAL evaluates the residual of the declared
Navier-Stokes equation for supplied derivatives/gradients.

The mode switch cycles without resetting the underlying state.

`SimulationState` stores index, t, f, omega, integrated phase and particle positions.
`with_mode` changes only the view. The dataset computes all field diagnostics at each
step; `navier_mode` chooses a presentation without restarting any trajectory. A test
compares all physical values between cycling and fixed-mode runs.

This is a computational verification layer, not a claim of a new physical law,
and the residual helper is not a full Navier-Stokes solver.

## Explicit dynamics and residual

For the declared rigid-rotation control field v=(-omega y, omega x, 0):

| Term | Formula | Units |
| --- | --- | --- |
| omega | 2 pi f | rad/s |
| alpha | 2 pi df/dt | rad/s² |
| partial_t v | (-alpha y, alpha x, 0) | m/s² |
| (v dot grad)v | (-omega² x, -omega² y, 0) | m/s² |
| laplacian(v) | (0,0,0) | 1/(m s) |
| curl(v) | (0,0,2 omega) | s⁻¹ |
| divergence | 0 | s⁻¹ |
| p-p0 | rho omega²(x²+y²)/2 | Pa |

Pressure is a **declared control field**, with p0=0 for export. It is not inferred
from a measured pressure dataset. Positive uniform density and kinematic viscosity
are explicit inputs. The model assumes a local incompressible Newtonian rigid-rotation
field; geometry, walls and initial-value well-posedness of a real fluid remain separate.

The pressure acceleration cancels the centripetal term, leaving the temporal term
unless a tangential force is supplied. `force_mode=none` sets F=0 explicitly.
`force_mode=manufactured_rotation` explicitly prescribes F=(-alpha y,alpha x,0)
as an analytical/numerical control. The engine never silently fits this force.
For nonconstant frequency the unforced run must expose a nonzero residual.

`residual_validation=FAIL` makes the dataset `state=STOP`; kinematic calculations
retain scientific status `DER`. A passed residual is consistency of this declared
field and forcing, not a general 3-D Navier–Stokes solution or physical observation.

## Numerical conventions

- Samples must have finite, strictly increasing timestamps and finite positive f.
- `differentiate` uses three-point nonuniform interior differences and one-sided
  endpoints. Derivatives at abrupt sampled changes are estimates, not exact smooth
  derivatives of an unknown underlying signal.
- `integrate_phase_samples` uses the requested **right-endpoint rule**:
  phi[n]=phi[n-1]+2 pi f[n](t[n]-t[n-1]), starting at supplied phi0 at t[0].
  This is quadrature; it is not 2 pi f(t)t. Chirp tests verify the difference and
  convergence to the continuous integral.
- `advance_particles` uses **old-state explicit Euler**, x[n+1]=x[n]+v(x[n],t[n])dt.
  It preserves continuity and z, but introduces radial drift in rotation. Tests
  quantify that drift and its reduction as dt decreases; exact trajectories are
  not claimed. There is no randomization.
- `interpolate_frequency` provides an explicitly named piecewise-linear model
  between supplied samples. It does not extrapolate or uniquely reconstruct nature.
- NaN, infinity, invalid time order and unrepresentable outputs are rejected.

## Dynamic discovery and source boundary

`detect_dynamic_nodes` uses caller-declared thresholds for sample-local maxima/minima,
curvature-sign inflexion candidates, rapid transitions, abrupt changes and stable
regions. These features can occur at frequencies absent from every reference node.
Every feature is `status=DER`, `origin=DYNAMIC`; DYNAMIC is not a new scientific enum.
Plateau samples are handled as stable regions; strict extrema require strict neighbours.

Resonance-like **response** peaks require a separately supplied response-amplitude
series. A maximum in f(t) alone is not a resonance peak. Even an amplitude peak keeps
its physical resonance interpretation `HYP`, with transfer-function and control evidence
missing. Noise, sampling and thresholds affect all feature detections; no statistical
significance or uncertainty interval is manufactured.

The next input layer is explicitly separated:

```text
optional A(t) -> opted-in frequency estimator -> sampled f(t)
                                                   |
                                                   v
DNAReader.analyze_dynamic -> dynamics -> residual -> dataset + candidate nodes
```

`estimate_crossing_frequency` is a separately tested opt-in cycle-average estimator,
requiring a declared crossing threshold and one upward crossing per cycle. It does not
identify arbitrary multicomponent signals or prove anti-alias conditions. Its physical
interpretation remains STOP without sampling and signal-model provenance. None of the
14 deterministic dynamics controls uses this estimator.

## Reproduce and export

```powershell
python -m upi.cli dna-dynamic examples/dynamics/frequency-series.json --output result-new.json
python examples/dynamics/run_controls.py .pytest-tmp/dynamics-new-run
python examples/feedback/run_validation.py
```

The JSON input declares source, input_kind, timestamps, f samples, initial particles,
phase origin, density, viscosity, forcing and residual/detection tolerances. Export
refuses an existing output path. No command writes canonical `data/`.

The matrix contains constant, linear and sinusoidal f(t), plus four separate series
crossing TF1766, 7.834125 Hz, 1/0.126 Hz and 8 Hz. Each runs without force and with
explicit manufactured force: **14 controls**. Expected negative residual cases count
as successful software controls only when their datasets remain STOP.

Each dataset includes t,f,T,omega,df/dt,domega/dt,phi, velocity components and magnitude,
curl components and magnitude, divergence, pressure, particle positions, all temporal/
convective/Laplacian/pressure/force/residual vectors, mode and validation flags. Units,
source/input hashes, code hashes and the inventoried DNA are included. The first
particle supplies top-level field columns; `particle_fields` contains every particle.
Candidate features are validated against the existing node schema and retain DER.

No dynamic video renderer is deployed by this change. A future renderer must consume
this verified dataset and bind frames to sample indices/hashes; video consistency
is unverified until that adapter is implemented and tested.

## Changed implementation and checks

- `src/upi/__init__.py`: fix imported main syntax and public exports.
- `src/upi/spiral_flow.py`: reuse physics functions; add differentiate,
  integrate_phase_samples, interpolate_frequency, estimate_crossing_frequency,
  DetectionPolicy, detect_dynamic_nodes, SimulationState, rotation_terms,
  advance_particles and run_dynamic_series. Harden finite/vector/mode validation.
- `src/upi/dna.py`: analyze_dynamic, source binding and schema-valid feature candidates.
- `src/upi/cli.py`: dna-dynamic command and exclusive export.
- `examples/dynamics/frequency-series.json`: labelled sinusoidal control input.
- `examples/dynamics/run_controls.py`: reproducible seven-by-two control matrix.
- `tests/test_dynamic_series.py`: all requested relations, convergence, three-mode
  continuity, negative residual, dynamic detection, independent estimator and bad input.
- `tests/test_spiral_flow.py`: retained main regressions, run alongside the new tests.

Established mathematics supplies the kinematic definitions and the stated NS equation.
The exported calculations are DER under the declared field/model assumptions; the
scientific status model has not changed. TF1766 resonance/coupling remains HYP/STOP.
Windows isolation and 3I/ATLAS remain independently STOP/BLOCKED.
