# Changelog

All notable changes are documented here.

## 1.0.0

Software contract freeze for the gathering and validation layers.

- Canonical graph load from `data/`, typed bridges, hypothesis registry
- `upi merge-check` review pack with human approval gate
- Live search, rate limit, supersede, maintainer promote token
- Public contribute UI, OpenAPI, seed `dna_minne_7.834`
- Schema: `verification_type`, causation, domain guards
- Debug-index skips source manifests; quarantine path for hostile payloads

## Unreleased

### Documentation

- Synced README / README.sv / ROADMAP / ARCHITECTURE to the v1.0.0 main contract:
  DNA (`data/` on GitHub main) vs RNA (grok.me), closed software gaps no longer
  listed as open ERR, honest STOP table (Indaleko identity, promotion gate).

### Added

- `data/examples/rna_engine_ping.json` — SYM software_test ping from the RNA write path (not a physical claim).
- Information mass (HYP, T€@X 2026): an information-associated interpretation of the derived mass equivalent `m = h f / c^2`, with frequency-encoding assumption; no second mass symbol.
- Derived mass equivalent of a frequency quantum (DER): composition of `E = h f` and inertia of energy.
- Universal information measure (HYP): proposed dictionary frequency → m → geometric entropy → 11D brane, dual to AdS/CFT.
- Sub-Planck horizon STOP: Schwarzschild radius of laboratory `m = h f / c^2` is below `ℓ_P`.
- AdS spacetime (EST), CFT (EST), AdS/CFT correspondence (HYP, Maldacena 1997).
- Ryu–Takayanagi entanglement entropy (DER): `S_A = Area(γ_A)/4G_N`.
- Domain cut: our universe is not asymptotically AdS (STOP).
- Eleven-dimensional M-brane (SYM) and AdS4×S7 / ABJM as the M2 example.
- Bekenstein–Hawking horizon entropy (EST) as an area law, in-domain for `R >> ℓ_P`.
- Coding-theory cluster: E8, Leech Λ24, extended Golay G24, and QEC as a derived reading.
- Quantum-information cluster: Hilbert space, Born rule, qudit Weyl/Fourier, tensor register, torus search, classical resource STOP.

### Changed

- Bump `github/codeql-action/upload-sarif` to 4.37.9 (CI Trivy SARIF upload).
- Bump `actions/upload-artifact` to v7 (index-triage report upload).
- Planck–Einstein confusion guard no longer sneers at `m = h f / c^2`; it names photon rest mass (zero) versus the derived mass equivalent.
- Mass-energy record notes that `E = m c^2` is itself derived, and that applying it to radiation energy changes the referent of `m`.
- Public repository layout now follows a standard Python `src/` package, with private product scaffolding removed.
- Consistency inspection uses `--inspect` / `inspect=True` instead of a private product name.

### Removed

- Internal orchestrator, simulator, plugin, port, and environment files that belonged to a separate product.
- Duplicate license and JavaScript lint configuration that did not apply to this Python project.

### Added (1.0 gathering layer)

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
