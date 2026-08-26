# Index triage baseline campaign

Status: `SYM`  
`verification_type: software_test`

## Runs

| Run | Command | Artifact hash |
|---|---|---|
| 1 | `upi debug-index data --inspect` | `af2fabe022813f16582d4c04b4466f30d594d98e95e312a1ee23f25859bba694` |
| 2 | `upi debug-index data --inspect` | `af2fabe022813f16582d4c04b4466f30d594d98e95e312a1ee23f25859bba694` |
| 3 | `upi debug-index data --inspect` | `af2fabe022813f16582d4c04b4466f30d594d98e95e312a1ee23f25859bba694` |

Finish line: three identical redacted reports, no scanner mutation of `data/`.

## Independent verification

- Reports set `verification_type` to `software_test` and `source_values_redacted` to true.
- `pytest tests/test_triage.py tests/test_governed_system.py` is the verifier evidence.
- Scanner and verifier are separate: debug-index produced the report; tests compared it to the catalog.

## Catalog classes

| Class | Meaning | Approval |
|---|---|---|
| `negative_fixture` | Intentional invalid record | Expected |
| `source_manifest` | Not a node/bridge/theory | Expected `STOP` |
| `provenance_gap` | EST/theory record missing evidence provenance | Known, not closed |

## Manager decision

`advance` the baseline campaign. Remaining provenance gaps stay in the catalog until a human edits those records. New findings fail the routine.
