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

Send `POST /api/promote` with `X-UPI-Review-Token` and a JSON object containing
`address`. Missing or incorrect credentials return 403. A matching token permits
promotion only when the record has evidence or primary sources. The public form
does not collect or store this token. Use HTTPS termination for remote access;
the built-in server serves HTTP.

Promotion updates the live database. Canonical Git changes still require the
maintainer merge workflow. See `openapi.yaml` for the endpoint contract.
