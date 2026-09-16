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
