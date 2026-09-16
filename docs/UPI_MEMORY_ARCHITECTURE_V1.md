# UPI Memory Architecture v1

Purpose: separate short-lived working context, durable reference memory, and quarantine while preserving provenance and auditability.

## Three layers

### Working Memory
Current workload, active hypotheses, temporary calculations and unresolved questions.

### Long-Term DNA
Versioned durable records:
- EST
- reproducible DER
- persistent HYP
- ERR and STOP
- definitions and equations
- provenance
- verification paths
- known failure modes

### Junk / Quarantine Vent
Duplicates, transient noise, malformed inputs, abandoned branches and unresolved low-value material. Quarantine is reversible and always records a reason.

## Four operational pillars

These are UPI architectural pillars inspired by the transparency/provenance principles under study around TF1766. They are not asserted to be four legal pillars of TF1766.

1. SOURCE: preserve origin and provenance.
2. OPEN: make reasoning inspectable where applicable.
3. VERIFY: separate evidence, derivation, hypothesis and error.
4. RETURN: allow traceable recovery from prior states and quarantine.

## Dynamic routing

INPUT -> CLASSIFY -> ROUTE

WORK -> active reasoning
DNA -> durable reference
QUARANTINE -> low-value or unresolved
REVIEW -> requires verification

Promotion: WORK -> DNA only after verification and provenance requirements.

Demotion: DNA -> REVIEW when contradiction or superseding evidence appears.

Recovery: QUARANTINE -> REVIEW when new evidence makes material relevant.

## Invariants

Every promoted record has provenance.
Every quarantined record has a reason.
Every overwrite retains the previous version.
Every final claim has explicit status.

## Relation to Internal DNA

DNA = durable reference
RNA = active workload
Bridge = comparison/update
Working Memory = current state
Quarantine = reversible junk vent

The objective is controlled information flow, not maximum retention.
