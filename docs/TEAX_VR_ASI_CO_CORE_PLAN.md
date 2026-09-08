# T€@X™–VR-ASI-CO core plan

Status: `SYM` architecture with `verification_type: software_test`.

This plan defines the new core independently of any physical conclusion. Raw observations are retained; hypotheses, derivations, reference models and verification remain separate layers.

## Core principle

The engine must not force discovery toward either an established answer or a preferred new answer. It preserves the full observation set, allows long exploratory jumps, then exposes every bridge for derivation and verification.

```text
RAW OBSERVATION (immutable)
        |
        +--> EXPLORE / PUZZLER
        |        |
        |        v
        |   candidate maps, geometry, frequency bands
        |        |
        +--> DERIVATION / MIRROR
        |        |
        |        v
        |   algebra, dimensions, inverse, invariants
        |        |
        +--> ODIN EYE / INDEPENDENT VERIFY
                 |
                 v
          PASS / OPEN / ERR / QUARANTINE
```

An unused observation is never silently deleted. It remains `OPEN` with an explicit reason. A verifier may reject a relation but may not erase the observation or the exploratory path that produced it.

## 12-speed dynamic core

The core is 12-speed rather than a fixed four-mode system. The speeds are control levels, not twelve theories. They can be mapped onto four broad families while preserving twelve distinct gears:

1. Capture: immutable raw observation and provenance.
2. Explore: free association and long A→Å candidate jumps.
3. Map: graph candidate relations without requiring acceptance.
4. Expand: dynamically split interesting frequency/geometry regions.
5. Hypothesis: turn a mapped path into explicit assumptions.
6. Derive: require explicit mathematical operators for each bridge.
7. Mirror: run forward/backward and dual representations.
8. Invariant: test declared conserved quantities and state integrity.
9. Challenge: generate counterexamples and competing explanations.
10. Strong Hypothesis: require discriminating predictions and held-out tests.
11. Independent Verify: verifier is blind to desired target where practical.
12. Promote/Quarantine: promotion requires evidence and policy gate; failures remain replayable.

Users may run Odin Eye continuously if they want, but continuous verification must annotate rather than destroy exploratory state. A failed intermediate bridge stays visible and learnable.

## Dynamic expansion by band and geometry

Do not prebuild every specialist kernel. Start with a minimal parent kernel and expand only where the data requires resolution.

```text
K0
 +-- band/region A --> K1A
 +-- band/region B --> K1B
 |                     +--> K2B1
 |                     +--> K2B2
 +-- geometry C -----> K1C
```

Each child receives an immutable input snapshot, parent hash, declared frequency/scale interval, geometry tags, resource budget and verifier contract. Children may be merged or retired, but their evidence remains content-addressed in the shadow ledger.

The expansion dimensions are intentionally generic. Candidate geometry tags may include local ring/torus, dual/mirror, shell/spiral, spring/helix and chamber/domain. These are model descriptors, not assumed physical facts.

## Retroactive remapping

When a better frame is discovered, old observations are not rewritten. The new frame produces a new derived view:

```text
O17 --frame-v1--> D17.v1
O17 --frame-v2--> D17.v2
```

This permits retrospective testing while preserving anti-post-hoc provenance. A frame discovered later can explain old held-out data, but the ledger records when the frame was created and which observations were visible at that time.

## Frequency-band specialization

A kernel may specialize to a frequency or scale band, but no preferred frequency is injected merely to obtain a match. Band discovery records:

- source sampling/clock provenance;
- band boundaries and resolution;
- transformation/window/filter used;
- candidate peaks and uncertainty;
- whether a target value was known before analysis;
- neighboring/null bands for comparison.

This lets the system distinguish discovery from target fitting.

## Canonical IR

```text
Observation {
  id, value, unit, dimension, uncertainty,
  provenance, observed_at, source_hash, status
}

Relation {
  relation_id, opcode, parameters,
  domain, codomain, assumptions,
  inverse_opcode?, provenance, prediction_phase
}

Frame {
  frame_id, parent_frame?, created_at,
  visible_observation_cutoff, geometry_tags,
  frequency_bounds?, assumptions
}

Kernel {
  kernel_id, parent_kernel?, frame_id,
  band_or_region, resource_budget,
  state, checkpoint_hash
}
```

Rust and Python mirror semantics and canonical serialization, not source-code length.

## Rust / Python split

Rust owns the bounded deterministic hot path: canonical IR, transforms, inverse operations, state machine, hashes, bounded queues and pressure valve. Python owns readable reference calculations, adapters, candidate generation, retrospective analysis and evidence reports.

Neither side may silently promote a candidate relation. `black_box` or similar optimization barriers are never correctness checks.

## Odin Eye

Odin Eye is a non-mutating observer. For a candidate relation it checks:

```text
y_rust = F_rust(x)
y_py   = F_python(x)
x_rust = Finv_rust(y_rust)
x_py   = Finv_python(y_py)
```

It checks dimensions/domain, forward equivalence, inverse closure, invariant preservation, provenance, edge cases, limits, resource bounds and prediction timing.

A perfect closure score is not automatically physical evidence. A suspiciously universal perfect result triggers a self-test to ensure the verifier is not merely verifying its own normalization.

## G normalized invariant

Where a model declares the normalized gravity/closure invariant, the reference is exact by definition:

```text
G_norm := 1.0000000
DeltaG := G_test - G_norm
```

`G_norm` is not the SI Newtonian gravitational constant. The core does not silently add an uncertainty to the defined reference. Numerical/meter uncertainty belongs to the measured or computed `G_test` and its provenance.

If a transformation unexpectedly changes a declared exact invariant, the branch is stopped/quarantined and replayed from the previous valid checkpoint. No post-hoc renormalization may hide the deviation.

## Shadow ledger and coverage

The shadow is cold/audit storage, not hidden executable authority. It retains raw evidence, long representations, traces, rejected paths, counterexamples and replay material.

Every run reports observation coverage:

```text
coverage = accounted_observations / original_observations
```

`accounted` includes USED, REJECTED-WITH-REASON and OPEN. Missing observations make the run `INCOMPLETE`; they are not treated as irrelevant by default.

## Pressure / entropy valve

Keep independent data and control lanes. Under overload or integrity failure:

```text
RUNNING -> THROTTLED -> BACKTRACKING -> ISOLATED
        -> MIRROR_VERIFY -> RECOVERY_PENDING
        -> independent ratification -> RUNNING
```

The external/network lane may be clipped while the core remains on the last verified checkpoint. Reconnection occurs only after integrity checks. A software clock is not labeled an analog measurement; a physical analog reference must name its hardware/sensor source.

## Independent verification and falsification

Standard/reference physics is a comparison model, not an automatic judge. Novel hypotheses receive the same mathematical checks as established models. Conversely, novelty is not evidence.

A strong hypothesis should produce a discriminating prediction:

```text
H_candidate -> P_A
H_reference -> P_B
P_A != P_B
```

The most useful next observation is one capable of distinguishing the predictions.

Statuses remain `EST`, `DER`, `HYP`, `STOP`, `ERR`, `SYM`. Software closure remains `verification_type: software_test` and cannot by itself establish a physical claim.

## Governed roles

Workflow: `teax-core-mirror-v1`.

- manager: routing/ledger only;
- reference-reader: read-only reference ingestion;
- rust-core: deterministic hot implementation;
- python-mirror: independent readable implementation;
- puzzler: exploratory candidate generation without promotion authority;
- odin-verifier: non-mutating differential/invariant verifier;
- resilience-verifier: overload, rollback, replay and recovery drills.

Retry is bounded to two attempts per immutable payload before quarantine/escalation. Human approval remains required for promotion, policy changes, external writes and new executable relation classes.

## Implementation order

Phase 0: freeze baseline, corpus, serialization and numeric policies.

Phase 1: implement canonical IR and minimal Rust/Python mirror kernel.

Phase 2: implement 12-speed controller, immutable observation coverage and non-mutating Odin Eye.

Phase 3: implement dynamic band/geometry kernel expansion and content-addressed shadow storage.

Phase 4: implement retrospective frame replay with visible-observation cutoffs and held-out tests.

Phase 5: connect pressure valve, isolation and durable recovery drills.

Phase 6: add governed workflow automation after three identical manual baselines.

Initial files:

```text
crates/teax-mirror-core/Cargo.toml
crates/teax-mirror-core/src/lib.rs
src/upi/teax_ir.py
src/upi/teax_reference.py
src/upi/teax_chamber.py
tests/test_teax_reference.py
tests/test_teax_resilience.py
examples/workflows/teax-core-mirror.workflow.json
.github/workflows/teax-core-mirror.yml
docs/TEAX_VR_ASI_CO_CORE.md
```

## Hard failure conditions

- Rust/Python semantic mismatch outside declared policy: `STOP` migration.
- Candidate alters verifier, policy or its own promotion path: `ERR`, quarantine.
- Raw observation disappears or is overwritten: `ERR` integrity failure.
- Declared invariant changes and is hidden by renormalization: `ERR`.
- Dynamic expansion exceeds bounded resource budget: throttle/isolate.
- Recovery cannot validate durable checkpoint history: no scheduled autonomy.
- Physical relation without independent provenance remains `HYP`/`SYM`.
