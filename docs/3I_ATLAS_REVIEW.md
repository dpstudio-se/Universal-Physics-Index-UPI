# 3I/ATLAS: primary-source orbital review

Decision: **STOP / BLOCKED. Do not promote.**

The current gate implementation, binding protocol and exact claim ledger are documented in
[ATLAS_GATE_AUDIT.md](ATLAS_GATE_AUDIT.md). The current generated reports identify every remaining blocker.

## EST: source and metadata

On 2026-09-13 the public [JPL SBDB request](https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=3I&full-prec=true&cov=mat)
returned orbit solution **54**, solution date **2026-02-19 09:10:47**, for C/2025 N1 (ATLAS),
SPK identity 1004083. The request uses the alias 3I. API version 1.3 is distinct from orbit version 54.

The raw response is preserved in `examples/feedback/sources/jpl_3i_atlas_sbdb.json` with SHA-256
`f67ef2e8c4691a437597b32ea324a8b45a6f4cb1b0dee54b7da281daca66ab29`.
The adjacent manifest records the request, retrieval date, identifiers and field-definition source.
The URL returns a mutable current solution; reproducibility uses the saved bytes and solution id,
not an assumption that the URL will return solution 54 forever. No immutable JPL historical URL
was established by this retrieval.

The returned osculation epoch is **JD 2461090.5 TDB**, with equinox **J2000**. The
[SBDB field definitions](https://ssd-api.jpl.nasa.gov/doc/sbdb.html) specify heliocentric IAU76/80
ecliptic elements and formal 1-sigma uncertainties. Covariance epoch equals the element epoch.

| Parameter | Source value | Formal 1-sigma |
| --- | --- | --- |
| e | 6.141351449317625 | 0.00002469 |
| q (AU) | 1.356481057231181 | 0.0000037743 |
| a (AU) | -0.2638374502507929 | 0.00000069616 |
| i (degrees) | 175.1164570850441 | 0.000019023 |

The fit uses 782 observations spanning 2025-05-15 to 2026-02-19. The source includes fitted
nongravitational A1, A2, A3 and DT parameters and an inverse-square activity model comment.
These are statements about the published solution, not independent remeasurement or validation
of every systematic uncertainty. The complete covariance and model parameters remain in the raw file.
JPL's model-parameter `kind: EST` means estimated in the fit; it is not UPI's scientific status EST.

## DER: what closes

The signed osculating identity `a=q/(1-e)` gives **-0.2638374502507929 AU**, agreeing with the
published a at the declared numerical tolerance of 1e-12 AU. This tolerance is a calculation control,
not an observational error bar. The two results share the same fit and do not constitute independent evidence.

Propagating the e/q covariance with derivatives `da/de=q/(1-e)^2` and `da/dq=1/(1-e)` gives
**sigma_a = 6.961602298080138e-7 AU**. This agrees with JPL's rounded sigma_a within the predeclared
relative tolerance 1e-4. The covariance cross term is retained; independence of e and q is not assumed.
The adapter checks the e/q submatrix, not positive definiteness of the complete ten-parameter matrix.

The corrected vis-viva equation passes its energy-identity check. These results apply to osculating
elements at the stated epoch. They do not validate conservative two-body propagation of a solution
whose force model includes nongravitational terms.

## Schema resolution

The unpromoted candidate is `examples/feedback/candidates/3i_atlas_upi_case.json`. It uses the actual
bundled node schema without extending it. The original GitHub case remains unchanged in `sources/`.

| Original shape | Candidate representation |
| --- | --- |
| purpose without description | explicit description of the orbital-only review scope |
| nested orbital_parameters | quantities with units, uncertainties and per-quantity source bindings |
| missing epoch/frame bindings | reference_frame, definitions and the adjacent metadata manifest |
| broad EST and mixed nested status labels | candidate STOP with a concrete stop_reason |
| observation, cometary, origin and symbolic branches | retained in the archived original; not promoted by the orbital projection |

No approximate legacy number is silently relabeled as a precise measurement. The candidate explicitly
adopts solution 54; the original approximate values are a separate archived input with unknown epoch.

## Current gate ledger

| Check | Current meaning | Next action |
| --- | --- | --- |
| canonical | Comparison executes against 99 exact committed blobs; three supporting nodes are absent at the selected baseline. | Review/version the missing dependencies; never count an uncommitted correction as canonical support. |
| software_tests | The full-suite runner creates a per-test binding receipt for the final candidate, sources and code. | Rerun `run_validation.py` after any bound input changes; inspect the generated receipt for the current result. |
| claim_coverage | All 104 original scalar fields are classified in 43 groups with explicit scopes and source bindings. | Preserve the distinction between complete classification and evidence sufficient to resolve each claim. |
| claim_resolution | Scientific evidence gaps and invalid/mixed original labels remain; long-term full-force propagation is not validated. | Follow the per-claim actions in `examples/feedback/claim_coverage.md`. |

The complete case remains STOP and no promotion is performed. The version-bound orbital metadata
and schema pass within the candidate's scope. See [ATLAS_GATE_AUDIT.md](ATLAS_GATE_AUDIT.md) for
all binding rules, the baseline comparison, non-gravitational parameters and exact source references.

## Reproduction and controls

From the repository root:

```powershell
.\.venv\Scripts\python.exe examples/feedback/review_atlas.py
.\.venv\Scripts\python.exe -m pytest tests/test_orbital_source.py tests/test_orbital_review.py tests/test_feedback.py -q -p no:cacheprovider
```

The saved report is `examples/feedback/atlas_review_result.json`. The default example uses the
primary solution. `run_review(use_primary=False)` exercises the prior approximate-data review;
`run_review(use_original=True)` also restores the historical wrong-sign node for regression.

`verification_type: software_test`. Negative controls remove metadata and uncertainties, change
identity, units and covariance epoch, corrupt covariance and alter candidate/source bindings.
Falsification condition: any such corruption passes its affected check, or the complete case is
accepted despite a missing required check. Python environment: 3.14.7; local repository base:
`b2663cb0d9296cb616865d93d549a44159867601` plus the uncommitted reviewed changes.

PostgreSQL live integration remains a separate, unverified integration track. It is neither a
source of astronomical evidence nor a blocker that can be resolved by this orbital calculation.
