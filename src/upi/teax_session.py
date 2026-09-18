"""T€@X core selector and bounded session lock.

Software access control only. It is not a physical law or measurement.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib, hmac, secrets, time

UNSIGNED_SESSION_SECONDS = 300
TEAX_SESSION_SECONDS = 1800

class SessionState(str, Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    EXPIRED = "EXPIRED"
    LOCKED = "LOCKED"

class CoreId(str, Enum):
    HKTITAN = "hktitan-universal-physics"
    TEAX = "teax-universal-physics"
    TEAX_PLUS = "teax-universal-physics-plus"

@dataclass(frozen=True)
class Session:
    session_id: str
    core: CoreId
    issued_at: float
    expires_at: float
    tag_verified: bool

@dataclass(frozen=True)
class SessionStatus:
    state: SessionState
    remaining_seconds: int
    core: CoreId

class TeaxTagVerifier:
    """Server-side HMAC tag verification. Keep the secret outside the repo."""
    def __init__(self, secret: bytes):
        if not secret:
            raise ValueError("TEAX tag secret must not be empty")
        self._secret = secret
    def issue(self, subject: str) -> str:
        nonce = secrets.token_urlsafe(24)
        payload = f"{subject}:{nonce}".encode()
        sig = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return f"{nonce}.{sig}"
    def verify(self, subject: str, tag: str) -> bool:
        try:
            nonce, signature = tag.split(".", 1)
        except ValueError:
            return False
        if not nonce or not signature:
            return False
        payload = f"{subject}:{nonce}".encode()
        expected = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

class CoreSelector:
    DEFAULT_CORE = CoreId.TEAX
    @classmethod
    def select(cls, requested: str | None) -> CoreId:
        if not requested:
            return cls.DEFAULT_CORE
        try:
            return CoreId(requested)
        except ValueError as exc:
            raise ValueError(f"unknown core: {requested}") from exc

class SessionGuard:
    """Monotonic-clock session state machine: 5 min unsigned, 30 min verified."""
    def __init__(self, clock=time.monotonic):
        self._clock = clock
    def start(self, core: CoreId, *, tag_verified=False, now=None) -> Session:
        issued = self._clock() if now is None else now
        lifetime = TEAX_SESSION_SECONDS if tag_verified else UNSIGNED_SESSION_SECONDS
        return Session(secrets.token_urlsafe(18), core, issued, issued + lifetime, tag_verified)
    def status(self, session: Session, now=None) -> SessionStatus:
        current = self._clock() if now is None else now
        remaining = max(0, int(session.expires_at - current))
        state = SessionState.ACTIVE if remaining > 0 else SessionState.LOCKED
        return SessionStatus(state, remaining, session.core)
    def require_active(self, session: Session, now=None) -> SessionStatus:
        status = self.status(session, now)
        if status.state is SessionState.LOCKED:
            raise PermissionError("UPI session expired; start a new session")
        return status
