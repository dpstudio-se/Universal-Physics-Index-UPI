# TF1766 resilience control

Status: `SYM` architecture with `verification_type: software_test`.

The executable primitives are in `upi.resilience`. They implement the previously documented
backward acceptance path without presenting TF1766 or 8 Hz as an experimentally established law
of nature.

## Invariants

1. `TF1766` identifies the immutable sequence-zero recovery root, `X0`.
2. Every later checkpoint commits its state hash and the previous checkpoint hash.
3. Backtracking moves the active pointer; it never deletes later ledger entries.
4. The default control rate is 8 Hz, so one host-driven tick is 0.125 seconds.
5. The data lane may throttle or disconnect while the control lane continues ticking.
6. Reconnection requires two approvals of the same checkpoint hash, from different verifiers,
   separated by at least one control tick.
7. Changing the checkpoint changes its hash and therefore cannot satisfy the existing mirror gate.

The host must persist `RecoveryChain.to_dict()` atomically after appending or moving the active
pointer. `RecoveryChain.restore()` validates state hashes, checkpoint hashes, links, sequence order,
the active pointer and the TF1766 root before use.

## Trip, Trap and Trull

The names are symbolic aliases for conventional overload controls:

| Alias | Engineering action | Result |
|---|---|---|
| Trip | high-water backpressure | Pause new input; keep the connection and control clock alive |
| Trap | circuit-breaker isolation | When both lanes are critical, disconnect ingress and activate X0 |
| Trull | bounded rollback and replay gate | Step toward X0 once per tick, then require temporal mirror verification |

```text
RUNNING
  -> THROTTLED                 one lane reaches the high-water mark
  -> BACKTRACKING              digital lane reaches the critical mark
  -> ISOLATED                  digital and reference lanes are both critical

BACKTRACKING
  -> X(n-1) -> ... -> X0       at most one step per control tick

ISOLATED / BACKTRACKED
  -> RECOVERY_PENDING          load returns below the high-water mark
  -> FIRST_RATIFIED            first verifier approves the active hash
  -> SECOND_RATIFIED           different verifier approves it after >= 0.125 s
  -> RUNNING                   external input may reconnect
```

`reference_fill_ratio` can represent an independently wired clock or watchdog when such hardware
exists. Without that adapter it is a declared software reference lane, not an analog measurement.

## Temporal mirror

For checkpoint `P` and receipts `V1`, `V2`:

```text
hash(V1.proposal) = hash(P) = hash(V2.proposal)
V1.verifier != V2.verifier
V2.time - V1.time >= 1 / control_clock_hz
V1.approved = V2.approved = true
```

Two software approvals establish recovery consistency only. They do not promote a scientific
claim to `EST`.

## Event-stream overflow

The contribution database remains the durable event source. Each SSE subscriber has a bounded
notification queue. A full queue now trips the connection instead of silently discarding an
unknown gap. The server closes that stream, reads the browser's `Last-Event-ID` on reconnect and
replays durable events. This protects the control path while applying backpressure to a slow
consumer.

## Python example

```python
from datetime import datetime, timedelta, timezone

from upi import RecoveryChain, ResilienceController, VerificationReceipt

now = datetime.now(timezone.utc)
chain = RecoveryChain({"role": "recovery-root", "revision": 0}, recorded_at=now)
chain.append({"revision": 1}, recorded_at=now + timedelta(seconds=1))
control = ResilienceController(chain)

# Digital overload: the host calls tick() at 8 Hz until a safe checkpoint is active.
control.sample_load(0.96, 0.20)
control.tick()

# Safe load opens the double-verification gate, not the external connection.
control.sample_load(0.20, 0.20)
candidate = chain.active.checkpoint_hash
control.submit_recovery_receipt(
    VerificationReceipt.create(
        proposal_hash=candidate,
        evidence={"check": "first"},
        verifier_id="verifier-a",
        decided_at=now,
    )
)
control.submit_recovery_receipt(
    VerificationReceipt.create(
        proposal_hash=candidate,
        evidence={"check": "second"},
        verifier_id="verifier-b",
        decided_at=now + timedelta(seconds=0.125),
    )
)
```

The module does not start a hidden thread, sample physical hardware or guarantee that an operating
system cannot fail. Those integrations require a durable host, an atomic storage adapter and, for
a genuinely analog reference, a named clock/sensor interface.
