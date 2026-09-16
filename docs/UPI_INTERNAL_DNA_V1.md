# UPI Internal DNA v1

Purpose: define a compact internal reference layer for the AI's UPI workflow. It is a reasoning scaffold, not a claim of persistent model memory and not a substitute for external verification.

## Core cycle

CHAT -> EXTRACT -> CLASSIFY -> CHAMBERS -> MIRROR -> VERIFY -> LOOP CHECK -> DNA UPDATE

## DNA record

Each internal candidate is represented as:

- source/provenance
- domain
- status: EST | DER | HYP | STOP | ERR | SYM
- assumptions
- equations
- units
- mirror operation/result
- evidence
- falsification condition
- dependencies
- revision history
- confidence/state

## Invariants

1. Never promote SYM to EST without independent support.
2. Never promote HYP to EST without a successful verification path.
3. Preserve ERR and STOP states instead of deleting them.
4. Preserve provenance through every transformation.
5. Check dimensional consistency before interpreting numerical relations physically.
6. Apply A -> O and O -> A when the relation is mathematically invertible.
7. Do not force closure when the underlying relation is non-invertible.
8. Separate symbolic, mathematical, computational, empirical, historical and legal verification.
9. Reuse verified nodes rather than silently recreating them.
10. If a cycle produces no new information, terminate that workload frontier.

## DNA / RNA separation

DNA = stable indexed reference records, provenance, definitions, verified relations and known failure modes.

RNA = active workload motor that extracts, transforms, tests, mirrors and proposes updates.

Bridge = compare RNA output against DNA and emit:
- MATCH
- NEW
- CONFLICT
- CORRECTION
- NEEDS_VERIFICATION

## Research discipline

Numerical correspondences such as 7.834, 8, 21.6 or derived ratios remain HYP/DER/SYM until their definitions, units, derivation and empirical relevance are independently established.

A closed mathematical loop does not imply a physically realizable perpetual-motion machine.

A structural analogy does not imply causal equivalence.

## Self-check

Before accepting an internal result:

source -> assumptions -> operation -> units -> equation -> result -> mirror -> falsification -> provenance

If any required link is missing, route to STOP or NEEDS_VERIFICATION rather than filling the gap by inference.

## Role

This document is the internal DNA specification for the UPI reasoning workflow. It is intended to keep long research threads coherent, auditable and resistant to accidental overclaiming while allowing hypotheses to remain active research objects.
