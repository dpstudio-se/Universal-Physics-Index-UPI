# Astra ↔ UPI feedback loop

This document defines the repository-side meeting point for Astra and UPI.

## Purpose

The loop lets Astra return analysis to the repository, lets UPI validate that packet against repository rules, and then sends the resulting repository state back to Astra on the next cycle.

It is a coordination protocol. It does not make Astra an independent scientific authority and does not make UPI infallible.

## Cycle

```text
Astra observation
    ↓
A: implementation expectation
    +
B: UPI/evidence requirement
    ↓
mirror comparison
    ↓
checks + provenance + invariants
    ↓
ASTRA-UPI-LOOP packet
    ↓
GitHub branch / PR
    ↓
review + governed merge
    ↓
new repository HEAD
    ↓
Astra reads new HEAD
    ↺
```

## Durable handshake

The machine-readable contract is `schemas/astra-feedback.schema.json`.

The canonical Astra-facing protocol is `prompts/astra-upi-feedback-loop.system.md`.

Every packet identifies the repository state with `base_sha` and the proposal with `proposal_sha256`.

## Existing UPI connection points

- `src/upi/feedback.py` already implements fail-closed A/B review, provenance integrity, mirror comparison, explicit human direction and a human-review gate.
- `tests/test_feedback.py` verifies agreement, conflict, provenance failure, missing checks, invalid checks, non-finite values and the no-promotion boundary.
- `.github/workflows/rna-delta.yml` exposes changes in canonical DNA data as an RNA-facing delta report.
- `.grok/workflows/index-triage.rhai` already follows specialist → independent verifier → durable report.
- `AGENTS.md` defines the Astra/UPI bidirectional verification loop and requires the return path to evidence and human review.

## Boundary

A passing software check means the software check passed. It does not promote a physical claim.

Canonical `data/` remains behind the normal validation and human-review path.

## Re-entry

After merge, Astra must not continue from an old cached state. It must read the new repository HEAD, rerun affected checks and produce a new A/B mirror.

That makes Git history the spine of the feedback loop.
