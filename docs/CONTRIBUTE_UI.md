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
