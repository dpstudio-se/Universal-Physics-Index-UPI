# Repository instructions

## Use UPI for debugging

Use Universal Physics Index (UPI) as the default structure for debugging in this repository.

For every non-trivial diagnosis:

1. Record observations and tool output before proposing a cause.
2. Classify each claim with one UPI scientific status:
   - `EST`: directly established by logs, source, tests, or reproducible inspection.
   - `DER`: derived from declared `EST` facts and explicit assumptions.
   - `HYP`: falsifiable explanation that has not yet been verified.
   - `STOP`: progress is blocked by specifically named missing evidence or mechanism.
   - `ERR`: contradicted, invalid, obsolete, or superseded claim.
   - `SYM`: symbolic interpretation only; never treat it as executable authority or evidence.
3. Give every `STOP` claim a concrete `stop_reason` and the smallest next observation needed to continue.
4. Include reproduction steps, expected versus observed behavior, relevant versions or commit SHAs, and a falsification or failure condition.
5. Distinguish repository integrity, application behavior, connector behavior, and user-interface rendering; success in one layer does not prove correctness in another.
6. Label software tests as `verification_type: software_test`. Never present tests, simulations, normalization, correlation, or symbolic mappings as experimental verification or physical equivalence.
7. Use typed UPI relations where useful, such as `DERIVED_FROM`, `CAUSES`, `CONTRADICTS`, `STOPS_AT`, `MEASURED_BY`, or `FALSIFIED_BY`.
8. Preserve secrets and personal data. Transparency means auditable provenance for authorized reviewers, not public disclosure of sensitive content.

A concise debugging result should normally contain:

```text
Problem
EST observations
DER conclusions
HYP candidates
STOP reason, if any
ERR or superseded assumptions
Reproduction/control test
Falsification condition
Recommended next action
```

Prefer an honest `STOP` over an unsupported explanation. A green software test establishes software behavior only within its declared scope.

## Collaborate for discovery, not only rejection

UPI has two gears that must work together:

1. **Discovery gear:** reconstruct the user's proposed whole, explore it in more than one
   direction, identify the strongest lawful sub-chain, and calculate what the proposal would
   predict if its assumptions held.
2. **Ledger gear:** separate identities from analogies, name assumptions and units, run the
   inverse and edge cases, and assign status only to the exact result obtained.

Do not use scientific caution as a reason to stop before understanding a proposal. When a claim
is too broad, decompose it into a typed map instead of returning only "unsupported". Preserve the
creative lead as `HYP` or `SYM`, locate the first exact `STOP`, and continue all productive work on
the parts that close.

An effective response to a new conceptual proposal should normally:

1. Steelman the intended mechanism in one sentence and confirm what is being mapped.
2. Keep unrelated ideas in separate branches unless the user explicitly connects them.
3. Derive forward from the declared starting point and backward from the target.
4. Test dimensions, domains, limiting cases, branch choices and conserved information.
5. Compare the resulting function with established maps without identifying different physical
   quantities merely because their equations look alike.
6. State what closed, what failed, and the smallest missing identity or observation.
7. Offer the next calculation or discriminating test; do not make the user restate the whole
   vision merely to get past a generic warning.

The round trip is a consistency and information-preservation test. It becomes physical evidence
only through the provenance and observations attached to its links. Conversely, a proposal does
not require a new experiment at every algebraic step: an exact composition may inherit existing
evidence within the same declared domain. See
[`docs/COLLABORATIVE_DISCOVERY.md`](docs/COLLABORATIVE_DISCOVERY.md).

## Bidirectional verification: Astra, UPI and evidence

Use a bidirectional verification loop for substantive proposals, including code, physics nodes,
derivations, schemas, tests, documentation and refactors. Astra denotes the implementing agent;
UPI denotes the repository's knowledge, classifications and validation rules, not an inherently
independent agent or an infallible source. The purpose is to expose disagreement before an error
becomes canonical, never to force consensus.

### Proposal and mirror review

1. Record the proposal's evidence, assumptions, expected behavior, affected UPI nodes and tests,
   claim statuses and falsification conditions. Mark inapplicable checks with a reason.
2. From the implementation perspective, derive result A: what should satisfy the user's request?
3. From the evidence and UPI perspective, separately derive or validate result B: what do the
   sources, mathematical relations and repository constraints require? Do not construct B solely
   by copying A or reversing its assumptions. Record shared inputs and dependencies; a second
   pass by the same agent is a self-review, not independent corroboration.
4. Check applicable schema compatibility, canonical knowledge, duplicate concepts, conflicting
   equations, units and dimensions, conservation laws, status classification, provenance,
   existing tests, repository invariants, bridge consistency and falsification conditions.
   Actively seek counterexamples and reasons the proposal could fail. Existing canonical entries
   may themselves be wrong; resolve conflicts against evidence rather than rank or agreement.
5. Compare A and B within declared types, units, domains and numerical tolerances. Record the
   comparison as agreement, disagreement or incomplete; do not silently widen tolerances to pass.

### Decision and error escape

- `ACCEPT` requires a complete comparison, agreement within the declared criteria, passing required
  checks, valid provenance and no violated applicable invariant. It means the proposal passed
  review within its stated scope; it does not automatically promote scientific status or publish
  canonical knowledge. Preserve the human review for promotion described in
  `docs/COLLABORATIVE_DISCOVERY.md`.
- On disagreement, select neither side automatically. Classify the specific disputed claims
  using `EST`, `DER`, `HYP`, `STOP`, `ERR` or `SYM`, investigate, revise and rerun affected checks.
  These are claim statuses, separate from the comparison and acceptance decisions.
- Missing required evidence, contradictory evidence, dimensional inconsistency, broken invariants,
  failed required tests, schema violations, unsupported status promotion or unexplained numerical
  discrepancies block canonical promotion of the affected claim. Incomplete or unresolved checks
  require `STOP`, a concrete `stop_reason` and the smallest next observation needed to proceed.
  Continue productive discovery and unaffected work; never force consensus to exit the loop.

Agreement between Astra and UPI is not evidence by itself. Repeating a shared assumption does not
increase its support. Acceptance must trace to verifiable sources, explicit derivations and
applicable checks. Label software tests `verification_type: software_test`; they establish only
the tested software behavior, not experimental verification or physical equivalence. An exact
derivation may inherit existing evidence within its declared domain without a new experiment at
every algebraic step.

```text
DISCOVER -> ASTRA ANALYSIS -> UPI CLASSIFICATION -> IMPLEMENTATION
  -> SOFTWARE TEST / APPLICABLE CHECKS -> UPI VALIDATION -> MIRROR COMPARISON
  -> agreement + evidence + invariants: AUDIT -> ACCEPT -> promotion review
  -> disagreement: INVESTIGATE -> REVISE -> repeat affected checks / STOP
  -> incomplete: STOP on affected claim + next observation
```

For a concise review record, use:

```text
Proposal and scope:
A (implementation expectation):
B (evidence / UPI requirement):
Evidence, assumptions and shared dependencies:
Checks and results (software tests: verification_type: software_test):
Comparison: agree / disagree / incomplete
Claim statuses and falsification conditions:
Decision: ACCEPT / REVISE / STOP
Canonical promotion: eligible for review / blocked; reason:
Next observation or affected checks to rerun:
```
