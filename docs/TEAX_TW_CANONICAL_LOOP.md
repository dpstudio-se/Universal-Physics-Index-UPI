# T€@X™-TW Canonical Verification Loop

The canonical UPI research loop is:

INPUT
 ↓
EXTRACT
 ↓
CLASSIFY
 ↓
DOMAIN
 ↓
DERIVE
 ↓
MIRROR
 ↓
REVERSE
 ↓
COMPARE
 ↓
Δ
 ↓
VERIFY
 ↓
LOOP

## Operational semantics

INPUT: preserve the submitted claim/data and provenance.

EXTRACT: separate equations, observations, sources, assumptions and transformations.

CLASSIFY: assign EST, DER, HYP, SYM, ERR or OPEN.

DOMAIN: route the item to the relevant UPI chamber, such as physics, frequency, flow, biology, information or legal-source verification.

DERIVE: perform the permitted mathematical/physical derivation and record assumptions.

MIRROR: apply the declared transformation.

REVERSE: apply the inverse/back transformation where defined.

COMPARE: compare the returned state with the original state.

Δ: compute the residual
Δ = Xmirror-back − Xoriginal
when the representation permits numerical comparison.

VERIFY:
- Δ = 0 supports invariance of the tested transformation on its declared domain.
- Δ ≠ 0 routes to re-examination and may become ERR or remain HYP.
- missing source, data or executable transformation routes to OPEN.

LOOP: retain provenance and unresolved branches and feed them into the next workload cycle.

## Guard

An invariant transformation result is evidence about the transformation. It does not by itself establish an unrelated physical, biological, legal or cosmological hypothesis.

## Frequency/flow specialization

frequency
 ↓
integrate_phase()
 ↓
phase
 ↓
navier_stokes_residual()
 ↓
rigid_vortex_*

This specialization is one concrete path through DOMAIN → DERIVE → VERIFY and can feed the MIRROR stage.


## T€@X™ Core Selector + Mirror-Loop Session Guard

The mirror loop may route through one of the registered research cores:

```text
CORE SELECTOR
├── HKTITAN Universal Physics
├── T€@X™ Universal Physics          ← default
└── T€@X™ Universal Physics+        ← extended research core
```

The session guard is a software control around the interactive core, not a physical law or resonance claim.

```text
SELECT CORE
  ↓
SESSION GUARD
  ↓
TAG VERIFIER
  ↓
MIRROR LOOP
  ↓
REVERSE / COMPARE / Δ / VERIFY
  ↓
SESSION GUARD
  ├── ACTIVE  → continue loop
  └── EXPIRED → LOCK
```

Session durations:

- no valid T€@X™ tag: 300 s (5 min)
- valid T€@X™ tag: 1800 s (30 min)

The timeout is measured in software wall-clock time. The ratio is `1800 / 300 = 6`. The corresponding cycle frequencies are `1/300 = 0.003333333 Hz` and `1/1800 = 0.000555556 Hz`.

A tag verifier must be implemented server-side or in another trusted execution boundary. A frontend-only secret is not a security boundary.

### Core capability map

| Core | Cosmological theory | Fundamental QG / unification |
|---|---|---|
| HKTITAN Universal Physics | Index, compare and test | Main research domain |
| T€@X™ Universal Physics | Index, derive, compare and test | Research domain |
| T€@X™ Universal Physics+ | Extended observation/model/residual analysis | Extended QG/unification research pipeline |

`T€@X™ Universal Physics+` adds the current research extensions without changing the default T€@X™ workflow:

- cosmological theory
- galactic and large-scale structure
- dark-matter / baryonic separation
- multiscale wave / oscillation analysis
- quantum-gravity research
- unification research
- adversarial referee
- null-model testing

The core selector changes routing only. It must not bypass provenance, classification, dimensional checks, falsification conditions, or the existing `EST → DER → HYP → STOP/ERR/SYM` controls.
