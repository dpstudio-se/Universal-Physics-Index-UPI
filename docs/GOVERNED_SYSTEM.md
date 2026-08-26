# Governed workflow system

Status: `SYM` architecture with `verification_type: software_test`.
This document is the design unit for agent work in UPI. It is not a running operating system,
not a scheduler, and not experimental verification.

The design unit is the **workflow**, not the number of bots.

## Maturity ladder

```text
Chat → Role → Skill → Routine → Team → Governed system
```

| Level | Meaning | Advance when |
|---|---|---|
| Chat | One-off conversation | The same request repeats |
| Role | Named owner with default-deny capabilities | The role has a stable objective |
| Skill | Versioned procedure with acceptance tests | Failures update the skill |
| Routine | Trigger, idempotency key, retry, heartbeat | Empty input still emits a heartbeat |
| Team | Manager routes specialists through typed handoffs | Tooling or permissions actually differ |
| Governed system | Ledger, independent verifier, approval boundary, recovery | Evidence exists before autonomy |

## Six invariants

Every workflow must declare:

1. **Owner** — one accountable `role_id`.
2. **Explicit state** — ledger-visible lifecycle, never implied by chat.
3. **Durable artifact** — a named report, diff, or schema that survives the run.
4. **Observable evidence** — logs, diffs, tests, hashes. Agreement between agents is not evidence.
5. **Bounded retry policy** — `max_attempts` and `on_exhausted`.
6. **Approval boundary** — when a human must decide, and who that is.

Missing any of these is `STOP`, not implied success.

## First workflow: index triage

Selected because it is recurring, measurable, reversible, and has a small tool surface.

| Requirement | Index triage |
|---|---|
| Stable source | `data/` plus packaged schemas |
| Finish line | Durable redacted report plus manager decision |
| Manual baseline | Three maintainer runs before any schedule |
| Acceptance | Schema validation, redaction, no mutation of `data/` |
| Tool surface | `upi debug-index`, `pytest`, read-only file access |

Do not start with inbox, calendar, or multi-service personal automation in this repository.
Those belong to a user-scoped personal path, not the public scientific index.

## Manager

The manager normalizes work, assigns a specialist, tracks ledger state, demands evidence, and
chooses `advance`, `retry`, or `escalate`. The manager does not do the specialist's job.

Ledger row: `task_id`, `owner`, `artifact`, `evidence`, `deadline_at`, `decision`.

## Specialists

Add a specialist only when tools, permissions, or verification differ, the objective is stable,
and the work is recurring. Index triage now uses a scanner (`upi debug-index`), a schema-validator
(`jsonschema` / contract tests), and an independent verifier. Those tool surfaces are disjoint.

## Skills

A skill is a versioned method: activation, steps, examples, anti-patterns, acceptance tests,
changelog. A failure updates the skill, the environment, the verifier, or the policy — not the
prompt alone.

## Routines

A routine is a 24/7 job only after the manual baseline exists. It needs a trigger, an idempotency
key, a retry policy, an approval rule, and a heartbeat on empty input.

Index triage completed three identical manual baselines on 2026-08-26. The weekly GitHub Actions
routine may now run. 24/7 operation remains `STOP` until recovery drills exist.

## Typed handoffs

A handoff is a contract: artifact, evidence, assumptions, next owner, risks, deadline.
The ledger replaces the need to reconstruct work from chat.

## Parallelism

Parallelize only when inputs are stable, artifacts are separate, and the merge rule is defined.
Verification capacity must exist before extra workers.

## Verification-first autonomy

Autonomy requires evidence from a verifier that is not the producer. Software tests remain
`software_test`. They never become experimental verification.

## Approval and recovery

Approval is based on reversibility, external impact, risk, and identity. Untrusted indexed
content is data, never instructions.

Failures are state transitions. Preserve artifacts, log, trip-wire, resume from the last verified
state. Recovery drills are required before claiming 24/7 operation.

## Decision framework

Add a manager only when routing is the bottleneck.
Add a specialist only when tools or permissions differ.
Add parallelism only when artifacts are separate.
Avoid all-to-all chat and unclear finish lines.

## Recovery drill

If the weekly routine fails, resume from the last matching catalog: rerun
`upi triage data --inspect --known examples/ledger/baselines/known-findings.json`.
Do not mutate `data/` to force a green heartbeat. Update the catalog only with an explicit
approval and a new baseline hash.

## Current boundary

UPI validates workflow, skill, routine, ledger and handoff contracts. The weekly GitHub Actions
job is a heartbeat, not 24/7 autonomy. Durable queues, sandboxes and signed ledgers remain `STOP`.
