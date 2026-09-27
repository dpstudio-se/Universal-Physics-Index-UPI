"""Taurus guardrails: history, independent mirror, delta/epsilon, next observation, pruning and rollback."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Literal


@dataclass(frozen=True)
class TaurusDelta:
    added: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()

    @property
    def has_verified_change(self) -> bool:
        return bool(self.added or self.changed)


@dataclass(frozen=True)
class TaurusObservation:
    check: str
    required: bool = True
    detail: str = ""


@dataclass(frozen=True)
class TaurusMirror:
    forward: str
    reverse: str
    independent: bool
    delta: float
    epsilon: float

    @property
    def within_tolerance(self) -> bool:
        return abs(self.delta) <= self.epsilon


@dataclass(frozen=True)
class TaurusCheckpoint:
    revision: str
    generation: int
    dna_revision: str
    state_digest: str


@dataclass(frozen=True)
class TaurusState:
    generation: int = 0
    dna_revision: str = ""
    workload: tuple[str, ...] = ()
    shadow: tuple[str, ...] = ()
    history: tuple[str, ...] = ()
    checkpoints: tuple[TaurusCheckpoint, ...] = ()
    last_delta: TaurusDelta = field(default_factory=TaurusDelta)
    next_observations: tuple[TaurusObservation, ...] = ()
    status: str = "OPEN"


@dataclass(frozen=True)
class TaurusReport:
    state: TaurusState
    next_state: TaurusState
    decision: Literal["CONTINUE", "STOP", "ROLLBACK"]
    reasons: tuple[str, ...]
    pruned: tuple[str, ...] = ()


def state_digest(state: TaurusState) -> str:
    payload = repr((state.generation, state.dna_revision, state.workload, state.shadow, state.history))
    return sha256(payload.encode()).hexdigest()


def verify_mirror(mirror: TaurusMirror) -> bool:
    """Software-level mirror gate; independence is a required assertion."""
    return mirror.independent and mirror.within_tolerance


def advance_taurus(
    state: TaurusState,
    *,
    verified_delta: TaurusDelta,
    mirror: TaurusMirror | None = None,
    next_workload: tuple[str, ...] = (),
    preserve_shadow: tuple[str, ...] = (),
    next_observations: tuple[TaurusObservation, ...] = (),
    prune: tuple[str, ...] = (),
    dna_revision: str | None = None,
    checkpoint: bool = True,
) -> TaurusReport:
    if state.generation < 0:
        raise ValueError("generation must be non-negative")

    reasons: list[str] = []
    shadow = tuple(dict.fromkeys((*state.shadow, *preserve_shadow, *verified_delta.unresolved)))
    history = tuple(dict.fromkeys((*state.history, state.dna_revision)))
    workload = tuple(dict.fromkeys(next_workload))
    observations = tuple(next_observations)
    pruned = tuple(dict.fromkeys(prune))

    if mirror is not None and not verify_mirror(mirror):
        reasons.append("mirror gate failed: independence or delta/epsilon gate failed")
        return TaurusReport(state, state, "STOP", tuple(reasons), pruned)

    if any(o.required and not o.detail.strip() for o in observations):
        reasons.append("required next observation is undefined")
        return TaurusReport(state, state, "STOP", tuple(reasons), pruned)

    can_continue = verified_delta.has_verified_change or bool(workload)
    if not can_continue:
        reasons.append("no verified change and no new workload frontier")
        return TaurusReport(state, state, "STOP", tuple(reasons), pruned)

    revision = dna_revision if dna_revision is not None else state.dna_revision
    next_checkpoints = state.checkpoints
    next_generation = state.generation + 1
    if checkpoint:
        cp = TaurusCheckpoint(
            revision=revision or f"gen-{next_generation}",
            generation=next_generation,
            dna_revision=revision,
            state_digest=state_digest(state),
        )
        next_checkpoints = (*state.checkpoints, cp)

    next_state = TaurusState(
        generation=next_generation,
        dna_revision=revision,
        workload=workload,
        shadow=shadow,
        history=history,
        checkpoints=next_checkpoints,
        last_delta=verified_delta,
        next_observations=observations,
        status="CONTINUE",
    )
    reasons.append("verified delta or new workload frontier available")
    if shadow:
        reasons.append("unresolved material preserved in shadow")
    if pruned:
        reasons.append("failed/nonproductive branches retained as prune records")
    return TaurusReport(state, next_state, "CONTINUE", tuple(reasons), pruned)


def rollback_taurus(state: TaurusState, checkpoint: TaurusCheckpoint) -> TaurusState:
    """Return to an exact previously recorded checkpoint without deleting history."""
    if checkpoint not in state.checkpoints:
        raise ValueError("checkpoint is not part of this Taurus state")
    return TaurusState(
        generation=checkpoint.generation,
        dna_revision=checkpoint.dna_revision,
        history=state.history + (f"ROLLBACK:{checkpoint.revision}",),
        checkpoints=state.checkpoints,
        status="ROLLBACK",
    )
