# UPI Mirror-Bridge Verification Loop

Status: SYM architecture; software verification only.

## Purpose

Connect the existing mirror verification, provenance, shadow, feedback, workflow, skill, routine, and typed-bridge layers into one reusable loop.

```text
SOURCE
  ↓
PROVENANCE
  ↓
PRIMARY ANALYSIS A
  ↓
BRIDGE B
  ↓
INDEPENDENT MIRROR M
  ↓
COMPARE / DELTA
  ↓
CLASSIFY
  ├─ AGREE → NEXT BRIDGE
  ├─ CONFLICT → STOP / REVIEW
  └─ UNKNOWN → NEXT OBSERVATION
  ↓
DURABLE REPORT
  ↓
NEXT POINTER
  ↺
```

## Dual-strand routing

The loop can be multiplexed as two logical strands without requiring two independent schedulers:

- Strand A: source, implementation expectation, primary derivation.
- Strand B: evidence-only derivation, mirror, independent checks.
- Bridge: transfers only a typed handoff containing artifact identity, hashes, assumptions, quantities, status, and next observation.
- Shadow: retains conflicts, alternative reconstructions, missing information, and discarded candidates without promoting them.

The strands must not silently share the expected answer. The mirror derivation receives evidence, not A.

## Typed bridge

A bridge is a graph relation between UPI nodes. Use `schemas/bridge.schema.json` and preserve one of its declared relations. A bridge is valid only when its source and target are addressable and its status is explicit.

Recommended bridge payload:

```text
source → target
relation
status
evidence[]
assumptions[]
equations[]
mechanism
confusion_guard
```

`LINKED != MERGED`. A bridge records a relation; it does not establish that two domains are the same physical mechanism.

## Mirror gate

For quantities in the same unit and domain:

```text
Δ = A - M(A)
```

and

```text
AGREE iff |Δ| ≤ declared tolerance
CONFLICT iff |Δ| > declared tolerance
UNKNOWN iff evidence, units, domain, or required checks are missing
```

The existing `upi.feedback.review_node` already implements this fail-closed gate, provenance integrity, required checks, and a human-review boundary.

## Re-entry

After a governed merge, the next cycle must read the new repository HEAD. It must not reuse a stale cached state. The durable artifact and next pointer therefore form the bridge between cycles.

## Failure routing

```text
CONFLICT → STOP → human review → revised proposal or new observation
UNKNOWN  → STOP/REVIEW → missing evidence/check → rerun
PASS     → durable report → next typed bridge
```

A software PASS is never promoted to experimental or physical verification.

## Scope boundary

The loop is an operational verification architecture. It does not prove Ω1766, a universal double-helix field, or any other physical hypothesis. Physical claims require independent data, declared predictions, uncertainty analysis, null models, and reproducible tests.

## Existing connections

- `src/upi/feedback.py`: executable mirror/provenance gate.
- `tests/test_feedback.py`: regression coverage for agreement, conflict, provenance failure, missing checks and no-promotion.
- `schemas/bridge.schema.json`: typed graph bridge.
- `docs/ASTRA_UPI_FEEDBACK_LOOP.md`: repository re-entry.
- `docs/UNIVERS_OCR.md`: source → provenance → decode → mirror → cross-verify.
- `docs/GOVERNED_SYSTEM.md`: workflow, durable artifact, verifier and approval boundary.
- `schemas/skill.schema.json` and `schemas/routine.schema.json`: operational contracts.

## Status

This document closes the architectural connection between those existing components. It remains SYM until the corresponding workflow/skill/routine examples and their software tests are validated together.
