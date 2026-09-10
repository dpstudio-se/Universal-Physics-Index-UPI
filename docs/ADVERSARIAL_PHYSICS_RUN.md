# UPI adversarial physics run — octave scaling and xenon recoil

**Scientific conclusion: DER kinematic compatibility, HYP particle identity.**
The declared numbers produce an energy-equivalent mass near 626.684 GeV/c².
If that mass belongs to a dark matter particle, it can transfer 248 keV to Xe-131
at suitable speed and angle. Neither the particle nor the physical 84-octave
mechanism has been established. `verification_type: software_test` throughout
the computational results. No additional experimental dataset was compared.

## 1. Repository and preservation

EST: inspected commit `20e528a230e871a2cf5ef6c57900248e9f454b98`, branch
`oden-knot-engine`, isolated worktree `.worktrees/oden`. The parent checkout has
uncommitted work, including Aureum nodes. Those were inspected and left untouched.
Search commands and observations are in
[`repository-audit.json`](../examples/adversarial_physics/repository-audit.json).
The search covers available local history and the stated paths; it cannot rule
out an unavailable private derivation or prove the chronological origin of an idea.

EST: input declaration was frozen before this run's calculations in
[`input-freeze.json`](../examples/adversarial_physics/input-freeze.json).
It preserves six existing anchor byte hashes and the request hash. No old node,
scientific classification or known-finding baseline was rewritten.
Git attributes preserve frozen bytes, LF calculation source, and the original
CRLF anchor checkout bytes across platforms; line endings are part of these hashes.

## 2. Existing nodes reused

- `data/information_physics/frequency_mass_equivalent.json`: DER conversion scope.
- `data/bridges/frequency_mass_from_mass_energy.json`: DER, same named energy.
- `data/bridges/frequency_mass_from_planck_constant.json`: EST SI constant scope.
- `data/bridges/frequency_mass_from_planck_einstein.json`: DER quantum-energy composition.
- `data/bridges/information_mass_from_frequency_mass.json`: HYP interpretation.
- `data/bridges/frequency_mass_stops_at_27_11.json`: existing STOP retained.

Existing `physics.py` provides the float forward/inverse controls. Existing ODEN
`Observation`, `Step`, `PathTrace`, `Tolerance` and `analyze` compare the return paths.
Their shared-law provenance is explicit: ODEN reports `DEPENDENT_SOURCES`, and
also `NUMERICAL_NOISE` for the small velocity residual. Independent implementations
do not constitute independently observed physical evidence.

## 3. Files and architecture

Added `src/upi/dark_matter_candidate.py` for Decimal/rational energy conversion,
elastic recoil, inverse speed, truncated-Maxwellian mean inverse speed and Helm
form factor. Added `src/upi/adversarial_physics.py` for write-once prediction
freezes, sweeps, ODEN comparisons and the supplied-observation comparison.
Added `tests/test_dark_matter_candidate.py`, this report, `.gitattributes` and
the `examples/adversarial_physics/` audit records.

Added three nodes under `data/open-problems/octave_recoil_*.json`: H_OCTAVE_84,
H_DM and an ERR correction to the proposed zero-frequency inference. Added three
typed bridges under `data/bridges/octave_recoil_*.json`.

One backward-compatible schema addition was necessary: optional
`falsification_conditions` on bridges. UPI's existing validator already requires
test metadata for HYP records, but the bridge schema previously admitted none of
the recognized fields. Both schema copies, `Bridge` and `bridge_from_json` now
preserve the field. Validation rules and existing record statuses were not relaxed.

## 4. Exact derivation and units

DER under the declared scale map:

\[
N=7\times12=84,\quad f_N=(7.834\;\mathrm{Hz})2^{84},\quad
E_N=hf_N,\quad m_{eq}=E_N/c^2.
\]

Exact SI values: h = 6.62607015×10⁻³⁴ J s, c = 299792458 m/s,
and 1 eV = 1.602176634×10⁻¹⁹ J. Source: [BIPM SI](https://www.bipm.org/en/measurement-units).
No expected mass or velocity is hard-coded in the implementation.

| Quantity (DER) | Value |
|---|---:|
| f₈₄, exact for the declared decimal input | 151531597933776079274370924.544 Hz |
| E₈₄, exact for that input | 1.00405899785079535566394284314890076160×10⁻⁷ J |
| m_eq | 1.117166300239827401399073534175…×10⁻²⁴ kg |
| E₈₄ in eV | 626684334637.971855270448815663… eV |
| m_eq in GeV/c² | 626.684334637971855270448815663… GeV/c² |

The implementation uses 80-digit Decimal arithmetic and stores the exact rational
mass as numerator/denominator. Long digits express arithmetic precision, not
measurement accuracy. [Final prediction](../examples/adversarial_physics/run-002/prediction.json).

Dimensional controls: (J s)(s⁻¹)=J; J/(m² s⁻²)=kg. Dividing joules by the joules
per eV gives eV; dividing by 10⁹ gives GeV. A value stated as GeV/c² names a mass.
In natural-unit recoil formulas, a speed in m/s must be divided by c before squaring.
Tests compare SI and natural-unit implementations explicitly.

## 5. Sensitivity without frequency normalization

DER differences relative to 7.834 Hz, with N held fixed:

| f₀ (Hz) | Δf₀ (Hz) | Relative difference | Δf₈₄ (Hz) | m_eq (GeV/c²) | Δm (GeV/c²) |
|---:|---:|---:|---:|---:|---:|
| 7.83 | −0.004 | −0.0510594843% | −7.73712524553×10²² | 626.364352849 | −0.319981789 |
| 7.834 | 0 | 0 | 0 | 626.684334638 | 0 |
| 8.0 | +0.166 | +2.1189685984% | +3.21090697690×10²⁴ | 639.963578900 | +13.279244262 |

Exactly: Δf₈₄=2⁸⁴Δf₀, and relative frequency/energy/mass changes are identical.
At fixed integer N, u(m)/m=u(f₀)/f₀. No u(f₀) was supplied, so these alternatives
are sensitivity cases, not confidence bounds. N±1 halves/doubles the mass;
N=72,83,84,85,96 are retained. The continuous derivative m ln(2) is only a
diagnostic; it does not define a probability distribution over the integer N.

Control: if the 12 steps meant musical semitones, 84 steps would be seven octaves,
giving approximately 4.14704905443×10⁻²¹ GeV/c², smaller by 2⁷⁷. This does not
replace the user's explicit doubling rule; it tests an easily confused alternative.

## 6. Xenon recoil from conservation

The [NIST isotope table](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&isotype=all)
gives the Xe-131 atomic mass 130.90508406(24) u.
[CODATA 2022](https://physics.nist.gov/cuu/Constants/Table/allascii.txt) supplies
u = 1.66053906892×10⁻²⁷ kg and m_e = 9.1093837139×10⁻³¹ kg.

DER nuclear approximation: m_A=m_atom−54m_e+B_e/c². The baseline neglects total
electron binding B_e, rather than equating the atomic mass with the nuclear mass.
It gives m_A≈2.17323815730×10⁻²⁵ kg≈121.909720005 GeV/c². The 0, 100 keV and
1 MeV electron-binding controls are declared sensitivity probes, not measured
binding energies or uncertainty bounds. Isotopes 129, 131, 132 and 136 are also tested.

In the CM frame an elastic collision preserves |p|=μv. Rotating that momentum
through θ gives q²=2μ²v²(1−cosθ). The initially stationary target has
E_R=q²/(2m_A), so

\[
\mu={m_\chi m_A\over m_\chi+m_A},\qquad
E_R={\mu^2v^2\over m_A}(1-\cos\theta),\qquad
E_{R,max}={2\mu^2v^2\over m_A}.
\]

Here μ≈102.056530230 GeV/c². SI dimensions: kg²(m/s)²/kg=J and q has kg m/s.
The assumptions are elastic two-body scattering, a stationary free nucleus,
CM angle, and nonrelativistic speeds. The API rejects forward recoil calculations
at v≥0.01c. Formal inverse controls outside that domain are explicitly flagged.

| v (km/s), DER | E_R,max (keV) | q (MeV/c) | μ (GeV/c²) |
|---:|---:|---:|---:|
| 220 | 92.018937721 | 149.786534327 | 102.056530230 |
| 361.168539969 | 248.000000000 | 245.900835954 | 102.056530230 |
| 600 | 684.438379744 | 408.508729981 | 102.056530230 |

At a given recoil, v_min=√(m_A E_R/(2μ²)). It is the minimum incident speed;
larger speeds permit the same energy at smaller momentum-transfer angles.
248 keV is not mχc². Its experimental source, uncertainty, recoil calibration,
and whether it is nuclear-recoil or electron-equivalent energy are unknown.

## 7. Independent inverse and ODEN

Path A uses direct SI energy conversion and CM momentum transfer. Path B builds
exact rational constants and reconstructs f from m_eq; a separate lab-frame
conservation inverse uses target speed u=√(2E_R/m_A) and
v=u(1+m_A/mχ)/2. Both energy and momentum conservation are tested.

DER residuals: exact rational f→E→m→E→f is zero; Decimal residual is zero at
80 digits. Existing float API relative energy residual is −1.1102230246251565×10⁻¹⁶;
mass and frequency inverse residuals are zero for the declared input.
The largest speed residual at the three required points is
1.1641532182693481×10⁻¹⁰ m/s (at 600 km/s). ODEN's declared numerical tolerance
is 10⁻¹⁴ times the reference, and its acceptance tolerance is 10⁻¹² times it.
This establishes algebraic consistency within the implementation, not an experiment.

## 8. Rate versus kinematics versus detector response

The rate layer follows the standard flux-times-differential-cross-section
construction; see [PDG, direct detection discussion](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-dark-matter.pdf).
The following is a conditional benchmark, not an inferred interaction model.

Let f_lab integrate to one in velocity space. Per kg of a pure isotope,
N_T=1/m_A and nχ=ρχ/mχ. For a spin-independent elastic contact cross section
σ_A(0) and normalized form factor F(0)=1,

\[
{d\sigma_A\over dE_R}={m_A\sigma_A(0)\over2\mu^2v^2}F^2(q),\quad
\eta(v_{min})=\int_{v\ge v_{min}}{f_{lab}(\mathbf v)\over v}d^3v,
\]
\[
{dR\over dE_R}=\sigma_A(0){\rho_\chi\over2m_\chi\mu^2}F^2(q)\eta(v_{min}).
\]

The implementation outputs the coefficient of σ_A(0), with units
events kg⁻¹ day⁻¹ keV⁻¹ m⁻²; multiply by a nuclear cross section in m².
No numerical σ is selected. No implicit nucleon cross section or A² conversion
is introduced. In SI η has s/m; the unconverted coefficient has
kg⁻¹ s⁻¹ J⁻¹ m⁻². Multiplication by 86400 s/day and the J/keV conversion gives
the reported units. Integrating the point-contact fixed-speed cross section
over 0≤E_R≤E_R,max returns σ_A, checked independently in tests.

Declared halo: ρχ=0.3 GeV/c²/cm³, truncated Galactic Maxwellian
f_gal∝exp(−v²/v₀²) with v₀=220, v_esc=544 and lab boost v_E=232 km/s.
These are illustrative assumptions, not exact universal values. Lab support
ends at 776 km/s. For this isotope/candidate, the recoil support is
0–1144.867682669 keV. The frozen JSON includes the spectrum at 10-keV grid
spacing plus the endpoint and a point beyond it, and a 0–776 km/s velocity sweep.
Analytic η is checked against independent numerical velocity integration,
including its piecewise boundary and cutoff.

The Helm convolution uses R=1.2A^(1/3) fm, skin s=0.9 fm,
R₁²=R²−5s² and F=3j₁(qR₁/ℏ)/(qR₁/ℏ) exp[−(qs/ℏ)²/2]. This particular radius
choice is a phenomenological benchmark, not a precision xenon fit; see the
[form-factor discussion](https://link.springer.com/article/10.1140/epjc/s10052-015-3634-z).
The removable q=0 singularity is handled by a series expansion.

At 248 keV, the baseline F²≈0.0002668731431 and coefficient≈2.325228269×10³¹
events kg⁻¹ day⁻¹ keV⁻¹ m⁻². This large coefficient is **per square metre of
unknown cross section**, not a predicted event count. Varying radius ±10% and
skin 0.8–1.0 fm gives F² roughly 1.10×10⁻⁵–1.75×10⁻³ in these controls.

Detector prediction would require an exposure, efficiency ε(E_R), response
kernel G(E_obs|E_R), isotope fractions and background model:
N_bin=exposure∫bin dE_obs∫dE_R ε(E_R)G(E_obs|E_R)dR/dE_R, plus backgrounds.
These are not supplied. Absolute rate is STOP at the unknown interaction
normalization; the next input is an independently constrained coupling/cross
section. Event counts are STOP at the missing response/exposure information.

## 9. Red-team audit A–J

| Attack | Exact finding and status |
|---|---|
| A: N=84 | HYP: no independent scale mechanism found; N±1 changes the mass by a factor two. |
| B: f₀ | HYP: 7.834 is a configurable SYM reference in the existing repo; measurement provenance is missing. |
| C: rest mass | HYP: E/c² does not identify the invariant mass of a photon or a new particle. |
| D: recoil mapping | DER: conservation checks pass; several distinct candidate masses can generate 248 keV. |
| E: halo | DER: rate varies with density, dispersion, cutoff and boost; support is conditional. |
| F: isotope | DER: v_min spans 363.054733 (Xe-129) to 356.664509 km/s (Xe-136); not one universal speed. |
| G: look-elsewhere | STOP: no complete search history/trial count; next input is dated choices and selection protocol. No significance is computed. |
| H: dimensions | DER: SI/natural-unit and conservation tests pass; semitone/octave ambiguity changes the output by 2⁷⁷. |
| I: circular reasoning | ERR: solving for a free speed and returning the supplied recoil cannot independently validate the mass. |
| J: post-hoc fitting | STOP: the targets preceded this run. Next input is a pre-target derivation or genuinely held-out prediction protocol. A later hash cannot repair earlier selection bias. |

The surviving result after removing attractive numbers is the general conditional
map and the standard recoil/rate equations. Neither 84 nor 626.684 is selected
by those equations. In particular, half and twice the proposed particle mass can
both give 248 keV within the declared halo. If σ_A is free down to zero, a null
count alone cannot falsify this incomplete mass-only hypothesis.

Possible lawful completions were considered separately: a discrete scale symmetry
with ratio two still needs boundary conditions to select 84 steps; an RG flow
needs degrees of freedom and beta functions; a geometric eigenfrequency ladder
needs a specified operator and boundaries. An ordinary harmonic oscillator's
levels E_n=(n+1/2)ℏω do not require an 84-octave frequency ladder. These are possible
research branches, not inferred mechanisms.

## 10. Closure classification and terminology

| Closure type | Status and exact scope |
|---|---|
| Algebraic | DER: named-energy and elastic-backscatter round trips close. |
| Dynamical | STOP: no equation of motion driving the octave ladder; supply one with initial conditions. |
| Causal | STOP: no energy-transfer channel from low-frequency reference to DM; specify mediator and source. |
| Thermodynamic | STOP: no reservoir/boundary flux accounting for physical frequency doubling; supply an energy budget. |
| Feedback | DER: immutable calculation→freeze→comparison records form an audit sequence, not physical feedback control. |
| Spatial boundary | STOP: no metric or domain identifying a causal patch; supply geometry and boundary conditions. |
| Effective-theory domain | DER: declared NR elastic contact calculation for v<0.01c. This is not a derived ultraviolet completion or an identified EFT of the candidate. |

The circle control follows identical spatial geometry with angular rates 1 and 2;
it returns different states at the same time. Another control maps distinct
polarization labels at the same frequency to the same energy equivalent.
Thus SAME GEOMETRY does not identify an evolution operator, and SAME FUNCTION
does not identify an object. No extra causal or thermodynamic closure is inferred.

Terminology is function-specific: use **scale transformation** here; use
**scale invariance**, **self-similarity**, **universality**, or **RG flow** only
after identifying the corresponding mathematical/physical property. A “kammare”
can mean a domain of validity when that is its function; “causal patch” requires
causal geometry. “Lokal ToE” has no automatic equivalence to an EFT. A “fjäder”
can be a helix only if its parameterization supports that identification.
Existing project aliases were not globally renamed.

## 11. Ground-state audit

DER: no literal historical `0 K = 0 Hz = dark matter` record was found in the
declared search scope. A new ERR correction node attaches to that proposed
inference without inventing or erasing a historical claim. For a harmonic
oscillator with ω>0, n=0 gives E₀=ℏω/2, not ω=0; see
[MIT oscillator notes](https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2013/808334d09369e3a726f6f20d82315c20_MIT8_04S13_Lec08.pdf).
Temperature does not label the oscillator frequency. The ω→0 expression is a
limit, not a normalizable bound oscillator at ω=0. Applying hf/c² to f=0 gives
zero for that named energy; another mass contribution requires a separate term.

## 12. Prediction freeze and comparison chronology

EST: final code snapshot is `47eda6013a8c8b6a79db563e48cab7aad9eb9776`.
The final [prediction](../examples/adversarial_physics/run-002/prediction.json)
was written and SHA-256 hashed before the runner read the supplied recoil into
its inverse calculation. It includes model version, commit, timestamp, source
hashes, inputs, conditional mass, assumptions, spectrum, uncertainty boundaries
and falsification criteria.

SHA-256: `a0c7089119028705502a23533b23dcc3d7725919264ee79fe435c7de973914eb`.
Prediction timestamp: `2026-09-10T10:39:28.851248+00:00`.
Result timestamp: `2026-09-10T10:39:28.925620+00:00`.
These local timestamps and hashes establish an inspectable record, not trusted
third-party proof of when a physical idea originated.

Run-001 remains immutable. Run-002 adds ODEN output and explicit domain flags
and is tied to committed code; its primary arithmetic is unchanged. The supplied
248 keV, approximate mass and speed were already known before both freezes.
Background references were consulted for formulas and constants; no candidate
comparison to their experimental exclusion results was performed.
`additional_experimental_comparisons` is empty.

## 13. Reproduction, failure conditions and tests

From the worktree root, with repository dependencies and pytest installed:

```powershell
$env:PYTHONPATH = 'src'
python -m upi.adversarial_physics --output dist/adversarial-new-run
python -m pytest -q
python -m ruff check src tests
python -m mypy src/upi --ignore-missing-imports
```

The output directory must not already exist. Input hash mismatch and overwriting
a freeze are rejected. Repeated runs produce the same numerical results but new
timestamps and hashes. The source revision and frozen source hashes explain
which implementation produced each record.

EST: final full suite **205 passed** (182 existing + 23 new), Python 3.14.7,
pytest 9.1.1. Ruff 0.16.6 passed; mypy 2.3.1 passed across 40 files. New checks
cover exact rational arithmetic, float API agreement, conservation, natural
units, angular/mass limits, input preservation, invalid domains, η quadrature,
rate normalization/cutoff, zero frequency, typed graph/schema round trip, ODEN,
and freeze corruption/overwrite rejection.

During integration, five missing metadata findings caused two triage tests to
fail. Those new-record defects were fixed through explicit provenance and the
optional bridge field; the existing finding catalog remained unchanged.

Falsification of software correctness: residual beyond the declared tolerance,
lost input identity, changed old anchor bytes, malformed graph metadata, negative
rate, nonzero rate beyond halo support, conservation failure, or accepted freeze
tampering. Successful software tests establish no detector behavior, external
connector operation or physical discovery. No deployment, push or main merge.

## 14. Scientific boundary and next discriminating evidence

H_OCTAVE_84 and H_DM remain HYP (open). STOP at: independently derived N and f₀;
particle identity; 248-keV event provenance; interaction normalization; detector
response; historical selection/trials. Each boundary specifies its missing input
above and in the machine-readable records. The next useful evidence is a dated,
independently motivated scale mechanism plus a sourced recoil dataset with
calibration. A future completed model must freeze its coupling, halo treatment,
response and rejection statistic before testing genuinely held-out observations.

```text
EST established laws/constants
  ↓ E = hf
  ↓ m_eq = hf/c²                         DER, named energy
  ↓ f₀ × 2⁸⁴                            DER map; HYP physical N=84
  ↓ 626.684334638 GeV/c²                 DER mass equivalent
  ↓ H_DM                                HYP particle identification
  ↓ Xe-131 elastic scattering           DER conditional kinematics
  ↓ recoil spectrum per unknown σ_A     DER conditional rate
  ↓ supplied observation claim          HYP; provenance STOP
  ↓ ODEN EYE + RED
  ├─ PASS arithmetic                    DER
  ├─ OPEN mechanism / identity          HYP
  ├─ STOP rate / detector / provenance  STOP
  └─ REJECT closure ⇒ discovery         ERR
```

DERIVATION != IDENTIFICATION · COMPATIBILITY != DISCOVERY · CLOSURE != EVIDENCE.
