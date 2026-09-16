# UPI Workload Loop v1

Purpose: provide a bounded, auditable workload splitter for research threads. This document maps observations into domain chambers, applies bidirectional review, and routes unresolved work without promoting symbolic patterns to scientific fact.

## Pipeline

```text
CHAT
 -> EXTRACT
 -> CLASSIFY
 -> DOMAIN CHAMBERS
 -> MIRROR (A -> O and O -> A)
 -> VERIFY
 -> LOOP CHECK
```

## A — Extract

Split source material into:

- physics
- mathematics
- signal/frequency
- law / TF1766
- history
- music/audio
- system architecture
- hypotheses

Preserve the original source and provenance. Do not discard failed branches.

## B — Classify

Use the existing UPI scientific statuses exactly:

- `EST`: established within the declared domain
- `DER`: derived from specified facts and assumptions
- `HYP`: falsifiable hypothesis awaiting verification
- `STOP`: named proof, mechanism or observation is missing
- `ERR`: invalid, contradicted or superseded
- `SYM`: symbolic interpretation or analogy

Workflow states such as `OPEN`, `TEST`, `PASS`, `FAIL` and `CONFLICT` remain separate from scientific status.

## C — Domain chambers

Use typed domain buckets. Initial chambers from the current research thread:

- `0K`: total/reference origin
- `0W`: dynamic reference point
- `0C`: coherence/cycle reference
- spacetime
- flow / Navier–Stokes
- frequency / signal
- information
- energy / mass
- network / orchestration
- law / TF1766
- history
- music / audio
- biology
- AI

A domain label is organizational metadata, not a scientific claim.

## D — Mirror

Every nontrivial relation should be checked in both orientations where mathematically meaningful:

```text
A -> O
O -> A
```

For an involution `M`, require `M(M(x)) = x` when that is part of the proposed model. For non-invertible operations, replace inverse closure with provenance-preserving forward validation.

Do not force a loop when the evidence supports a tree, disconnected graph, or another topology.

## E — Verify

Run the strongest applicable checks:

1. symbolic consistency
2. mathematical algebra / closure
3. dimensional consistency and unit typing
4. established-domain physics
5. historical source verification
6. legal text and explicit cross-reference verification
7. signal/audio measurement when actual signal data is available
8. falsification/null-model checks

Software verification applies only to the tested computation. It does not establish experimental physics.

## F — Loop check

```text
NEW NODE       -> add versioned candidate
CONFLICT       -> retain both branches; add discriminating test
EXISTING NODE  -> reuse exact record and provenance
NO NEW INFO    -> STOP / close cycle
```

Coverage invariant for recursive splitting:

`coverage(parent) == union(coverage(children))`

for the declared workload partition.

Provenance invariant:

`provenance(parent) ⊆ union(provenance(children))`

No child may silently lose its source, assumptions, or status.

## Dynamic workload

A workload may expand recursively:

`W -> {W1, W2, ..., Wn}`

and rejoin into a report without deleting history. Repartition only when a new distinction, dependency, contradiction, or verification requirement is discovered.

## Current research-thread mappings

The following remain candidates unless independently supported:

- dynamic scale / local reference points
- frequency candidates `7.834`, `8`, `21.6`, `1.45798`, `0.145798`
- frequency mirroring such as `M(k)=81/k`
- Taurus / toroidal closure
- biological structural analogies
- music/orkestra as network architecture
- TF1766 as a transparency/verifiability model
- CREED as provenance/origin metadata

Do not promote these to `EST` merely because they form elegant numerical or structural correspondences.

## Required research loop

```text
load verified previous state
preserve raw observation
extract candidate claims
classify each claim
split into domain chambers
mirror where valid
run symbolic checks
run mathematical checks
run dimensional checks
run domain tests
run falsification path
retain conflicts and STOPs
reassemble with provenance
compare against previous state
if changed: create next workload frontier
if unchanged: stop this cycle
```

This workflow is an orchestration specification. It does not itself create a scheduler, worker daemon, or scientific proof.