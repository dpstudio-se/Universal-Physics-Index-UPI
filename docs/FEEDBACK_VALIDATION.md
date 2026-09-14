# Human-directed feedback validation

`upi.feedback.review_node` implements a node-review component. The human supplies intent,
can redirect or defer the work, and receives the resulting review. Human direction is not
scientific evidence. The component does not write canonical records or authenticate approvals.

```text
Human intent -> proposal + expected quantity A
  -> node schema/status checks + evidence artifact integrity
  -> evidence-only derivation B + required domain checks
  -> mirror comparison AGREE / CONFLICT / UNKNOWN
  -> VERIFY / STOP -> human review and next direction
```

## Executed checks and technical boundaries

- The existing node schema and scientific-boundary validators execute on the proposed node.
- Every node `evidence[].source` must resolve to a unique supplied artifact. SHA-256 checks
  the supplied bytes against the expected digest. A digest supplied by the same author establishes
  consistency only; it does not authenticate a publisher or validate the content's truth.
- The mirror derivation receives only evidence artifacts. It does not receive A. Quantity values
  must be finite; units and domains must match exactly; the caller declares an absolute tolerance
  in the quantity's unit. Unit conversion belongs in an explicit domain adapter.
- Required checks default to `physics`, `canonical`, and `software_tests`. Missing checks produce
  `UNKNOWN`, never implicit success. Application code supplies trusted Python callbacks; callbacks
  execute and return `PASS`, `FAIL`, or `UNKNOWN`, reasons, and next observations on failure.
  Additional supplied checks also participate in the gate.
- Each callback receives a fresh copy of the node. Exceptions become `UNKNOWN` without exposing
  exception text. Callback isolation is not a security sandbox or evidence of independent AI.
- The caller owns the required-check policy. A domain adapter must check that A represents the
  proposal, source relevance, assumptions, dimensions, invariants, affected tests and compatibility
  with the canonical baseline. A passing stub or a weakened policy proves none of those properties.

All checks must pass and the mirror must agree before `VERIFY`. The promotion gate then remains
`AWAITING_HUMAN_REVIEW`. Conflicts, unknowns or human `revise`/`defer` produce `STOP` and `BLOCKED`,
with reasons and next actions. A human can change direction but cannot make a failed check pass
by supplying approval. Decisions and comparison outcomes are separate from UPI scientific statuses.

The report includes a SHA-256 of the proposed node, human intent/direction, both quantities,
check details and the limits of independence. It is a review result, not an authorization token:
an integrating promotion service must bind its policy, sources, code version and actual human
decision to the reviewed content and reject stale reports. No existing ingestion or publishing
path is intercepted by the standalone API; the live promotion service integration is described below.

## Reproduction and failure controls

Run from the repository using its Python environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_feedback.py -q
```

The fixture in `tests/test_feedback.py` is a runnable API example using synthetic scalar bytes.
It declares a synthetic-only policy instead of pretending to run physics validation.
`verification_type: software_test` applies to these controls and the gate implementation.

Expected behavior: matching quantities with valid artifact integrity and passing required checks
return `VERIFY` and await human review. Tampered or absent artifacts, changed units/domains,
non-finite results, unavailable checks, callback errors and evidence-boundary violations block.
Human deferral also blocks despite numerical agreement. These cases are regression controls.

Falsification condition: any such failed or unknown required check permits a `VERIFY` result, or
any result automatically writes/promotes canonical data. Passing tests establish only the exercised
software behavior, not experimental verification or general physics correctness.

## First astronomical application: 3I/ATLAS and hyperbolic_orbit

The default example now reviews a pinned primary JPL solution and a schema-valid, unpromoted
orbital candidate. Source metadata, candidate schema, vis-viva and correlated uncertainty checks
pass within their stated scope. Canonical and claim checks now execute, and the full-suite runner
binds each reported test result. The full case remains STOP for absent canonical dependencies and
unresolved claim evidence. See [ATLAS_GATE_AUDIT.md](ATLAS_GATE_AUDIT.md).

See [3I_ATLAS_REVIEW.md](3I_ATLAS_REVIEW.md) for the source revision, metadata, uncertainty
calculation, schema mapping, exact remaining blockers and reproduction commands. Original GitHub
snapshots remain preserved as historical regression inputs. `run_review(use_primary=False)`
restores the previous approximate-data review; `run_review(use_original=True)` also exercises
the original vis-viva sign error.

## Structured review for the human

`FeedbackReport.as_dict()` retains the original fields and adds `review_result` with
`decision_state`, human intent/direction and pending human review, the proposal digest and proposed
status, `astra_result`, `upi_result`, `evidence_result`, mirror quantities/tolerance, `disagreements`,
`missing_checks`, `unknown_checks`, and `required_next_observation` per failed/unknown check.

Absent callbacks are distinguished from callbacks that executed but returned UNKNOWN. A failed
invariant is a disagreement; absent evidence is an unknown. Human deferral is a direction decision,
not a scientific contradiction. Artifact summaries include source references and expected/actual
digests but never raw source bytes. These reports are intended for authorized reviewers and can
contain private references or validator diagnostics; they are not automatically public artifacts.

## Publication integration boundary

The earlier token-plus-source-field-only `/api/promote` behavior is superseded. Both
`/api/promotion-review` and `/api/promote` now run feedback through `ContributionService`.
The default configuration has no promotion policy and blocks promotion.

Configure a trusted `PromotionPolicy(version, prepare)` on the service. `prepare(target)` returns
`PromotionInputs`: the expected quantity, source artifacts, evidence derivation, domain callbacks
and tolerance. `version` must identify the deployed policy/code version. Required checks are fixed
by the service: `physics`, `canonical`, `software_tests` and `status_promotion`, in addition to the
built-in schema/status, provenance-integrity and mirror checks. The status-promotion check must
justify the proposed EST status against the original claim and evidence, including observational
provenance when relevant. This is not supplied by a generic orbital identity check.

The service reviews the exact target payload with status EST. Passing checks return a random receipt
and AWAITING_HUMAN_REVIEW, without changing the store. Approval requires the shared maintainer token,
receipt id and explicit `human_decision=approve`. The receipt binds the current source hash, target
report, human intent and policy version. Reports include evidence digests, quantities and tolerance.
Before writing, the service reruns the policy and all checks and requires the same report hash.
The store then atomically compares the source hash, updates the payload and writes a decision audit.

Receipts expire after 900 seconds, are consumed on success, and are lost on process restart. The
in-memory cache holds at most 256 receipts; eviction requires a fresh review. A missing callback,
exception, conflict, unknown, changed source/evidence/policy or forged client report cannot authorize
promotion. A supplied decision cannot override these failures. The shared token authenticates its
holder; the system does not prove that the request was manually entered by a particular person.

This is a boundary for the live promotion service. `build_merge_pack` still produces a review pack
without writing canonical Git data. Trusted repository imports (`allow_est=True`) copy existing
canonical records; public ingestion cannot set that flag. Direct database access and arbitrary
Python code remain trusted administrative capabilities, not public promotion endpoints.

Reproduce with `python -m pytest tests/test_promotion.py tests/test_contribute.py -q`.
The synthetic policy fixture exercises the real HTTP review/approval cycle, missing checks,
forged reports, evidence changes that preserve the numerical value, policy changes, expiry,
replay, and a concurrent candidate revision at the atomic write boundary. These are software
tests, not a policy that should be deployed to approve scientific claims. SQLite is exercised
locally; PostgreSQL uses its transaction API but requires a live database integration run.
