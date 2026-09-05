# Index triage baseline campaign

Status: `SYM`  
`verification_type: software_test`

## Runs

| Run | Command | Artifact hash |
|---|---|---|
| 1 | `upi debug-index data --inspect` | `4929c31a0377e173af4e7ba268bfc083f2f402b19a2dedfbe93169e8b66d1df3` |
| 2 | `upi debug-index data --inspect` | `4929c31a0377e173af4e7ba268bfc083f2f402b19a2dedfbe93169e8b66d1df3` |
| 3 | `upi debug-index data --inspect` | `4929c31a0377e173af4e7ba268bfc083f2f402b19a2dedfbe93169e8b66d1df3` |

Finish line: three identical redacted reports, no scanner mutation of `data/`.

## Independent verification

- Reports set `verification_type` to `software_test` and `source_values_redacted` to true.
- `pytest tests/test_triage.py tests/test_governed_system.py` is the verifier evidence.
- Scanner and verifier are separate: debug-index produced the report; tests compared it to the catalog.

## Catalog classes

| Class | Meaning | Approval |
|---|---|---|
| `negative_fixture` | Intentional invalid record | Expected |
| `source_manifest` | Not a node/bridge/theory | Known `STOP`; review classification |
| `hypothesis_boundary_gap` | HYP bridge lacks test/falsification metadata | Known, not closed |
| `provenance_gap` | Scientific record lacks evidence provenance | Known, not closed |

## Manager decision

`advance` the baseline campaign. Cataloged findings stay open until a human corrects their source records. Catalog membership acknowledges the software-test result but does not resolve it. New findings fail the routine.
