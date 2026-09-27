# Index triage baseline campaign

Status: `SYM`  
`verification_type: software_test`

## Runs

| Run | Command | Artifact hash |
|---|---|---|
| 1 | `upi debug-index data --inspect` | `733aff76a4d707fff1d2d1f13b6a6fdd4a3e4dc7711c4fe0c4d135a18c33c271` |
| 2 | `upi debug-index data --inspect` | `733aff76a4d707fff1d2d1f13b6a6fdd4a3e4dc7711c4fe0c4d135a18c33c271` |
| 3 | `upi debug-index data --inspect` | `733aff76a4d707fff1d2d1f13b6a6fdd4a3e4dc7711c4fe0c4d135a18c33c271` |

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

## Repair verification (2026-09-08)

- EST: Working tree at commit `b2663cb0d9296cb616865d93d549a44159867601` contained nested merge-conflict markers in five ledger artifacts. The initial main-suite run produced five JSON parsing failures, 134 passes, and 14 temporary-directory permission errors.
- DER: Conflict markers caused the JSON parsing failures; the temporary-directory errors belonged to the local test environment. The repaired artifacts parse and the same suite passes with a writable temporary directory.
- EST: Regenerated the canonical report from current `data/` three times with identical UTF-8/LF bytes; synchronized its SHA-256 across the catalog, run manifest, ledger, and table above. Existing finding identities are unchanged. Aureum records were preserved.
- Reproduction/control: On Windows with Python 3.14.7 and pytest 9.1.1, run `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-tmp/repair-control-UNIQUE` (choose an unused suffix). Expected and observed after repair: 153 passes. ResonanceFS: 9 passes. Ruff and mypy pass for both packages.
- Falsification condition: JSON parsing fails, the regenerated report differs from the baseline, artifact hashes disagree, or a control test fails.
- Scope: `verification_type: software_test`. These results establish local repository/software behavior only; they do not verify physical claims, external connectors, live UI rendering, or the CI Python-version matrix.
