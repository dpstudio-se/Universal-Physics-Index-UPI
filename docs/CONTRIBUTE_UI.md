# Public contribution UI

Status: `SYM` architecture with `verification_type: software_test`.

The live UI lets anyone add classified UPI records. Writes go to a durable
database and appear over Server-Sent Events. Repo files under `data/` are not
mutated by the UI.

## Six invariants

| Invariant | Live contribution |
|---|---|
| Owner | public contributor; manager does not write EST |
| Explicit state | stored row with address, status, hash, created_at |
| Durable artifact | SQLite file or remote PostgreSQL |
| Evidence | schema + boundary validation before insert |
| Retry | client resubmits after listed errors |
| Approval | EST is rejected on the public endpoint |

## dna_minne_7.834

Address: `UPI<symbolic,1,memory,dna_minne_7.834>`

This is a symbolic memory slot at 7.834 Hz. It is not biological DNA, not a
medical frequency, and not a universal constant.

## Run

The local model laboratory is available at `/lab`, with a link from the
contribution home page. See [T€@X laboratory v1](TEAX_LAB_V1.md) for calculators,
model boundaries, export and verification.

```bash
upi serve --database sqlite:///upi.db
upi serve --database postgresql://upi:upi@host:5432/upi
```

`UPI_DATABASE_URL` is accepted when `--database` is omitted.

## Maintainer promotion

Set `UPI_REVIEW_TOKEN` in the server environment before starting `upi serve`.
The server reads environment variables directly; it does not load `.env` itself.
An empty token disables promotion. There are no accounts, sessions, refresh
tokens, or automatic expiry. Restart the server to rotate the shared token.

Promotion also requires a server-owned `PromotionPolicy` configured on `ContributionService`.
The default service has no domain policy and fails closed; setting a token alone cannot enable
promotion. Policy setup is a Python integration, not a client-supplied report or CLI flag.

1. Send `POST /api/promotion-review` with `X-UPI-Review-Token`, `address` and `human_intent`.
2. Inspect the returned report. STOP has no usable `review_id`. Passing checks return
   `AWAITING_HUMAN_REVIEW` and a server-issued review id valid for 15 minutes.
3. After human review, send `POST /api/promote` with the token, `address`, `review_id` and
   `human_decision: "approve"`. The server reruns feedback and rejects changed inputs or policy.

Missing or incorrect credentials return 403. Missing, stale or blocked reviews return 409.
Receipts are process-local and one-use; restarts require a new review. Successful promotion and
its decision audit are stored atomically. The shared token identifies its holder, not an individual
human account. The public form does not collect or store this token. Use HTTPS termination for
remote access; the built-in server serves HTTP. See `FEEDBACK_VALIDATION.md` for policy requirements.

Promotion updates the live database. Canonical Git changes still require the
maintainer merge workflow. See `openapi.yaml` for the endpoint contract.
