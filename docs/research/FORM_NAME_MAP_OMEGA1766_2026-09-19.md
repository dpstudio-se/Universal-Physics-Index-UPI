# Ω1766 / UPI — Form & Name Map
Date: 2026-09-19

## Objective

Map names, visual forms, mathematical forms and physical forms from the latest image batch into typed UPI nodes.

Rule:
NAME != FORM != PHYSICAL MECHANISM

A shared name or visual shape is not evidence of a shared physical process.

## 1. Astronomical forms

### NGC 6302
Names:
- NGC 6302
- Butterfly Nebula
- planetary nebula

Forms:
- bipolar / hourglass morphology
- central dust torus
- two opposing lobes
- ionized gas structures

UPI types:
NAME: astronomical object
FORM: bipolar geometry
PHYSICS: stellar outflow + ionized gas + radiation

Status:
astronomical object and broad morphology = EST
"butterfly" = visual descriptor

Relation:
NGC6302 --HAS_FORM--> BIPOLAR_LOBE
NGC6302 --HAS_FORM--> DUST_TORUS
NGC6302 --VISUAL_ALIAS--> BUTTERFLY

## 2. Fourier / epicycle forms

Names:
- Fourier series
- harmonic
- epicycle
- partial sum
- square-wave approximation

Forms:
- rotating-circle construction
- sinusoidal components
- odd-harmonic ladder
- reconstructed periodic waveform

Displayed form:
y_6(x) = sum[k=0..6] 2/(2k+1) sin((2k+1)x)

Harmonic indices:
1, 3, 5, 7, 9, 11, 13

UPI types:
FORM: harmonic decomposition
MATH: Fourier partial sum
SIGNAL: periodic waveform

Relations:
COMPLEX_SIGNAL --DECOMPOSED_BY--> FOURIER
FOURIER_COMPONENT --HAS_HARMONIC--> n
EPICYCLE --REPRESENTS--> SINUSOIDAL_COMPONENT

Status: EST mathematics.

## 3. Sonoluminescence forms

Names:
- sonoluminescence
- acoustic cavitation
- bubble collapse

Forms:
- spherical bubble
- radial oscillation
- rapid collapse
- shock/compression region
- short light pulse

Physics chain:
acoustic pressure -> R(t) -> collapse -> compression/heating -> emission

UPI types:
FORM: spherical cavity
DYNAMIC: nonlinear radial oscillation
ENERGY: acoustic -> internal/radiative channels
OUTPUT: photon emission

Relations:
SOUND_FIELD --DRIVES--> BUBBLE
BUBBLE --OSCILLATES_AS--> R(t)
COLLAPSE --PRODUCES--> LIGHT_PULSE

Status:
sonoluminescence = EST phenomenon
microscopic emission pathway = model-dependent

## 4. Musical spiral form

Names:
- Music for Aliens
- musical notation
- spiral score
- rhythm
- pitch

Forms:
- staff notation
- note sequence
- temporal rhythm
- pitch sequence
- logarithmic/Archimedean-looking spiral visual motif

UPI separation:
RHYTHM = temporal structure
PITCH = acoustic frequency
SPIRAL = spatial/geometric structure
SCORE = information representation

Do not convert spiral geometry directly into temporal frequency without an explicit transform.

Status: SYM/creative representation.

## 5. Mathematical-name map

Euler:
e^(i*pi)+1=0
TYPE: EST mathematical identity

Ramanujan:
rapidly convergent series for 1/pi
TYPE: EST mathematical result

Gauss:
Gaussian distribution
TYPE: EST mathematical/statistical model

Newton:
F=G*m1*m2/r^2
TYPE: EST classical gravitational law within its domain

Euclid:
Euclidean geometry
TYPE: EST mathematical framework

Archimedes:
F_b=rho*g*V
TYPE: EST buoyancy relation under standard displaced-fluid assumptions

Pythagoras:
a^2+b^2=c^2
TYPE: EST Euclidean geometry

von Neumann:
A*x=lambda*x
TYPE: EST linear algebra / eigenvalue problem

Riemann:
zeta(s)=sum[n=1..infinity] 1/n^s for Re(s)>1
TYPE: EST mathematical definition in convergence domain

Control:
The image's phrase "History's Greatest Minds" is editorial and is not stored as a scientific ranking.

## 6. Egyptian symbolic forms

Names:
- Anubis
- Opening of the Mouth
- funerary ritual
- judgment imagery

Forms:
- jackal/canine-headed deity
- ankh-like symbols
- funerary chamber
- ritual gesture
- luminous modern graphic effects

UPI separation:
HISTORICAL_NAME -> source-backed cultural entity
RITUAL_FORM -> archaeological/textual evidence required
AI_VISUAL_EFFECT -> modern representation

Potential relation:
ANUBIS --ASSOCIATED_WITH--> FUNERARY_CONTEXT

Status:
historical/cultural claims require source verification
visual luminous effects = SYM/artistic

## 7. Norse forms

Names:
- Frigg
- Fensalir
- Æsir
- Ragnar/Lagertha as modern media references

Forms:
- woven textile
- spindle
- braided hair
- Viking-age-inspired clothing
- shield/warrior imagery

UPI rule:
Modern costume/AI art is not automatically historical evidence.

Frigg:
NAME: Norse mythological figure
FORM: modern artistic reconstruction
SOURCE_STATUS: source verification required for individual attributes

Ragnar/Lagertha:
NAME: modern media/cultural reference in the screenshot
FORM: modern photograph/media representation
STATUS: MEDIA/PROVENANCE

## 8. Cross-domain form dictionary

BIPOLAR:
two dominant opposing lobes or directions.
Used in astronomy and other physical systems only when geometry supports it.

SPIRAL:
planar/3D curve with changing radius or pitch.
Can occur in physical systems, mathematics, art and symbolism.
A visual spiral alone does not specify dynamics.

TORUS:
ring/doughnut geometry.
In NGC 6302, a dusty central torus is part of the astrophysical model.
Do not equate every ring symbol with a physical torus.

WAVE:
requires a propagating or oscillating degree of freedom plus a medium/field/model.
A drawn squiggle is not automatically a physical wave.

FREQUENCY:
requires definition of what repeats and its unit.
Same numeric value does not imply same physical phenomenon.

ROTATION:
angular motion around an axis.
An epicycle can represent harmonic motion mathematically without implying a literal rotating physical object.

## 9. Ω1766 name/form gate

For every new node:

NAME
-> ENTITY TYPE
-> FORM TYPE
-> PHYSICAL/MATHEMATICAL DOMAIN
-> UNITS
-> EQUATION
-> MECHANISM
-> EVIDENCE
-> STATUS

Promotion rule:

EST only when the claim is established within its stated domain.

DER when derived from established inputs.

HYP when testable but not established.

SYM when conceptual/cultural/metaphorical.

STOP when required evidence or mechanism is missing.

ERR when contradicted or mathematically invalid.

## 10. Core graph

NAME
  |
  v
ENTITY
  |
  v
FORM
  |
  v
MODEL
  |
  v
MECHANISM
  |
  v
MEASUREMENT
  |
  v
STATUS

This prevents the common category error:

similar name/shape -> assumed same physics.

## 11. Ω1766 cross-scale hypothesis to test

Potentially reusable mathematical structures can be compared across scales:

harmonic signal
<-> bubble oscillation
<-> cavity mode
<-> astrophysical bipolar structure

But the comparison must use dimensionless quantities or explicitly transformed dimensional variables.

Candidate normalized variables:

tau = t/t0
r = R/R0
fhat = f/f0
Ehat = E/E0
Shat = S/k_B

A structural similarity becomes scientifically meaningful only if the governing equations and boundary conditions map consistently.

Status: HYPOTHESIS / research program, not established unification.

## UPI write policy

Preserve:
- original name
- aliases
- observed form
- source/provenance
- domain
- status
- equations
- uncertainty
- transformation used

Never collapse an artistic alias, cultural symbol, mathematical representation and physical mechanism into one node merely because they look alike.


## 12. FORMULA <-> NAME registry

This section makes the mathematical names explicit so that formulas can be indexed as named UPI objects.

| Name | Formula / mathematical form | Domain | Status |
|---|---|---|---|
| Euler identity | e^(i*pi)+1=0 | complex mathematics | EST |
| Pythagorean theorem | a^2+b^2=c^2 | Euclidean geometry | EST |
| Newton gravitation | F=G*m1*m2/r^2 | classical mechanics | EST within domain |
| Archimedes buoyancy | F_b=rho*g*V | fluid statics | EST under standard assumptions |
| Eigenvalue equation | A*x=lambda*x | linear algebra | EST |
| Riemann zeta | zeta(s)=sum 1/n^s, Re(s)>1 | analysis / number theory | EST definition in convergence domain |
| Gaussian PDF | p(x)=1/(sigma*sqrt(2*pi))*exp(-(x-mu)^2/(2*sigma^2)) | probability/statistics | EST |
| Fourier series | x(t)=a0+sum[a_n cos(n*omega0*t)+b_n sin(n*omega0*t)] | signal analysis | EST |
| Image Fourier partial sum | y_6(x)=sum[k=0..6] 2/(2k+1) sin((2k+1)x) | harmonic reconstruction | EST mathematical construction |
| Sonoluminescence bubble model | R*Rddot+(3/2)*Rdot^2=(P_B-P_inf-2*sigma/R-4*mu*Rdot/R)/rho | nonlinear bubble dynamics | EST model class; details depend on regime |
| Wave relation | lambda=v/f | wave physics | EST |
| Angular frequency | omega=2*pi*f | oscillations/waves | EST |
| Energy-frequency relation | E=h*f | quantum physics | EST |
| Mass-energy relation | E=m*c^2 | relativity | EST |
| Equivalent mass from photon energy | m_eq=E/c^2=h*f/c^2 | energy-equivalent quantity | DER from established relations |
| Generic wave field | psi(r,t)=sum A_n(t) exp(i(k_n·r-omega_n*t)) | field/wave modelling | DER/model representation |
| Beat frequency | f_beat=|f1-f2| | interference/beating | EST |
| Two-frequency superposition | cos(2*pi*f1*t)+cos(2*pi*f2*t)=2*cos(2*pi*(f1-f2)t/2)*cos(2*pi*(f1+f2)t/2) | wave mathematics | EST |
| Entropy balance | dS_system/dt=Sdot_in-Sdot_out+Sdot_gen | thermodynamics | EST |
| Internal entropy production | Sdot_gen >= 0 | thermodynamics | EST |
| Energy balance | dU/dt=P_in-P_out+P_internal | thermodynamic bookkeeping | EST/model-dependent partition |
| Fixed-cavity scaling | f_n proportional to 1/R_eff | idealized modal scaling | DER/HYP when applied to a specific Earth cavity |
| Normalized radius | r=R/R0 | dimensionless modelling | DER |
| Normalized frequency | fhat=f/f0 | dimensionless modelling | DER |

### Named-structure links

EULER_IDENTITY --HAS_FORM--> e^(i*pi)+1=0
PYTHAGORAS --HAS_FORM--> a^2+b^2=c^2
NEWTON --HAS_FORM--> F=G*m1*m2/r^2
ARCHIMEDES --HAS_FORM--> F_b=rho*g*V
VON_NEUMANN --HAS_FORM--> A*x=lambda*x
RIEMANN --HAS_FORM--> zeta(s)
GAUSS --HAS_FORM--> GAUSSIAN_PDF
FOURIER --HAS_FORM--> HARMONIC_SERIES
EPICYCLE --REPRESENTS--> HARMONIC_COMPONENT
SONOLUMINESCENCE --MODELLED_BY--> BUBBLE_RADIAL_DYNAMICS
WAVE --HAS_RELATION--> lambda=v/f
QUANTUM_ENERGY --HAS_RELATION--> E=h*f
MASS_ENERGY --HAS_RELATION--> E=m*c^2
THERMODYNAMIC_SYSTEM --HAS_BALANCE--> dS/dt=Sdot_in-Sdot_out+Sdot_gen

### Formula-name control

A formula is indexed with:
FORMULA_NAME
-> SYMBOLS
-> UNITS
-> DOMAIN
-> ASSUMPTIONS
-> DERIVATION
-> EVIDENCE
-> STATUS

Important:
A formula can be mathematically valid while an application of that formula to a particular physical system remains HYP or STOP because geometry, parameters, boundary conditions or measurements are missing.
