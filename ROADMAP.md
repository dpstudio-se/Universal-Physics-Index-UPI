# Roadmap

Status of this document: `SYM` planning. Delivery claims below are software
milestones. They are `verification_type: software_test` unless a line explicitly
names experimental evidence. A green test does not close a physics `STOP`.

Prefer an honest `STOP` over an unsupported milestone.

## Current: v1.0.0 (software)

Implemented and frozen under this tree for the **gathering and validation**
layers. Experimental physics review remains outside the project.

Shipped (see [`CHANGELOG.md`](CHANGELOG.md)):

- Canonical graph load from `data/` into `UPIGraph` (`upi graph`, `load_graph`)
- Typed bridges in `data/bridges/` (closed relation set)
- Hypothesis registry, merge-check review pack, human approval gate
- Live search, rate limit, quarantine, maintainer promote token
- Public contribute UI + OpenAPI; seed `dna_minne_7.834`
- Schema fields: `verification_type`, causation, domain guards
- Evidence on core examples (`eight_hz.json`, `newtonian.json`, …) — no open
  `UPI-E007` on those paths

## Honest open gaps (not closed by listing)

| Gap | Status | Note |
|---|---|---|
| Live DB and `data/` are two stores | `STOP` (by design) | Gather layer ≠ DNA until human merge |
| HYP → EST promotion path | `STOP` | Needs named evidence + human reviewer |
| Indaleko 160 TB payload identity | `STOP` | [`data/open-problems/`](data/open-problems/); issue #8 |
| AdS/CFT applied to observed sky | `STOP` | Domain: not asymptotic AdS |
| Experimental lab verification of ledger claims | `STOP` | Outside software contract |
| RNA explorer lag vs `main` | `DER` ops | Fix DNA/source, then redeploy; `main` wins |

### Closed since alpha (do not re-open as ERR)

| Former gap | Resolution |
|---|---|
| Almost no bridges in `data/` | Bridges present under `data/bridges/` |
| `UPIGraph` not loaded from files | `upi.index.load_graph` + CLI `upi graph` |
| `UPI-E007` on `eight_hz` / `newtonian` | Evidence + primary sources on nodes |
| Schema missing `verification_type` | Present in v1 schemas |

## Near-term software (still not physics)

- Keep merge-check + mirrors green; patch failures before features
- RNA pull/propose path stays proposal-only into review
- Document DNA/RNA surfaces when UI routes change (RNA tree, not this DNA clone)
- Indaleko: cite and map; **do not** ingest 160 TB or treat Arango as UPI store

## Out of scope (drop)

- Odin-as-host-OS, HFT/climate plant, Arango as canonical UPI DB
- Closing STOP by arithmetic, slider “alignment”, or elegance
- Treating `software_test` as `experimental_observation`
- Second ledger under RNA `catalog.json`

## Version policy

Breaking schema → new major. Additive optional fields → minor.
See [`docs/MIGRATION.md`](docs/MIGRATION.md).
