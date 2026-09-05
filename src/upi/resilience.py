"""Deterministic recovery and overload-control primitives for UPI.

The module turns the documented ``X_n -> ... -> X_0`` acceptance rule into
executable software behavior.  ``TF1766`` is the default symbolic identity of
the recovery root and 8 Hz is the default control-loop rate; neither is
presented here as a measured law of nature.

No background thread is started.  A host calls :meth:`ResilienceController.tick`
from its own clock source, which may be a software timer or an independently
connected reference clock.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Any

TF1766_ANCHOR_ID = "TF1766"
CONTROL_CLOCK_HZ = 8.0


def _canonical_json(value: Any) -> str:
    """Return the stable JSON representation used by every resilience hash."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def content_hash(value: Any) -> str:
    """Hash a JSON-compatible value using UPI's canonical serialization."""
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class RecoveryCheckpoint:
    """One immutable, content-addressed state in a backward recovery chain."""

    checkpoint_id: str
    anchor_id: str
    sequence: int
    state_json: str
    state_hash: str
    previous_checkpoint_hash: str | None
    recorded_at: str
    control_clock_hz: float
    checkpoint_hash: str

    @classmethod
    def create(
        cls,
        state: dict[str, Any],
        *,
        anchor_id: str = TF1766_ANCHOR_ID,
        previous: RecoveryCheckpoint | None = None,
        recorded_at: datetime | None = None,
        control_clock_hz: float = CONTROL_CLOCK_HZ,
    ) -> RecoveryCheckpoint:
        """Create a checkpoint linked to *previous*, or an anchor when omitted."""
        if not anchor_id:
            raise ValueError("anchor_id must not be empty")
        if control_clock_hz <= 0:
            raise ValueError("control_clock_hz must be positive")
        if previous is not None and previous.anchor_id != anchor_id:
            raise ValueError("checkpoint anchor_id must match the previous checkpoint")

        state_json = _canonical_json(state)
        state_digest = sha256(state_json.encode("utf-8")).hexdigest()
        sequence = 0 if previous is None else previous.sequence + 1
        checkpoint_id = f"{anchor_id}:{sequence}:{state_digest[:16]}"
        previous_hash = None if previous is None else previous.checkpoint_hash
        recorded_text = _timestamp(recorded_at or datetime.now(timezone.utc))
        body = {
            "checkpoint_id": checkpoint_id,
            "anchor_id": anchor_id,
            "sequence": sequence,
            "state_hash": state_digest,
            "previous_checkpoint_hash": previous_hash,
            "recorded_at": recorded_text,
            "control_clock_hz": float(control_clock_hz),
        }
        return cls(
            checkpoint_id=checkpoint_id,
            anchor_id=anchor_id,
            sequence=sequence,
            state_json=state_json,
            state_hash=state_digest,
            previous_checkpoint_hash=previous_hash,
            recorded_at=recorded_text,
            control_clock_hz=float(control_clock_hz),
            checkpoint_hash=content_hash(body),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecoveryCheckpoint:
        """Restore and validate one durable checkpoint receipt."""
        state = data.get("state")
        if not isinstance(state, dict):
            raise ValueError("checkpoint state must be an object")
        try:
            checkpoint = cls(
                checkpoint_id=str(data["checkpoint_id"]),
                anchor_id=str(data["anchor_id"]),
                sequence=int(data["sequence"]),
                state_json=_canonical_json(state),
                state_hash=str(data["state_hash"]),
                previous_checkpoint_hash=(
                    None
                    if data.get("previous_checkpoint_hash") is None
                    else str(data["previous_checkpoint_hash"])
                ),
                recorded_at=str(data["recorded_at"]),
                control_clock_hz=float(data["control_clock_hz"]),
                checkpoint_hash=str(data["checkpoint_hash"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid checkpoint receipt: {exc}") from exc
        errors = checkpoint.validate()
        if errors:
            raise ValueError("invalid checkpoint receipt: " + "; ".join(errors))
        return checkpoint

    @property
    def state(self) -> dict[str, Any]:
        """Return a detached copy of the checkpointed state."""
        value = json.loads(self.state_json)
        if not isinstance(value, dict):  # Defensive; create() only accepts dictionaries.
            raise ValueError("checkpoint state must decode to an object")
        return value

    def hash_body(self) -> dict[str, Any]:
        """Return the exact fields committed by ``checkpoint_hash``."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "anchor_id": self.anchor_id,
            "sequence": self.sequence,
            "state_hash": self.state_hash,
            "previous_checkpoint_hash": self.previous_checkpoint_hash,
            "recorded_at": self.recorded_at,
            "control_clock_hz": self.control_clock_hz,
        }

    def validate(self) -> list[str]:
        """Return integrity errors without mutating the checkpoint."""
        errors: list[str] = []
        if self.sequence < 0:
            errors.append("checkpoint sequence must not be negative")
        if sha256(self.state_json.encode("utf-8")).hexdigest() != self.state_hash:
            errors.append("state_hash does not match checkpoint state")
        if content_hash(self.hash_body()) != self.checkpoint_hash:
            errors.append("checkpoint_hash does not match checkpoint metadata")
        if self.sequence == 0 and self.previous_checkpoint_hash is not None:
            errors.append("anchor checkpoint must not have a previous checkpoint")
        if self.sequence > 0 and self.previous_checkpoint_hash is None:
            errors.append("non-anchor checkpoint must link to a previous checkpoint")
        if self.control_clock_hz <= 0:
            errors.append("control_clock_hz must be positive")
        try:
            _parse_timestamp(self.recorded_at)
        except ValueError as exc:
            errors.append(str(exc))
        return errors

    def to_dict(self, *, include_state: bool = True) -> dict[str, Any]:
        """Serialize the durable receipt; include the recoverable state by default."""
        result = {**self.hash_body(), "checkpoint_hash": self.checkpoint_hash}
        if include_state:
            result["state"] = self.state
        return result


class RecoveryChain:
    """Append-only checkpoint ledger with a movable active-state pointer."""

    def __init__(
        self,
        anchor_state: dict[str, Any],
        *,
        anchor_id: str = TF1766_ANCHOR_ID,
        recorded_at: datetime | None = None,
        control_clock_hz: float = CONTROL_CLOCK_HZ,
    ) -> None:
        anchor = RecoveryCheckpoint.create(
            anchor_state,
            anchor_id=anchor_id,
            recorded_at=recorded_at,
            control_clock_hz=control_clock_hz,
        )
        self._checkpoints: dict[str, RecoveryCheckpoint] = {
            anchor.checkpoint_hash: anchor
        }
        self._active_hash = anchor.checkpoint_hash
        self._anchor_hash = anchor.checkpoint_hash

    @property
    def active(self) -> RecoveryCheckpoint:
        return self._checkpoints[self._active_hash]

    @property
    def anchor(self) -> RecoveryCheckpoint:
        return self._checkpoints[self._anchor_hash]

    @property
    def at_anchor(self) -> bool:
        return self._active_hash == self._anchor_hash

    def append(
        self, state: dict[str, Any], *, recorded_at: datetime | None = None
    ) -> RecoveryCheckpoint:
        """Add a new state after the currently active checkpoint."""
        checkpoint = RecoveryCheckpoint.create(
            state,
            anchor_id=self.anchor.anchor_id,
            previous=self.active,
            recorded_at=recorded_at,
            control_clock_hz=self.anchor.control_clock_hz,
        )
        self._checkpoints[checkpoint.checkpoint_hash] = checkpoint
        self._active_hash = checkpoint.checkpoint_hash
        return checkpoint

    @classmethod
    def restore(cls, document: dict[str, Any]) -> RecoveryChain:
        """Restore a complete append-only ledger from a serialized document."""
        if document.get("format") != "upi-recovery-chain":
            raise ValueError("recovery document has an unknown format")
        if document.get("version") != "1.0.0":
            raise ValueError("recovery document has an unsupported version")
        if document.get("status") != "SYM":
            raise ValueError("recovery architecture status must remain SYM")
        if document.get("verification_type") != "software_test":
            raise ValueError("recovery verification_type must be software_test")
        rows = document.get("checkpoints")
        if not isinstance(rows, list) or not rows:
            raise ValueError("recovery document must contain checkpoints")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("every recovery checkpoint must be an object")
        checkpoints = [RecoveryCheckpoint.from_dict(row) for row in rows]
        by_hash = {checkpoint.checkpoint_hash: checkpoint for checkpoint in checkpoints}
        if len(by_hash) != len(checkpoints):
            raise ValueError("recovery document contains duplicate checkpoint hashes")

        chain = cls.__new__(cls)
        chain._checkpoints = by_hash
        chain._anchor_hash = str(document.get("anchor_checkpoint_hash") or "")
        chain._active_hash = str(document.get("active_checkpoint_hash") or "")
        errors = chain.validate_all()
        if errors:
            raise ValueError("invalid recovery chain: " + "; ".join(errors))
        return chain

    def step_back(self) -> RecoveryCheckpoint:
        """Move one state toward TF1766/X0 while preserving all ledger entries."""
        current = self.active
        if current.previous_checkpoint_hash is None:
            return current
        previous = self._checkpoints.get(current.previous_checkpoint_hash)
        if previous is None:
            raise ValueError("recovery chain is missing a previous checkpoint")
        self._active_hash = previous.checkpoint_hash
        return previous

    def rewind_to_anchor(self) -> tuple[RecoveryCheckpoint, ...]:
        """Walk back to X0 and return every activated checkpoint in order."""
        activated: list[RecoveryCheckpoint] = []
        while not self.at_anchor:
            activated.append(self.step_back())
        return tuple(activated)

    def active_lineage(self) -> tuple[RecoveryCheckpoint, ...]:
        """Return the active path from the current state back to the anchor."""
        lineage: list[RecoveryCheckpoint] = []
        current = self.active
        while True:
            lineage.append(current)
            if current.previous_checkpoint_hash is None:
                break
            previous = self._checkpoints.get(current.previous_checkpoint_hash)
            if previous is None:
                break
            current = previous
        return tuple(lineage)

    def validate_active_lineage(self) -> list[str]:
        """Validate hashes, sequence order and the Xn-to-X0 path."""
        errors: list[str] = []
        lineage = self.active_lineage()
        for checkpoint in lineage:
            errors.extend(
                f"{checkpoint.checkpoint_id}: {error}"
                for error in checkpoint.validate()
            )
        for current, previous in zip(lineage, lineage[1:], strict=False):
            if current.previous_checkpoint_hash != previous.checkpoint_hash:
                errors.append(f"{current.checkpoint_id}: previous hash link is broken")
            if current.sequence != previous.sequence + 1:
                errors.append(f"{current.checkpoint_id}: sequence link is broken")
        if not lineage or lineage[-1].checkpoint_hash != self._anchor_hash:
            errors.append("active lineage does not terminate at the TF1766 anchor")
        return errors

    def validate_all(self) -> list[str]:
        """Validate every preserved branch plus the currently active lineage."""
        errors: list[str] = []
        anchor = self._checkpoints.get(self._anchor_hash)
        active = self._checkpoints.get(self._active_hash)
        if anchor is None:
            errors.append("anchor checkpoint hash is missing from the ledger")
        elif anchor.anchor_id != TF1766_ANCHOR_ID or anchor.sequence != 0:
            errors.append("recovery root is not a sequence-zero TF1766 anchor")
        if active is None:
            errors.append("active checkpoint hash is missing from the ledger")
        for checkpoint in self._checkpoints.values():
            errors.extend(
                f"{checkpoint.checkpoint_id}: {error}"
                for error in checkpoint.validate()
            )
            if anchor is not None and checkpoint.anchor_id != anchor.anchor_id:
                errors.append(
                    f"{checkpoint.checkpoint_id}: anchor_id differs from TF1766 root"
                )
            if checkpoint.previous_checkpoint_hash is None:
                if checkpoint.checkpoint_hash != self._anchor_hash:
                    errors.append(
                        f"{checkpoint.checkpoint_id}: non-anchor root is not allowed"
                    )
                continue
            previous = self._checkpoints.get(checkpoint.previous_checkpoint_hash)
            if previous is None:
                errors.append(
                    f"{checkpoint.checkpoint_id}: previous checkpoint is missing"
                )
            elif checkpoint.sequence != previous.sequence + 1:
                errors.append(f"{checkpoint.checkpoint_id}: sequence link is broken")
        if active is not None:
            errors.extend(self.validate_active_lineage())
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize all branches and pointers for atomic durable storage."""
        checkpoints = sorted(
            self._checkpoints.values(),
            key=lambda checkpoint: (checkpoint.sequence, checkpoint.checkpoint_hash),
        )
        return {
            "format": "upi-recovery-chain",
            "version": "1.0.0",
            "status": "SYM",
            "verification_type": "software_test",
            "anchor_checkpoint_hash": self._anchor_hash,
            "active_checkpoint_hash": self._active_hash,
            "checkpoints": [checkpoint.to_dict() for checkpoint in checkpoints],
            "confusion_guard": (
                "TF1766 is a recovery-root identifier and 8 Hz is an implementation "
                "clock, not an experimentally established universal constant."
            ),
        }


@dataclass(frozen=True)
class VerificationReceipt:
    """One independently attributable decision about an unchanged checkpoint."""

    proposal_hash: str
    evidence_hash: str
    verifier_id: str
    decided_at: str
    approved: bool = True

    @classmethod
    def create(
        cls,
        *,
        proposal_hash: str,
        evidence: Any,
        verifier_id: str,
        decided_at: datetime,
        approved: bool = True,
    ) -> VerificationReceipt:
        if not verifier_id:
            raise ValueError("verifier_id must not be empty")
        return cls(
            proposal_hash=proposal_hash,
            evidence_hash=content_hash(evidence),
            verifier_id=verifier_id,
            decided_at=_timestamp(decided_at),
            approved=approved,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return an independently hashable audit receipt."""
        body = {
            "proposal_hash": self.proposal_hash,
            "evidence_hash": self.evidence_hash,
            "verifier_id": self.verifier_id,
            "decided_at": self.decided_at,
            "approved": self.approved,
        }
        return {**body, "receipt_hash": content_hash(body)}


class TemporalMirrorState(str, Enum):
    EMPTY = "EMPTY"
    FIRST_RATIFIED = "FIRST_RATIFIED"
    SECOND_RATIFIED = "SECOND_RATIFIED"
    REJECTED = "REJECTED"


class TemporalMirrorGate:
    """Require the same checkpoint to pass two independent decisions over time."""

    def __init__(self, proposal_hash: str, *, minimum_interval_s: float = 0.125):
        if minimum_interval_s < 0:
            raise ValueError("minimum_interval_s must not be negative")
        self.proposal_hash = proposal_hash
        self.minimum_interval_s = minimum_interval_s
        self.first: VerificationReceipt | None = None
        self.second: VerificationReceipt | None = None
        self.state = TemporalMirrorState.EMPTY

    @property
    def verified(self) -> bool:
        return self.state == TemporalMirrorState.SECOND_RATIFIED

    def submit(self, receipt: VerificationReceipt) -> list[str]:
        """Record a receipt, returning reasons when the gate remains closed."""
        errors: list[str] = []
        if receipt.proposal_hash != self.proposal_hash:
            return ["verification receipt refers to a different checkpoint hash"]
        try:
            receipt_time = _parse_timestamp(receipt.decided_at)
        except ValueError as exc:
            return [str(exc)]
        if not receipt.approved:
            self.state = TemporalMirrorState.REJECTED
            self.second = receipt
            return ["verification receipt rejected the recovery checkpoint"]
        if self.state == TemporalMirrorState.REJECTED:
            return ["temporal mirror gate is rejected and must be reset"]
        if self.first is None:
            self.first = receipt
            self.state = TemporalMirrorState.FIRST_RATIFIED
            return []
        if self.verified:
            return []
        if receipt.verifier_id == self.first.verifier_id:
            errors.append("second verification must use an independent verifier")
        first_time = _parse_timestamp(self.first.decided_at)
        minimum_time = first_time + timedelta(seconds=self.minimum_interval_s)
        if receipt_time < minimum_time:
            errors.append("second verification occurred before the temporal boundary")
        if errors:
            return errors
        self.second = receipt
        self.state = TemporalMirrorState.SECOND_RATIFIED
        return []

    def to_dict(self) -> dict[str, Any]:
        """Serialize both decisions so the temporal gate is externally auditable."""
        return {
            "proposal_hash": self.proposal_hash,
            "minimum_interval_s": self.minimum_interval_s,
            "state": self.state.value,
            "verified": self.verified,
            "first": None if self.first is None else self.first.to_dict(),
            "second": None if self.second is None else self.second.to_dict(),
        }


class ResilienceMode(str, Enum):
    RUNNING = "RUNNING"
    THROTTLED = "THROTTLED"
    BACKTRACKING = "BACKTRACKING"
    ISOLATED = "ISOLATED"
    RECOVERY_PENDING = "RECOVERY_PENDING"


@dataclass(frozen=True)
class ResilienceDecision:
    """Observable result of a load sample or control-clock tick."""

    mode: ResilienceMode
    action: str
    accepting_input: bool
    external_connection_allowed: bool
    active_checkpoint_hash: str
    at_anchor: bool
    control_tick: int
    reason: str


class ResilienceController:
    """Trip/Trap/Trull overload controller driven by a bounded control clock.

    Engineering mapping:

    * Trip: apply backpressure at the high-water mark.
    * Trap: isolate external ingress if both data and reference lanes saturate.
    * Trull: walk the immutable chain backward, then require temporal mirror
      verification before reconnecting.
    """

    def __init__(
        self,
        chain: RecoveryChain,
        *,
        control_clock_hz: float = CONTROL_CLOCK_HZ,
        high_watermark: float = 0.75,
        critical_watermark: float = 0.95,
    ) -> None:
        if control_clock_hz <= 0:
            raise ValueError("control_clock_hz must be positive")
        if not 0 < high_watermark < critical_watermark <= 1:
            raise ValueError("watermarks must satisfy 0 < high < critical <= 1")
        if chain.anchor.anchor_id != TF1766_ANCHOR_ID:
            raise ValueError("resilience chain must terminate at the TF1766 anchor")
        if abs(chain.anchor.control_clock_hz - control_clock_hz) > 1e-12:
            raise ValueError("controller clock must match the recovery-chain clock")
        self.chain = chain
        self.control_clock_hz = control_clock_hz
        self.high_watermark = high_watermark
        self.critical_watermark = critical_watermark
        self.mode = ResilienceMode.RUNNING
        self._tick = 0
        self._digital_fill = 0.0
        self._reference_fill = 0.0
        self._reference_available = True
        self._recovery_required = False
        self._gate: TemporalMirrorGate | None = None

    @property
    def control_period_s(self) -> float:
        return 1.0 / self.control_clock_hz

    def _check_ratio(self, name: str, value: float) -> float:
        numeric = float(value)
        if not 0.0 <= numeric <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
        return numeric

    def _decision(self, action: str, reason: str) -> ResilienceDecision:
        accepting = self.mode == ResilienceMode.RUNNING
        connected = self.mode not in {
            ResilienceMode.ISOLATED,
            ResilienceMode.RECOVERY_PENDING,
        }
        return ResilienceDecision(
            mode=self.mode,
            action=action,
            accepting_input=accepting,
            external_connection_allowed=connected,
            active_checkpoint_hash=self.chain.active.checkpoint_hash,
            at_anchor=self.chain.at_anchor,
            control_tick=self._tick,
            reason=reason,
        )

    def sample_load(
        self,
        digital_fill_ratio: float,
        reference_fill_ratio: float,
        *,
        reference_available: bool = True,
    ) -> ResilienceDecision:
        """Apply load gates without doing hidden work between clock ticks."""
        self._digital_fill = self._check_ratio(
            "digital_fill_ratio", digital_fill_ratio
        )
        self._reference_fill = self._check_ratio(
            "reference_fill_ratio", reference_fill_ratio
        )
        self._reference_available = bool(reference_available)

        digital_critical = self._digital_fill >= self.critical_watermark
        reference_critical = (
            not self._reference_available
            or self._reference_fill >= self.critical_watermark
        )
        if digital_critical and reference_critical:
            self.chain.rewind_to_anchor()
            self.mode = ResilienceMode.ISOLATED
            self._recovery_required = True
            self._gate = None
            return self._decision(
                "TRAP_ISOLATE",
                "both digital and reference lanes are unavailable or critical",
            )
        if digital_critical:
            self.mode = ResilienceMode.BACKTRACKING
            self._recovery_required = True
            self._gate = None
            return self._decision(
                "TRULL_BACKTRACK",
                "digital lane is critical; step toward TF1766 on each control tick",
            )
        lane_high = (
            self._digital_fill >= self.high_watermark
            or self._reference_fill >= self.high_watermark
            or not self._reference_available
        )
        if self._recovery_required:
            self.mode = ResilienceMode.RECOVERY_PENDING
            if lane_high:
                self._gate = None
                return self._decision(
                    "WAIT_SAFE_LOAD",
                    "recovery remains isolated until both lanes are below the high-water mark",
                )
            if self._gate is None:
                self._gate = TemporalMirrorGate(
                    self.chain.active.checkpoint_hash,
                    minimum_interval_s=self.control_period_s,
                )
            return self._decision(
                "VERIFY_RECOVERY",
                "load is safe; two temporal mirror receipts are required",
            )
        if lane_high:
            self.mode = ResilienceMode.THROTTLED
            return self._decision(
                "TRIP_THROTTLE",
                "a lane reached the high-water mark; external input is paused",
            )
        self.mode = ResilienceMode.RUNNING
        return self._decision("CONTINUE", "both lanes are below the high-water mark")

    def tick(self) -> ResilienceDecision:
        """Advance one 8 Hz control tick and perform at most one backward step."""
        self._tick += 1
        if self.mode == ResilienceMode.BACKTRACKING:
            before = self.chain.active.checkpoint_hash
            checkpoint = self.chain.step_back()
            if checkpoint.checkpoint_hash == before:
                return self._decision(
                    "HOLD_ANCHOR",
                    "TF1766 anchor is active while digital load remains critical",
                )
            return self._decision(
                "STEP_BACK",
                f"activated checkpoint {checkpoint.checkpoint_id}",
            )
        if self.mode == ResilienceMode.ISOLATED:
            return self._decision(
                "HEARTBEAT_ISOLATED",
                "external ingress is disconnected; TF1766 control remains alive",
            )
        return self._decision("HEARTBEAT", "control plane is alive")

    def submit_recovery_receipt(
        self, receipt: VerificationReceipt
    ) -> ResilienceDecision:
        """Apply one recovery decision and reconnect only after the mirror closes."""
        if self.mode != ResilienceMode.RECOVERY_PENDING or self._gate is None:
            return self._decision(
                "REJECT_RECEIPT",
                "recovery receipts are accepted only after load returns to safe levels",
            )
        errors = self._gate.submit(receipt)
        if errors:
            return self._decision("REJECT_RECEIPT", "; ".join(errors))
        if not self._gate.verified:
            return self._decision(
                "WAIT_SECOND_VERIFICATION",
                "first recovery decision recorded against the unchanged checkpoint",
            )
        self._recovery_required = False
        self.mode = ResilienceMode.RUNNING
        return self._decision(
            "RECONNECT",
            "two independent decisions closed the temporal mirror gate",
        )
