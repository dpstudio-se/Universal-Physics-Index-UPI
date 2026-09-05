"""Canonical serialization, cryptographic identities and Merkle roots."""

from __future__ import annotations

import json
from collections.abc import Iterable
from hashlib import sha256
from typing import Any


def canonical_json(value: Any) -> str:
    """Encode JSON deterministically for content identity."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_json(value).encode("utf-8"))


def merkle_root(chunk_hashes: Iterable[str]) -> str:
    """Return a domain-separated binary Merkle root for ordered chunk hashes."""
    level = [sha256(b"\x00" + bytes.fromhex(item)).digest() for item in chunk_hashes]
    if not level:
        return sha256(b"resonancefs:empty").hexdigest()
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            sha256(b"\x01" + level[index] + level[index + 1]).digest()
            for index in range(0, len(level), 2)
        ]
    return level[0].hex()
