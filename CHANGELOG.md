# Changelog

All notable changes are documented here.

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
- Typed status, frequency, quantity, uncertainty, provenance and audit models.
- Machine-readable validation issues `UPI-E001` through `UPI-E010`.
- Falsification, symbolic-boundary and configurable-normalization safeguards.
- Validation, inspection, conversion, discovery, schema and version CLI commands.
- Scientific-boundary documentation, Swedish overview and JSON examples.
- Functional DNA and Vortex-DNA symbolic collaboration architecture.
- Boundary validation for reference frames, normalization claims, causation and verification type.
