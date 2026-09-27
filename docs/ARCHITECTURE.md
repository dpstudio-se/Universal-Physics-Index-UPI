# Architecture

Software version referenced here: **1.0.0** (gathering and validation freeze).
Status of prose that is not backed by a test: treat as `SYM` guidance unless a
section names a concrete module path.

## Address

The conceptual address `UPI<D,G,T,N>` separates domain/system (`D`), governing
relation or transformation context (`G`), evidence/status type (`T`) and
normalization/notation context (`N`).

Example: `UPI<symbolic,1,memory,dna_minne_7.834>` is a `SYM` memory coordinate,
not a biology claim.

## Layers (do not collapse)

| Layer | Authority | Path / surface |
|---|---|---|
| DNA | Canonical scientific index | GitHub `main` → `data/**/*.json` |
| Schemas | Shape + closed relation set | `schemas/`, `src/upi/validation.py` |
| Package | Load, validate, CLI, gather API | `src/upi/` |
| Live DB | Untrusted gathering only | SQLite/Postgres via `upi serve` / ingest |
| RNA | Explorer transcription + proposals | Deployed TanStack app (grok.me); not DNA |

Success in one layer does not prove another. A green `software_test` proves
software behavior only within its declared scope.

## Graph

- Nodes: `data/<domain>/*.json` (and established/theories/examples/…)
- Bridges: `data/bridges/*.json` with relations from the closed set
  (`DERIVED_FROM`, `STOPS_AT`, `MEASURED_BY`, `FORM_SIMILAR`, …)
- Load: `upi.index.load_graph` → `UPIGraph` (in-memory view of DNA files)
- Merge gate: `upi merge-check` — STOP without `stop_reason` fails; unknown keys fail

## Status and evidence

See [`STATUS_MODEL.md`](STATUS_MODEL.md) and [`ERROR_CODES.md`](ERROR_CODES.md).

- Weakest status on a chain wins
- `verification_type` and `claims_experimental_verification` are explicit
- Public writes cannot mint `EST`

## Information layers

`PRIVATE`, `PUBLIC`, `ACADEMIC` describe disclosure and formality, not evidence
strength. They must never replace scientific statuses. Functional DNA,
Vortex-DNA and collaboration docs are `SYM` process maps unless a claim is
separately labeled EST/DER/HYP/STOP.

## Governed work

The workflow is the design unit; see [`GOVERNED_SYSTEM.md`](GOVERNED_SYSTEM.md).
Agent hard stops and DNA/RNA rules:
[`VSCODE_AGENT_PROMPT.md`](VSCODE_AGENT_PROMPT.md).
