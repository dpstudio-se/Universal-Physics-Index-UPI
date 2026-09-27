"""Content-addressed quarantine for rejected batches. No execution."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any


def quarantine_hash(payload: dict[str, Any]) -> str:
    """Stable hash of a rejected payload."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def store_rejected(payload: dict[str, Any], directory: Path, reason: str) -> Path:
    """Write a rejected batch under *directory*. Never execute it."""
    directory.mkdir(parents=True, exist_ok=True)
    digest = quarantine_hash(payload)
    path = directory / f"{digest}.json"
    envelope = {
        "quarantine": True,
        "reason": reason,
        "content_hash": digest,
        "payload": payload,
        "verification_type": "software_test",
        "executable": False,
    }
    path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    return path
