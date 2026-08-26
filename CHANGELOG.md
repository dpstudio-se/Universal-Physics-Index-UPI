# Changelog

All notable changes are documented here.

## 1.0.0

Software contract freeze for the gathering and validation layers.

- Canonical graph load from `data/`, typed bridges, hypothesis registry
- Canonical merge-check pack (`upi merge-check`) with human approval required
- Uncertainty helper, dimension check, visible evidence weights, quarantine store
- Live search, rate limit, supersede, maintainer promote token
- OpenAPI for the live API, migration policy, triage recovery drill
- Provenance on 8 Hz and Newtonian records; source manifests skipped by debug-index

## Unreleased

### Changed

- Public repository layout now follows a standard Python `src/` package, with private product scaffolding removed.
- Consistency inspection uses `--inspect` / `inspect=True` instead of a private product name.

### Removed

- Internal orchestrator, simulator, plugin, port, and environment files that belonged to a separate product.
- Duplicate license and JavaScript lint configuration that did not apply to this Python project.

### Added

- Governed-workflow contracts: six invariants, ledger, typed handoff, skill, routine.
- First reversible workflow: index triage, with manager / scanner / independent verifier.
- Three identical index-triage baselines, known-finding catalog, weekly routine, and schema-validator specialist.
- Public contribution UI with live SQLite/PostgreSQL store and `dna_minne_7.834` seed.
- Remote LLM system prompt plus check/insert for `upi-batch.json` files.
- Typed status, frequency, quantity, uncertainty, provenance and audit models.
- Machine-readable validation issues `UPI-E001` through `UPI-E010`.
- Falsification, symbolic-boundary and configurable-normalization safeguards.
- Validation, inspection, conversion, discovery, schema and version CLI commands.
- Scientific-boundary documentation, Swedish overview and JSON examples.
- Functional DNA and Vortex-DNA symbolic collaboration architecture.
- Boundary validation for reference frames, normalization claims, causation and verification type.
