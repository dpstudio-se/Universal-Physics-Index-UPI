# 3I/ATLAS gate completion audit

This review implements the previously absent checks. It does not promote the candidate or its
supporting nodes. The intended outcome is an auditable verdict, not necessarily acceptance.

## Canonical baseline

`examples/feedback/canonical_baseline.json` contains all 99 committed JSON blobs under `data/` at
`b2663cb0d9296cb616865d93d549a44159867601`, with exact contents, SHA-256 and Git blob identities.
The checker verifies the inventory against the commit's Git tree. Direct blob reads preserve bytes;
an intermediate archive with converted line endings was rejected and superseded.

This is the selected checked-out canonical baseline, not a claim that it is the latest remote branch.
The original case snapshots separately identify upstream commit `2aa811bf...`. Working-tree content
is not silently substituted into the frozen baseline.

The candidate address is new at the baseline. The helical node and its energy guard are present.
Three original dependencies are absent: `hyperbolic_orbit`, `solar_driven_activity`, and the
observational `3i_atlas` node. The corrected hyperbolic working-tree node is separately hashed but
not treated as a committed dependency. The canonical gate therefore returns UNKNOWN/STOP with the
missing addresses. Next action: review/version those dependencies against an explicitly selected
canonical commit, then compare again. No commit, merge or promotion is performed by this audit.

## Software-result binding

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe examples/feedback/run_validation.py
```

The runner snapshots candidate version and canonical-JSON/file hashes; source versions and byte
hashes; the selected baseline; claim classifications; validation policy version; and a full inventory
of current code, schemas, tests, fixtures and documentation. The base commit alone does not identify
uncommitted code: the working-tree input digest does. Input drift during the run fails the receipt.

Each Python test has its exact collected node id and setup/call/teardown results. Each JavaScript
test has its TAP name and result. Every test result and suite references the same binding SHA-256
and uses `verification_type: software_test`. Suite records retain commands, environments, collection
sets and their hashes, and hashed raw result/log files. Lint/type checks share that binding.
Pytest skips, absent cases, changed logs, changed inputs, missing suites or failed checks block.

The complete run produces `examples/feedback/test_receipt.json`, with raw logs/results below
`examples/feedback/runs/`. A single receipt binds all three suites: root Python, ResonanceFS Python,
and laboratory JavaScript. Historical exploratory counts are not retroactively attributed to this
candidate. The receipt records local execution, not a cryptographically signed independent attestation.

The software gate verifies the final receipt after the suites finish. Test collection itself may
see the previous receipt as absent/stale: that is expected, not an exemption. The new receipt is
created only after all final inputs are unchanged and the recorded tests have completed.

Generated receipt, result and log artifacts are excluded from the input digest to avoid a circular
hash definition. They are output evidence with their own hashes. Any later source, code, test,
candidate, claim-ledger or documentation change requires a fresh run. Tests verify software
behavior within this declared environment; they do not establish physical equivalence or replication.

## Claim coverage versus claim resolution

`claim_coverage.json` and its readable Markdown companion cover every one of the original case's
104 scalar leaves in 43 classified groups, including separate audits of mixed status labels.
Each group identifies exact source pointers/values, role, scoped status, evidence references,
falsification condition and unresolved evidence/action where applicable.

Metadata EST means the field exists in the source, not that its scientific interpretation is true.
Policy and symbolic references have no executable or evidential authority. The coverage validator
checks completeness and source integrity; the scientific assignments remain an explicit review,
not an automatic truth classifier. Coverage can PASS while claim resolution remains STOP.

Scoped orbital relations are DER and the primary reported fit/observation claims retain their
declared evidence. Legacy approximate values lack their original epoch/solution binding and remain
STOP; JPL solution 54 is not retroactive provenance for them. The Hubble coma observation is supported
by [NASA's instrument/date/program record](https://science.nasa.gov/asset/hubble/comet-3i-atlas/).
The broader structural exclusion needs resolution-limited analysis. Exact birth star, age/origin,
quantitative activity models and an artificial-object hypothesis require their own evidence or tests.
The original whole-case EST and mixed labels cannot override these boundaries.

For each unresolved group, the JSON/Markdown ledger names its exact next action: identify the legacy
orbital solution, supply calibrated imaging/PSF limits, fit thermal/outflow/spectral models, provide
stellar phase-space/encounter inference, or state and test a discriminating artificial-origin prediction.
The original archived case is unchanged; candidate 0.2.1 remains STOP outside `data/`.

## Non-gravitational model

The ledger preserves all JPL solution 54 model parameters, values, units, fit kinds and sigmas,
including A1, A2, A3 and DT and the activity-law constants. These are verified against the pinned
response; JPL `kind: EST` means estimated, not the UPI scientific classification EST.

The checked algebra is for osculating conic elements at JD 2461090.5 TDB. No full-force propagation,
held-out astrometric residual check or incoming/outgoing asymptotic reconstruction is implemented.
Long-term propagation remains STOP: use the fitted activity law and time offset, nongravitational
accelerations, planetary perturbations and covariance, and compare against a versioned astrometric
test set. Passing two-body algebra does not establish that two-body gravity is sufficient.

## Outputs and failure conditions

The runner updates `atlas_review_result.json`, `canonical_comparison.json` and
`claim_analysis_result.json`. They distinguish: performed comparisons, complete classification,
passing bound software tests, and unresolved scientific/canonical requirements. Every unresolved
claim retains its own reason/action. No `/api/promote` call is made by the runner.

Failure conditions include: an uncommitted dependency treated as canonical; incomplete claim
coverage accepted; a stale/partial test receipt accepted; nongravitational terms omitted; or an
unrelated claim promoted by orbital agreement. PostgreSQL live integration remains a separate
unverified track and is not counted as verified by the SQLite/software suites.
