# Roadmap

Status of this document: `SYM` planning. Delivery claims below are software
milestones. They are `verification_type: software_test` unless a line explicitly
names experimental evidence. A green test does not establish physical truth.

The design unit is the **workflow**, not the number of bots. Every milestone
must keep the six invariants: owner, explicit state, durable artifact,
observable evidence, bounded retry, approval boundary. Missing any of these is
`STOP`.

```text
Chat → Role → Skill → Routine → Team → Governed system
```

Index triage is a weekly heartbeat. Public ingest is a gathering layer.
Canonical science remains `data/` in git until a merge workflow exists.

## Current: v1.0.0 (software)

Implemented as software under this tree. Experimental physics review is still
outside the project.

## Was: v0.1.0-alpha

In the tree today (`EST` as software, not as a released package index):

- Typed status model: EST, DER, HYP, STOP, ERR, SYM
- Node / bridge / theory schemas and CLI validation
- Physics helpers and dual-observer trace (narrow, documented limits)
- `upi debug-index` / `upi triage` with a known-finding catalog
- Governed-workflow contracts (ledger, handoff, skill, routine)
- Public contribution UI, SQLite or PostgreSQL, SSE
- Remote LLM system prompt and `upi-batch.json` check/insert
- Seed node `UPI<symbolic,1,memory,dna_minne_7.834>` (`SYM`)

Known gaps that are **not** closed by being listed here:

| Gap | Status |
|---|---|
| Live DB and `data/` are two sources of truth | `STOP` |
| Almost no bridges in `data/` | `STOP` |
| `UPIGraph` is RAM-only; not loaded from files | `STOP` |
| `UPI-E007` on `eight_hz.json` and `newtonian.json` | `ERR` |
| Source manifests are not UPI records | `STOP` |
| Public EST, identity, rate limits, record revision | `STOP` |
| Durable queue, sandbox, signed ledger, 24/7 | `STOP` |
| Uncertainty / dimension / evidence-weight code | `STOP` |
| HYP→EST promotion path | `STOP` |

## v0.2.0 — Canonical graph and honest ingest

**Theme:** one scientific source of truth. Live writes stay untrusted until
reviewed.

### 0.2.1 Canonical merge (next)

Workflow `canonical-merge-v1`:

```text
live DB / upi-batch.json
  → check (no write to data/)
  → independent verifier
  → maintainer approval
  → merge-pack + optional git PR
```

- Owner: human maintainer. LLM maps and saves files only.
- States: `QUEUED → CHECKED → APPROVED|REJECTED → MERGED`
- Artifact: `upi-merge-pack.json` (addresses, hashes, decision)
- Evidence: schema, boundary codes, `upi triage` against the known catalog
- Retry: max 2, then escalate
- Approval: required before any `data/` write

Specialist added only if tools differ: `canonical-reviewer` (git/PR), not another
scanner.

### 0.2.2 Graph as the index

- Load nodes and bridges from `data/` into `UPIGraph`
- Add real bridges between established records (DERIVED_FROM, MEASURED_BY, STOPS_AT)
- Export/import that round-trips without truncating fields
- Graph consistency check in CI

### 0.2.3 Hypothesis registry

- Enumerable HYP list with falsification, predicted observation, and testability
- No silent promotion. Status changes are review events.

### 0.2.4 Close cataloged errors

- Give `eight_hz.json` and `newtonian.json` provenance, or downgrade status
- Keep intentional `invalid_*` fixtures out of the approval catalog
- Decide whether `data/sources/*` stay manifests or become STOP nodes

### 0.2.5 Narrow physics quality

- Uncertainty propagation for declared quantities (`docs/UNCERTAINTY.md`)
- Dimensional consistency checks where units are present
- Still not experimental verification

**Out of 0.2:** visualization, CrokPedia, 24/7 agents, inbox/calendar.

## v0.3.0 — Evidence, revision, identity of claims

- Evidence aggregation with visible weights (`docs/ENSEMBLE_EVIDENCE.md`)
- Source-independence and duplication penalty
- Revision graph: `replaces` / `superseded_by` / content hash per revision
- Provenance fields as used in `docs/PROVENANCE.md` (DOI, arXiv, source_status)
- CrokPedia remains an optional consumer of JSON seams, not a runtime
  (`docs/CROKPEDIA_INTEGRATION.md`)
- Quarantine store for rejected or hostile batches (content-addressed, no exec)

**Out of 0.3:** treating ensemble scores as EST.

## v0.4.0 — Observation surfaces

- Read API with OpenAPI for the live store (already partially present as
  `/api/nodes`, `/api/ingest`, `/api/events`)
- Conflict dashboard from inspector shadow/mirror groups
- Dependency graph view driven by real bridges, not layout decoration
- Search and filter by status, domain, address
- Identity and rate limits on public POST
- Record update/supersede instead of insert-only

**Out of 0.4:** a second product UI, secret orchestrators, EST from the public form.

## v1.0.0 — Stable scientific contract

- Frozen schema with a published migration policy
- Documented review that can promote HYP→EST under named evidence rules
- Validated reference dataset (established core + STOP problems)
- Reproducible releases (sdist/wheel, changelog, citation)
- Recovery drills for the weekly triage routine
- Security policy updated to match the actual HTTP surface

v1.0 does **not** mean Theory of Everything, peer-review replacement, or a
universal 7.834/8 Hz constant.

## Explicit non-goals (until named otherwise)

- Autonomous agent runtime or 24/7 “OS”
- Medical or biological claims from dna_minne / Vortex-DNA (`SYM` only)
- Executing indexed remote content
- All-to-all agent chat as a substitute for ledgers
- Parallel workers without a merge rule and a verifier

## Decision rule for later additions

Add a manager only when routing is the bottleneck (it is, for live→canonical).
Add a specialist only when tools or permissions differ.
Add parallelism only when artifacts are separate.
Prefer an honest `STOP` over an unsupported milestone.
