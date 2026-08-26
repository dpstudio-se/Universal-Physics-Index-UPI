# Index triage baseline campaign

Status: `SYM`  
`verification_type: software_test`

## Runs

| Run | Command | Artifact hash |
|---|---|---|
| 1 | `upi debug-index data --inspect` | `b89b24577cc6250e449d3cd0eb7ddeb02f351333cb1a87b4d2be7d8f33d28f46` |
| 2 | `upi debug-index data --inspect` | `b89b24577cc6250e449d3cd0eb7ddeb02f351333cb1a87b4d2be7d8f33d28f46` |
| 3 | `upi debug-index data --inspect` | `b89b24577cc6250e449d3cd0eb7ddeb02f351333cb1a87b4d2be7d8f33d28f46` |

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
