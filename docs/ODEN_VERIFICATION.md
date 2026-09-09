# ODEN implementation verification — 2026-09-09

`verification_type: software_test`. No experimental verification or new physical claim.

## Problem and source

Implement typed residual discovery and the ODEN Knot Map without erasing conflicting
observations or reclassifying canonical UPI records.

EST: isolated branch `oden-knot-engine` starts from fetched default-branch commit
`d0774e10a3d12df3f70c3af885a35cad45a069df`. The original checkout contained uncommitted
laboratory/publishing work and was preserved. This branch does not depend on that work.

Environment: Windows, CPython 3.14.7, pytest 9.1.1, Ruff 0.16.6, mypy 2.3.1,
Node 26.7.0, Playwright 1.62.0, Edge 152.0.4191.66. The CI Python 3.10–3.13 matrix
was not run locally; Ruff/mypy target the repository's declared Python compatibility.

## Files changed

| Layer | Files | Result |
| --- | --- | --- |
| Model | `src/upi/knot_model.py` | Immutable typed observations, paths, tolerances, causes and resolutions |
| Analysis | `src/upi/knot.py`, `src/upi/knot_score.py` | Aligned pair comparisons, RED checks, preservation and transparent ranking |
| Audit and serialization | `src/upi/knot_io.py`, `src/upi/knot_review.py` | Stable JSON and append-only evidence-bearing review decisions |
| Controls and build | `src/upi/knot_examples.py`, `src/upi/knot_site.py` | Existing Lorentz fixture, synthetic controls, static bundle |
| HTTP | `src/upi/contribute/server.py` | ODEN page, fixture API and bounded analysis endpoint |
| UI | `src/upi/contribute/static/oden.html`, `oden.css`, `oden.js` | Responsive knot graph, Mirror View, filters and provenance |
| Verification | `tests/test_knot.py`, `tests/test_knot_http.py`, `tests/smoke_oden.py` | Deterministic core, HTTP and real-browser controls |
| Documentation | `README.md`, `docs/ODEN_KNOT_ENGINE.md`, this file | Usage, boundaries and reproducible results |
| Local tooling | `.gitignore` | Excludes isolated browser tooling/cache |

## EST observations and test results

| Check | Expected | Observed |
| --- | --- | --- |
| Full `pytest tests -q` | All repository tests green | **164 passed, 2 failed**; two failures also existed before the patch |
| ODEN pytest subset | All new controls green | **16 passed** |
| Ruff, `src tests` | No violations | Passed |
| mypy, `src/upi --ignore-missing-imports` | No type errors | Passed, 34 source files |
| JS syntax check | Valid JavaScript | Passed |
| Browser smoke | Selection, seven filters, import/export, live analysis work | Passed |
| Browser layouts | No horizontal overflow at 1440px and 390px | Passed; screenshots inspected |
| Source-text injection control | HTML-like input remains text | Passed; no page or console errors |
| Static build | Complete allowlisted archive | Passed; `dist/oden-knot-engine.zip` |
| Wheel build and inspection | Python modules, ODEN assets and all schemas included | Passed, 12 packaged schemas |
| Schema/data checks from CI | Valid schemas and example records | Passed, 12 schemas and 105 records |
| ResonanceFS existing suite | Lint, typing and tests green | Passed, 9 tests and 8 typed source files |
| Deployment | Verified remote release | **STOP**, no upload performed |

The exact Lorentz time round trip has epsilon about `4.235e-22 s`, below its declared
`1e-18 s` numerical bound and `1e-9 s` tolerance: CLOSED / NUMERICAL_NOISE.
The deliberate observer-B offsets produce a position residual about `0.762188687 m`
against `0.1 m`: OPEN, not new physics. Raw observer A, predicted B, perturbed B and
reconstructed A are retained in the gallery's control provenance.

Synthetic temporal, name/function, false-mirror and sign-loss controls produce their
expected typed findings. Every knot runs at least 14 RED checks. A decision may falsify
a candidate explanation without changing the original residual or measured state.

## Existing failures and superseded assumptions

EST: before implementation, the baseline run already failed:

- `tests/test_triage.py::test_live_report_matches_known_catalog`
- `tests/test_triage.py::test_canonical_baseline_matches_live_report`

The live triage report contains `UPI-E007` ("Scientific claim lacks evidence provenance")
for `data/bridges/e8_coxeter_from_weyl.json` and `data/bridges/e8_weyl_from_lattice.json`.
These findings are absent from the accepted catalog. The initial run also had 14
temporary-directory errors with the deeply nested Windows worktree path. A short
temporary directory removed all 14 setup errors; the two triage failures remained.

DER: the two triage failures are not introduced by ODEN (`DERIVED_FROM`: baseline and
final run agreement). No baseline catalog, canonical bridge, scientific classification
or failing test was rewritten to hide them.

ERR/superseded: “all initial failures are application regressions.” The temporary-path
setup failures and pre-existing catalog findings have separate causes and controls.
The first wheel attempt also failed because a no-isolation environment lacked setuptools;
using the declared isolated build requirements succeeded. No dependency declaration was changed.

HYP candidates for the E8 findings: missing bridge evidence versus incomplete audit coverage.
The tests do not decide whether the scientific relation itself is wrong.

STOP: canonical triage acceptance requires provenance review of those two bridge records.
`stop_reason`: accepted finding catalog disagrees with current default-branch data.
Smallest next observation: inspect each bridge's source/evidence fields and validator
expectations, then decide whether an evidenced correction or reviewed catalog update is warranted.

## Reproduction and falsification

Use an environment installed from this checkout, or explicitly set `PYTHONPATH=src`.
On Windows use a short fresh `--basetemp` path, for example:

```powershell
python -m pytest tests -q -p no:cacheprovider --basetemp="$env:TEMP/oden-reproduce"
python -m pytest tests/test_knot.py tests/test_knot_http.py -q -p no:cacheprovider --basetemp="$env:TEMP/oden-controls"
python -m ruff check src tests
python -m mypy src/upi --ignore-missing-imports
node --check src/upi/contribute/static/oden.js
python -m upi.knot_site
python tests/smoke_oden.py
```

Browser tooling is optional and separate from offline core tests. Screenshots are
`dist/oden-1440.png` and `dist/oden-390.png`. The static archive contains a SHA-256
manifest for its entry point, assets and data; it contains no credentials.

Falsification condition: exact Lorentz closure fails; a wrong timestamp, incompatible
domain/unit or noninvertible loss closes silently; an input observation is mutated;
a review erases epsilon; a weak-provenance discrepancy outranks the stronger controlled
comparison; or UI filters/details differ from the computed result.

## Engine, UI and deployment status

EST: the engine, local HTTP surface, static build and browser flows work within the
tested scope. Core transformations must be supplied as recorded typed paths; arbitrary
remote code is never executed. Uncertainty covariance, real asymmetry and model failure
remain explicitly unverified. The synthetic gallery is not independent source evidence.

Known OPEN knots: perturbed observer residual, synthetic historical labels, unresolved
name variants and information loss. BAD_MIRROR cases request REMAP. These are intentionally
preserved findings rather than unresolved software exceptions.

STOP deployment: no verified remote document-root/subdirectory, SSH/SFTP account identity
or usable authenticated session was available for `ssh.wadenholt.se:22`. No matching
deployment/SSH credential environment-variable names were present. The current deployed
version, remote backup and release switch are consequently unverified. Credentials were
neither requested in plaintext nor written to output or source.

Smallest deployment input: the confirmed account and ODEN target directory plus access
through the SSH agent or secure secret store. Then inspect the current remote version,
prepare backup/switch/rollback, obtain publication authorization, deploy and verify HTTPS.
Local UI success does not establish that `wadenholt.se` serves this version.
