# ODEN Knot Engine

ODEN compares two or more recorded paths at explicitly corresponding checkpoints.
It locates disagreements without choosing which observation to erase. The existing
Lorentz forward/inverse functions provide the physics control. No canonical scientific
record or scientific status is migrated by this engine.

`MIRROR_FAIL => KNOT_FOUND`, not new physics or a source error.
`PATCH_NOT_ERASE = true` preserves raw observations, both paths, source references,
transform descriptions, uncertainty and the first failing aligned checkpoint.

## Run and build

From an environment with this checkout installed (`pip install -e ".[dev]"`):

```sh
python -m upi.cli serve --host 127.0.0.1 --port 8080
# Open http://127.0.0.1:8080/oden/
python -m upi.knot_site
python -m http.server 8081 --directory dist/oden
# Open http://127.0.0.1:8081/
```

The builder creates `dist/oden/` and `dist/oden-knot-engine.zip`, containing only
allowlisted static assets, a hash manifest, example input and computed results.
No credentials, repository files or database are copied. Assets and data use relative
URLs and support a host subdirectory. Build output is not a deployment.

The gallery contains seven independent synthetic controls. Their source lineage is
dependent and ranking scores are consequently zero. The historical territories are
invented; the name strings are distinct observations, not resolved genealogical identities.
The downloadable input contains the two Lorentz checkpoints, not a chain connecting
unrelated scientific and historical domains.

## Input and API

Download `paths.example.json` from the UI, retain its `format: upi-oden-paths` and
`version: 1.0`, and supply your recorded paths and checkpoint tolerances.

```sh
python -m upi.knot_site --input paths.json --output dist/oden-custom
```

`POST /api/knots/analyze` accepts the same JSON (256 KB maximum). It computes a result
without writing to the canonical graph or contribution database. `GET /api/knots`
returns the synthetic gallery. The static UI opens result JSON; interactive analysis
requires the Python server. It does not execute transformations supplied as remote text.
Core analysis has no network dependency.

Python callers can use `analyze(paths, tolerances)` from `upi.knot`, with frozen
`Observation`, `Step`, `PathTrace` and `Tolerance` from `upi.knot_model`.
The JSON adapter is `upi.knot_io.analyze_document`; `dumps` provides stable sorted UTF-8
serialization and rejects nonfinite numbers. At most 20 paths / 500 steps are accepted.
All path pairs are compared; correspondence is an explicit checkpoint key, never an
inferred spelling match. Intervening steps retain their original order and input IDs.
An unmatched checkpoint creates a `STOP` alignment gap. The first failure is the first
*aligned* failed checkpoint; absent observations cannot establish an earlier closure.

Every observation carries entity, domain, time, location, perspective, name, function,
source, source group, source quality, confidence, raw value, units, provenance, uncertainty
and scientific status. Missing context remains unknown. Timestamps are exact supplied
strings, so equivalent date spellings need an explicit upstream remap. Nothing propagates
present labels backward. Coordinates, names, units and functions are never normalized.

Numeric residuals are absolute differences in the declared units. Strings use the discrete
equality metric (0 or 1, retaining the original label unit); this is not a physical distance.
Incompatible entity/domain/function/value types or units yield `epsilon: null`, never an
invented numeric difference. Unknown uncertainties remain null; covariance is not assumed
and uncertainty is not silently added to the declared tolerance.

## RED and decisions

All knots, including high scores, run the RED checks. `DETECTED` means a conflict follows
from supplied metadata; `CLEAR` means that particular check did not detect a conflict;
`UNKNOWN` has a named `STOP` and a next observation. Neither CLEAR nor user-supplied flags
authenticate a source. Physical asymmetry and model failure remain explicit unknowns until
independent observations can discriminate them.

Exact/within-tolerance typed checkpoints are `CLOSED` only in their declared consistency
scope. Nonzero residuals below a separately declared numerical bound are numerical residue;
other acceptable residuals are tolerance effects. Invalid mirrors lead to `REMAP`.
Unexplained, temporal or lossy discrepancies remain `OPEN`. No residual is forced to zero.

`upi.knot_review.record_decision` appends a reviewer, timestamp, evidence reference and
reason for PATCH / REMAP / FLIP / OPEN / FALSIFIED. The decision is separate from the measured
state: falsifying a candidate explanation does not erase its measured disagreement.
Review decisions are recorded as HYP assertions until independently verified. CLOSED
cannot be assigned to a failed result through review; corrected paths need a new analysis.
Both original and revised reports remain available. The UI exposes decisions and history.

Ranking exposes independence × contradiction strength × source quality × cross-domain
support × persistence. Factors are bounded in [0,1]. Independence requires distinct known
lineage and no shared upstream references. Missing provenance zeros source quality.
Support and persistence default to zero and must be supplied with external justification;
they are engineering inputs, not inferred scientific evidence or probabilities. A high
score cannot promote a scientific status. Existing UPI status enums are reused.

## Verification and falsification

`verification_type: software_test` throughout. The software claim fails if the Lorentz
control exceeds its declared tolerance, raw observations change, incompatible units close,
historical labels propagate backward, weak provenance outranks stronger controlled evidence,
or UI selection/filtering misrepresents a result.

```sh
python -m pytest tests -q
ruff check src tests
mypy src/upi --ignore-missing-imports
node --check src/upi/contribute/static/oden.js
python tests/smoke_oden.py
```

The optional smoke script requires Playwright and installed Edge; it is separate from
offline core pytest tests. It exercises desktop and 390px layouts, all filters, knot details,
file import/export and inert rendering of HTML-like source text. Screenshots go to `dist/`.
Repository integrity, HTTP behavior, browser rendering and remote deployment have separate
verification scopes. See [implementation verification](ODEN_VERIFICATION.md).

## Deployment boundary

Intended host: `ssh.wadenholt.se:22`, public domain `wadenholt.se`. Before publication,
obtain a verified account/document root and working SSH-agent or secret-store authentication.
Review the current remote entry point, save its version, upload into a new release directory,
verify hashes, switch only the agreed ODEN entry point last, then verify HTTPS and rollback.
Do not delete or replace unrelated site content. No remote upload is part of the static builder.
