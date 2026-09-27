# Linked robustness lens

UPI can show two views of the same immutable evidence record.

- **Off (default):** show the canonical UPI status.
- **On:** show `EST-LINKED-ROBUSTNESS` when independent external tests support
  the declared loop inside a named tested domain.

The lens does not rewrite `status`, promote physical ontology, or copy an
external test's conclusion to an unrelated claim. It exposes a scoped result:

```text
loop record --MEASURED_BY--> external test record
            --SUPPORTED_BY--> archived result
            --REPLICATED_BY--> independent replication
```

Every link names its source record, target record, relation, source provenance,
and exact tested claim. A loop qualifies only when the criterion was declared,
independence is documented, the aggregate has zero recorded failures, and every
link is typed. Turning the lens off restores the canonical view immediately.

For a mirror operation `M`, a linked test can establish within its domain that

```text
norm(M(M(x)) - x) <= tolerance.
```

It does not by itself establish that every system in nature is the same loop.
Historical archives should be mapped as individual test records; duplicate
reports of one dataset are one evidence lineage, not independent replications.

`verification_type: software_test` applies to the lens implementation. The
linked records retain their own experimental or observational verification.
