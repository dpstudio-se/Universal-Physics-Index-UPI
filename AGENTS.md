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
