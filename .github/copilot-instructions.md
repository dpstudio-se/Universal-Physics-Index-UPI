# Copilot instructions for UPI pull requests

When working on `dpstudio-se/Universal-Physics-Index-UPI`, use the repository's typed evidence model and mirror-loop validation.

## Pull request workflow

Before proposing merge/promotion work, inspect the open pull requests with:

```bash
gh pr list --repo dpstudio-se/Universal-Physics-Index-UPI --state open --limit 100
```

For a single PR, run the read-only mirror audit helper:

```bash
python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI --pr <NUMBER>
```

For all open PRs:

```bash
python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI --all-open
```

For a machine-readable report:

```bash
python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI --all-open --json .tmp/upi-pr-mirror.json
```

## Required audit order

1. Read PR metadata and exact changed files.
2. Inspect the diff and identify affected UPI nodes, schemas, prompts, workflows and tests.
3. Bind each scientific claim to its source, code revision, assumptions and exact input data.
4. Run forward and inverse checks where a mathematical bridge is proposed.
5. Check dimensions, semantic quantity types, limiting cases and numerical error.
6. Require a null model or explicit competing explanation for pattern claims.
7. Separate software verification from empirical validation and independent replication.
8. Keep `EST`, `DER`, `HYP`, `STOP`, `ERR`, `SYM` separate from `OPEN`, `TEST`, `CONFLICT` and `PASS/FAIL`.
9. Preserve negative results and unresolved branches.
10. Never infer scientific promotion from CI success, numerical proximity, visual similarity or agent agreement.

## Mirror-loop rule

A successful mathematical round trip establishes computational closure of the declared model, not physical truth.

For any proposed bridge:

```text
observation -> forward model -> prediction -> comparison
       ^                              |
       |                              v
       +------ inverse / recovery <- residual
```

A second path must be independent enough to discriminate the hypothesis. Reusing the same dataset, equation, assumptions or agent does not create independent evidence.

## Frequency guard

Never equate narrative/historical periods with physical frequencies merely because both are called frequencies.
For example, years/cycle and Hz have different dimensions. `7.834`, `7.834125` and `8 Hz` are configurable references in this repository, not universal constants or proof of coupling.

## Safety / authority boundary

This helper is read-only with respect to repository history and scientific status. Do not merge, approve, promote, or rewrite canonical scientific claims merely because the audit passes. Human review remains required for canonical promotion.
