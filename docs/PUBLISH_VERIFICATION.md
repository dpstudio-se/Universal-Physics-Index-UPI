# Repository publication verification

Date: 2026-09-05. `verification_type: software_test`.

## Problem and established observations

- `EST`: the starting local base was `8cb4e6150beaf7df1fd6aebfe4ccfb887c022aec`.
  Remote main was six commits ahead at `c765700524b502645766d31dd3d84e4d81ba9b4f`.
  Local recovery, SSE, discovery documentation, and ResonanceFS changes were
  preserved in `afcd715` before merging remote main.
- `EST`: before integration, six UPI tests failed. Integration brought in the
  existing graph, Planck-boundary, and triage corrections; those failures cleared.
- `EST`: Ruff reported an import-format error in `test_sunet_physics_map.py`;
  mypy rejected `len(links)` in `evidence_lens.py` because its type could be None.
  Both are corrected. Remote CI run 33936331214 and audit run 33936331121
  stopped at their lint steps on the previous main.
- `EST`: index triage invoked pytest without installing its test dependencies.
  It now installs the development extra. CI also checks the new ResonanceFS project.
- `EST`: server startup printed the database URL; promotion lacked an OpenAPI
  contract; public text was interpolated into innerHTML; invalid Content-Length
  could raise ValueError. These paths are corrected and the token lifecycle is
  documented. Promotion uses constant-time comparison.

## Reproduction and controls

Local environment: Windows, Python 3.14.7, pytest 9.1.1, Ruff 0.16.6, mypy 2.3.1.
The Windows Store `python` alias could not execute. `.venv/Scripts/python.exe`
worked after installing development dependencies. Default pytest temporary paths
were inaccessible in the sandbox; a fresh directory under `.pytest-tmp/` resolved
that environment issue without changing application behavior.

Run from the repository root, using an available Python interpreter:

```text
python -m pytest tests/ -q
python -m ruff check .
python -m mypy src/upi --ignore-missing-imports
python -m pytest -c projects/resonancefs/pyproject.toml projects/resonancefs/tests -q
python -m mypy --config-file projects/resonancefs/pyproject.toml projects/resonancefs/src
python -m build
```

- `EST`: expected zero failures; observed 150 UPI tests and 9 ResonanceFS tests passed.
- `EST`: Ruff and both mypy checks passed; all 12 public schemas and 94 applicable
  data records validated. Source distribution and wheel built successfully;
  the wheel contains all 12 packaged schemas and browser assets.
- `EST`: HTTP controls cover disabled, missing, incorrect, and valid review tokens,
  evidence requirements, unchanged status on rejection, and malformed body length.
- `EST`: Node syntax validation passed. A minimal DOM harness confirmed that
  HTML-shaped contribution text reaches textContent without invoking innerHTML.
  This is a rendering-code control, not a full browser or hosted-site test.

## Conclusions and limits

`DER`: the observed local failures are resolved in the integrated source. A failing
command above, an unauthorized successful promotion, changed status after rejection,
or executable contribution markup would falsify the corresponding result.

`STOP`: hosted RNA behavior is outside this verification. `stop_reason`: its deployed
code and proxy configuration are not part of the inspected package. The smallest next
observation is the deployed revision/configuration plus a request against that surface.

GitHub Actions results must be checked against the final pushed SHA; local results
do not establish remote runner behavior. No software result establishes experimental
physics, and promotion only enforces the declared software access boundary.
