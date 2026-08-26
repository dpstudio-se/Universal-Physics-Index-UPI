# Recovery drill: index triage

1. Run `upi triage data --inspect --known examples/ledger/baselines/known-findings.json`
2. If unexpected findings appear, do not edit `data/` to hide them.
3. Inspect the codes. Update the catalog only with maintainer approval.
4. Resume from the last matching `artifact_hash` in `examples/ledger/baselines/runs.json`.

This drill is `software_test` only.
