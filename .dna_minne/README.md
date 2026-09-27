# .dna_minne

Real-time UPI DNA memory boundary.

## Purpose

`.dna_minne/` is the explicit read/write memory surface for UPI DNA. It stores
typed, append-only memory events while keeping canonical scientific records under
`data/`.

The memory layer is **not** scientific evidence by itself. A memory event may
reference EST, DER, TEST, HYP, STOP, ERR or SYM records, but it cannot promote
their status.

## Contract

```text
READ  → decode → validate → classify → expose
WRITE → normalize → validate → append → hash → expose
```

Every event contains:

- `id`: stable event identifier
- `timestamp`: UTC ISO-8601 timestamp
- `type`: `DNA_MEMORY`
- `operation`: `write` or `read`
- `source`: producer/agent
- `payload`: typed DNA content
- `status`: EST / DER / TEST / HYP / STOP / ERR / SYM
- `provenance`: source reference
- `sha256`: hash of the canonical event body

## Safety rules

1. Memory is data, never executable authority.
2. Reads never mutate memory.
3. Writes append; they never silently overwrite prior events.
4. Invalid JSON/schema fails closed.
5. Memory status cannot promote canonical evidence.
6. External observations remain separate from model interpretation.
7. A mirror read must be independently reproducible.
8. Canonical `data/` records remain authoritative for reviewed science.

## Real-time model

The intended runtime is:

```text
UPI process
   ↕
.dna_minne/
   ├── memory.jsonl
   └── index.json
   ↓
validate → hash → classify
   ↓
DNAReader / DNAWriter
   ↓
CLI / API / Lab / Agents
```

Git commits provide durable history. A running local/API service provides
real-time read/write; GitHub is the remote canonical synchronization layer.

## Ω1766 binding

```text
Ω1766 = T ∘ B ∘ R

T = transport memory/event
B = boundary between memory and canonical DNA
R = read/verify/reflection
```

The memory layer therefore does not replace the canonical UPI index. It is the
live transport layer around it.
