# Image Physics Corrections — 2026-09-30

## Scope and evidence boundary

This record corrects equations and numerical claims visible in the supplied
frequency, entropy-clock, antenna-stub, Navier–Stokes and 27D concept images.
The images are read-only inputs; this document records the corrected model,
not edits to those images.

Statuses:

- `EST`: follows from a defined equation or established relation within scope.
- `DER`: calculated from declared inputs and assumptions.
- `HYP`: a physical interpretation needing independent evidence.
- `SYM`: a visual or architectural analogy.
- `STOP`: insufficient definitions or evidence to calculate the proposed claim.

## Frequency, period, phase and wavelength

For positive frequency `f`:

```text
T = 1/f
omega = 2 pi f
phase(t) = phase_0 + 2 pi integral_0^t f(t') dt'
```

For an electromagnetic wave in vacuum, `lambda = c/f`. For a wave in a medium,
`lambda = v_phase/f`; frequency alone does not determine its wavelength without
the wave type and propagation speed.

Using exact `c = 299792458 m/s`:

| Reference | Frequency | Period | Vacuum EM comparison wavelength |
| --- | ---: | ---: | ---: |
| TF1766 image label | 1.766 Hz | 0.566251415629 s | 169757.903737 km |
| Resonance-named model reference | 7.834125 Hz | 0.127646674006 s | 38267.510156 km |
| 0.126 s pulse reference | 7.936507936508 Hz | 0.126 s | 37773.849708 km |
| 8 Hz control clock | 8 Hz | 0.125 s | 37474.057250 km |

The 7.834125 Hz value is a configurable reference used in the model, not an
assertion that a Schumann resonance is constant or exactly equal to that number.
Schumann modes are Earth–ionosphere cavity modes, not free-space waves.

The 0.126 s pulse and 8 Hz clock are distinct:

```text
8 - 1/0.126 = 0.063492063492 Hz
T_8 - 0.126 s = -0.001 s
relative-phase recurrence = 1/(8 - 1/0.126) = 15.75 s
phase slip = 2.857142857 degrees per 8 Hz cycle
```

For 8 Hz and 7.834125 Hz:

```text
delta_f = 8 - 7.834125 = 0.165875 Hz
T_8 - T_7.834125 = -0.002646674006 s
relative-phase recurrence = 1/delta_f = 6.028636021 s
```

## Shared "Entropy Clock & Earth Matrix" dashboard

The user-provided Gemini share displays a dashboard labelled "Entropy Clock &
Earth Matrix" and "Non-Linear Coordinate Telemetry Engine". Its displayed
"Schumann (f)" value is 7.61 Hz. This is a displayed app value, not a verified
measurement: the share provides no instrument, calibration, acquisition
timestamp, raw series, estimator, uncertainty, or source for this reading.

Arithmetic derived from that displayed value:

```text
f = 7.61 Hz
T = 1/f = 0.131406044678 s
omega = 2 pi f = 47.815040187637 rad/s
lambda_vac = c/f = 39394.541130 km
8 - f = 0.39 Hz
T - T_8 = 0.006406044678 s
relative-phase recurrence versus 8 Hz = 1/0.39 = 2.564102564 s
```

The vacuum wavelength is only a dimensional comparison for an electromagnetic
wave in vacuum; it is not the propagation wavelength of a Schumann cavity mode.
The 7.61 Hz display must remain distinct from the configured 7.834125 Hz
reference, the 0.126 s pulse (7.936507936508 Hz), and the 8 Hz control clock.
No automatic update or redefinition of those references follows from a dashboard
value without measurement provenance and an explicit model rule.

The same screen displays entropy `0.244`, flow load `0.24`, temperature `+4.7
°C`, pressure `1019.3 hPa`, humidity `27%`, wind `18 m/s` at `166°`, and an
"Eye State" of "3rd Eye Bridge". The screen does not define units or state
functions for entropy and flow load, document the meteorological data source or
timestamp, or define "3rd Eye Bridge" as a measurable quantity. Treat these as
UI values/labels (`SYM` or `STOP` for physical interpretation), not established
telemetry or physical couplings. The screen's coordinate readout is not
reproduced here because its location provenance and purpose are not established.

For equal-amplitude sinusoids, the identity

```text
cos(2 pi f_1 t) + cos(2 pi f_2 t)
= 2 cos(pi (f_1-f_2)t) cos(2 pi ((f_1+f_2)/2)t)
```

has a signed envelope that changes sign every `1/|delta_f|` and the same-phase
relative phase recurs every `1/|delta_f|`. The observable absolute-amplitude
maxima are spaced by `1/|delta_f|`. The decomposition does not establish a
biological, geophysical or entropy coupling.

## Image clock and entropy claims

- A plotted 8 Hz control has period 0.125 s, not 0.126 s. A plotted 0.126 s pulse
  corresponds to 7.936507936508 Hz. These traces drift in phase if free-running.
- A mapping from frequency bands to cosmic epochs is not implied by `T = 1/f`.
  For example, 0.1 Hz has a 10 s period and 8 Hz has a 0.125 s period; neither
  equation gives a cosmological age. The image's logarithmic frequency-to-age
  interpolation is a model choice, not a derived cosmological law.
- The image's 70/30 ocean/land split is a rounded surface-coverage illustration,
  not an energy or entropy partition. NOAA gives approximately 71% ocean and
  29% land surface coverage: <https://www.noaa.gov/jetstream/ocean>.
- A subsystem's entropy may decrease if entropy is exported. For an isolated
  total system, entropy production is nonnegative. The image's `dS/dt < 0` needs
  an explicitly bounded open subsystem and entropy flux; it cannot represent a
  universal decrease of total entropy.
- `S = -k_B Tr(rho ln rho)` is the von Neumann entropy for a normalized density
  operator. It cannot be equated to the thermodynamic entropy balance without a
  specified statistical/physical model.
- Proper time is metric- and worldline-dependent. For a static metric
  `ds^2 = -N(x)^2 c^2 dt^2 + g_ij dx^i dx^j`, a stationary observer has
  `d tau = N(x) dt`. A proposed `d tau = exp(phi(t)) dt` needs a metric deriving
  `phi`; frequency alone does not provide one.
- `∇·v < 0` denotes local compression. A pressure time derivative alone does
  not determine it. The relevant mass balance is
  `∂rho/∂t + ∇·(rho v) = 0`; incompressible constant-density flow has
  `∇·v = 0`.

## Stub and analog-vent image

For a transmission line with real reference impedance `Z_0`, load reflection is

```text
Gamma = (Z_in - Z_0)/(Z_in + Z_0)
```

The image states `Y_tot = (1-alpha) Y_s` and also that `alpha=1` gives perfect
matching. Under that displayed equation, `alpha=1` gives `Y_tot=0`, an open
circuit (`Z_in -> infinity`), for which `Gamma -> +1`, not zero. Thus the
displayed admittance equation and its perfect-match conclusion are inconsistent.

Perfect matching requires `Z_in=Z_0` (equivalently `Y_in=1/Z_0` for real `Z_0`).
A reactive stub can cancel a susceptance at a specified frequency and position,
but the diagram lacks the complete network topology, load, line impedance,
stub length/placement and component model needed to calculate a match. The
claimed 8 Hz control does not make an RF stub match at 8 Hz; the operating
frequency and electrical dimensions must be specified.

## Navier–Stokes and 27D image claims

- The enstrophy balance and vorticity equation shown are identities/estimates
  under their regularity, boundary and domain assumptions. Displaying the
  Beale–Kato–Majda condition
  `integral_0^T ||omega(t)||_infinity dt < infinity` does not prove that the
  condition holds for arbitrary smooth 3D initial data. The images provide no
  such proof; the general global-regularity problem remains open.
- A special exact smooth solution verifies that solution only, not global
  regularity for all admissible initial data.
- The proposed image functional `f[u] = (1/(2 pi)) ||omega||_L2 / ||u||_L2`
  has units of inverse length when `u` is velocity and `omega` is vorticity.
  It is not a frequency in hertz without a separately declared velocity/length
  scale.
- The 27D `Psi` expression does not define its manifold, measure, fields,
  normalization, units, boundary conditions or derivation. It cannot currently
  establish a conserved invariant or bound on `||omega||_infinity`; status
  `STOP`.
- Similar-looking network diagrams for cities and brains are structural
  analogies (`SYM`) unless datasets, node/edge definitions, spatial scales and
  a preregistered similarity metric are supplied. They do not by themselves
  establish identical physics.

## Verification record and next observations

The values in the frequency table and phase calculations are deterministic
arithmetic (`verification_type: software_test` when checked in code); they do
not establish that an image's reference frequency was measured. To verify a
signal claim, retain the raw time series, sample clock, sample rate, duration,
window, estimator and uncertainty. A 1 s FFT record has 1 Hz bin spacing;
precision finer than that needs a longer record or a documented estimator and
uncertainty analysis.

Smallest next observations:

1. For signal synchronization: provide both sampled signals, a shared clock or
   synchronization rule, and measured phase difference over time.
2. For the entropy clock: define the system boundary, entropy fluxes, metric,
   observer worldline and measured inputs.
3. For the stub: provide `Z_0`, complex load impedance, frequency, line
   topology, stub dimensions and component parasitics.
4. For Navier–Stokes: provide a complete derivation with hypotheses that proves
   the required BKM integral bound for the stated class of 3D initial data.
5. For a 27D bridge: define the mathematical spaces, dimensionally consistent
   map, inverse, limiting cases and a discriminating observable.
