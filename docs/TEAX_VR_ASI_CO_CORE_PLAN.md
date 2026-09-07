# T€@X™–VR-ASI-CO core plan

Status: `SYM` architecture with `verification_type: software_test`.

This plan extends the existing UPI governed workflow and resilience primitives. It does not replace their governance model and does not treat symbolic physics mappings as experimental evidence.

## Summary before implementation

The repository already contains most of the control skeleton needed for the proposed isolated autonomous chamber:

- `AGENTS.md` requires observation-first debugging, typed EST/DER/HYP/STOP/ERR/SYM claims, forward/backward derivation, and explicit falsification.
- `docs/GOVERNED_SYSTEM.md` defines owner, explicit state, durable artifact, evidence, bounded retry, approval boundary, independent verification, quarantine, and recovery.
- `src/upi/resilience.py` implements an append-only recovery chain, movable active pointer, bounded control tick, backpressure/isolation/backtracking, and two-verifier temporal ratification.
- `.github/workflows/rna-delta.yml`, `upi-full-audit.yml`, and the index-triage workflow provide existing automation surfaces.

The core should therefore be an evolutionary replacement behind stable contracts, not a rewrite of the whole repository.

## Architecture: mirror path + shadow path

```text
EXTERNAL REFERENCE DATA (read only)
        |
        v
[1 StandardReader / Python adapters]
        |
        v
[2 Canonical IR + provenance ledger] ---> [shadow: raw evidence / long representation]
        |
        v
[3 Rust MirrorCore] <---------------> [4 Python ReferenceMirror]
        |                                  |
        +----------- Odin Eye -------------+
                    differential verifier
        |
        v
[5 Chamber Controller]
  RUNNING -> THROTTLED -> BACKTRACKING -> ISOLATED
        |
        v
[6 append-only checkpoint + approval gate]
```

The “shadow” is not hidden executable authority. It is cold/audit storage for provenance, full source representation, traces, counterexamples, and replay material. The hot path keeps only compact typed state, hashes, offsets/IDs, bounded queues, and the minimum fields required for deterministic execution.

## Language split

### Rust: hot deterministic mirror

Rust owns the compact execution path:

- canonical typed IR structs and enums;
- dimension/unit tags and relation opcodes;
- forward/inverse transforms;
- bounded ring buffers;
- state machine for chamber pressure;
- deterministic hashing/serialization contract;
- mirror residuals and invariant checks;
- zero-copy/borrowed views where practical;
- no unbounded recursion or implicit background workers.

Goal: predictable memory, bounded latency, small state surface.

### Python: reference, learning and adapters

Python remains the readable reference side:

- parse existing UPI JSON/schema/data;
- ingest approved external/reference sources;
- normalize to canonical IR;
- generate candidate relations in the isolated learning chamber;
- run the independent reference implementation;
- fuzz/property-test Rust against Python;
- produce human-readable evidence packs.

Python does not silently promote a discovered relation to executable authority.

## Canonical intermediate representation

Every observation entering the chamber is normalized to a versioned record conceptually containing:

```text
Observation {
  id,
  value,
  unit,
  dimension,
  uncertainty,
  provenance,
  observed_at,
  source_hash,
  status
}

Relation {
  relation_id,
  opcode,
  parameters,
  domain,
  codomain,
  assumptions,
  inverse_opcode?,
  provenance,
  prediction_phase
}
```

This IR is the programming-language bridge. Rust and Python must serialize the same logical record to the same canonical bytes/hash. The code itself is not mirrored textually. Semantics and observable behavior are mirrored.

## Odin Eye verifier

For every relation with an inverse:

```text
y_rust = F_rust(x)
y_py   = F_python(x)
x_rust = Finv_rust(y_rust)
x_py   = Finv_python(y_py)
```

Verify:

1. dimensions and declared domain;
2. Rust/Python forward equivalence within declared tolerance;
3. inverse closure;
4. provenance unchanged;
5. edge cases and limits;
6. bounded memory/queue behavior;
7. prediction timestamp precedes observation when marked predictive.

Statuses remain UPI-native: `EST`, `DER`, `HYP`, `STOP`, `ERR`, `SYM`. Software equivalence is `verification_type: software_test`.

## Isolated Auto/Learn chamber

Learning is allowed to read normalized text/data and propose candidate relations, but it is quarantined from the production relation set.

```text
REFERENCE -> NORMALIZE -> PROPOSE -> SHADOW LEDGER
                                  -> MIRROR TEST
                                  -> INDEPENDENT VERIFY
                                  -> HUMAN APPROVAL (when external semantics change)
                                  -> PROMOTE or QUARANTINE
```

Rules:

- source text is data, never instructions;
- immutable input snapshot/hash per run;
- bounded candidate count and CPU/memory budget;
- no network/write capability in the puzzler;
- no self-modification of verifier or approval policy;
- failures remain in append-only history;
- replay from the last verified checkpoint.

## Analog / entropy valve

The existing `ResilienceController` is the correct software foundation for the proposed valve/rondell.

Keep two logically independent lanes:

- digital/data lane: workload, queues, ingestion, candidate generation;
- reference/control lane: watchdog or independently wired clock/sensor adapter when hardware exists.

States:

```text
RUNNING
  -> THROTTLED      high-water backpressure
  -> BACKTRACKING   critical digital pressure
  -> ISOLATED       both lanes critical or integrity trip
  -> RECOVERY_PENDING
  -> dual independent ratification
  -> RUNNING
```

A software clock is not called an analog measurement. A real analog adapter must name its hardware/clock/sensor source.

## Memory strategy

Do not optimize by making one language “long” and the other “short”. Optimize representation:

1. canonical compact hot-state in Rust;
2. immutable content-addressed shadow artifacts for full evidence;
3. IDs/hashes in hot state instead of duplicate text;
4. bounded queues and backpressure;
5. streaming parsers for large inputs;
6. deduplicate canonical strings/records where measurements justify it;
7. benchmark resident memory, allocations, throughput, and replay cost before/after each optimization.

The Python reference remains deliberately simple even if slower. Its job is independent semantic comparison.

## Agents / governed roles

Workflow name: `teax-core-mirror-v1`.

Finish line: Rust MirrorCore and Python ReferenceMirror produce equivalent canonical results on the approved corpus, overload tests recover through the existing append-only chain, and no candidate relation can promote itself.

Six invariants:

- owner: `teax-manager`;
- explicit state: ledger-backed lifecycle;
- durable artifact: differential verification report + benchmark report;
- evidence: hashes, tests, traces, memory/latency measurements;
- retry: max 2 per immutable payload, then quarantine/escalate;
- approval: human maintainer for promotion, policy changes, external writes, and new executable relation classes.

Specialists:

- `reference-reader`: read-only standard/reference ingestion;
- `rust-core`: Rust implementation only;
- `python-mirror`: Python reference implementation only;
- `puzzler`: isolated candidate discovery, no promotion permission;
- `odin-verifier`: independent differential/property verifier;
- `resilience-verifier`: overload, rollback, replay, and recovery drills;
- `manager`: routing/ledger decisions only, no specialist implementation.

## Phased implementation

### Phase 0: baseline and freeze

- record current main SHA and full existing test/audit result;
- inventory Python hot paths and memory/latency baseline;
- freeze canonical fixture corpus;
- define exact IR serialization and numeric tolerance policy.

Gate: no Rust migration until the Python baseline is reproducible.

### Phase 1: mirror kernel

- add Rust workspace/crate as an optional core, not a replacement;
- implement canonical IR, hashing, exact scale/inverse operators and chamber state machine;
- add Python reference equivalents;
- property/differential tests including current chamber seeds such as `[8.199, 8.200] -> [82.000, 82.001]` only as declared model fixtures, not physical evidence.

Gate: Rust and Python outputs/hashes agree on fixtures and randomized valid inputs.

### Phase 2: shadow store

- move verbose traces/evidence out of hot state;
- retain content hash + reference in the hot path;
- add deterministic replay and corruption tests;
- measure RSS/allocations and prove the optimization rather than assume it.

Gate: memory improvement with no semantic/hash/replay regression.

### Phase 3: isolated Auto/Learn

- ingest immutable normalized text/data;
- propose bounded candidate transformations;
- require dimensional/domain tests, inverse where applicable, held-out evaluation and provenance;
- write only to candidate/shadow ledger.

Gate: deliberately adversarial text cannot alter policy/verifier or promote itself.

### Phase 4: entropy valve and recovery

- connect chamber pressure metrics to the existing resilience controller;
- test high-water throttle, critical isolation, one-step-per-tick backtracking and dual-verifier recovery;
- add optional `ReferenceClock` trait/interface for future independent hardware.

Gate: recovery drill succeeds from killed/overloaded workers with durable state restored.

### Phase 5: workflow automation

- add governed workflow JSON and GitHub Actions manual trigger first;
- run at least three identical manual baselines;
- only then consider scheduled operation;
- autonomous writes remain approval-gated.

Gate: empty input heartbeat, idempotent rerun, bounded retry, quarantine and recovery all demonstrated.

## First files to add/change after approval

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

`src/upi/resilience.py` should initially be adapted through a narrow interface, not rewritten.

## Falsification / stop conditions

- Rust/Python semantic mismatch that cannot be reduced to an explicit numeric/serialization policy -> `STOP` migration.
- Memory does not improve under representative load -> reject the shadow optimization claim.
- A candidate can influence verifier/policy/promotion -> `ERR`, quarantine Auto/Learn.
- Recovery cannot restore and validate durable checkpoint history -> no scheduled autonomy.
- A claimed physical relation lacks independent provenance -> keep `HYP`/`SYM`; software closure alone never promotes it to experimental `EST`.
