"""Live .dna_minne reader/writer for UPI DNA events.

Memory is append-only data, never scientific authority.
""" 
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from threading import Lock
from typing import Any, Iterator


@dataclass(frozen=True)
class DNAMemoryEvent:
    id: str
    timestamp: str
    type: str
    operation: str
    source: str
    payload: dict[str, Any]
    status: str
    provenance: str
    sha256: str


class DNAWriter:
    """Append-only writer with atomic line replacement and integrity hashing."""

    def __init__(self, root: str | Path = ".dna_minne") -> None:
        self.root = Path(root)
        self.path = self.root / "memory.jsonl"
        self.index = self.root / "index.json"
        self._lock = Lock()

    @staticmethod
    def _canonical(event: dict[str, Any]) -> bytes:
        body = {k: v for k, v in event.items() if k != "sha256"}
        return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

    def write(
        self,
        payload: dict[str, Any],
        *,
        source: str = "UPI",
        status: str = "DER",
        provenance: str = "runtime",
    ) -> DNAMemoryEvent:
        if status not in {"EST", "DER", "TEST", "HYP", "STOP", "ERR", "SYM"}:
            raise ValueError(f"invalid DNA status: {status}")
        self.root.mkdir(parents=True, exist_ok=True)
        with self._lock:
            stamp = datetime.now(timezone.utc).isoformat()
            event = {
                "id": hashlib.sha256(f"{stamp}|{source}|{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()[:16],
                "timestamp": stamp,
                "type": "DNA_MEMORY",
                "operation": "write",
                "source": source,
                "payload": payload,
                "status": status,
                "provenance": provenance,
            }
            event["sha256"] = hashlib.sha256(self._canonical(event)).hexdigest()
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            self._reindex()
            return DNAMemoryEvent(**event)

    def _reindex(self) -> None:
        records = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        index = {
            "count": len(records),
            "latest_id": records[-1]["id"] if records else None,
            "latest_timestamp": records[-1]["timestamp"] if records else None,
        }
        tmp = self.index.with_suffix(".tmp")
        tmp.write_text(json.dumps(index, indent=2), encoding="utf-8")
        tmp.replace(self.index)


class DNAReader:
    """Read-only view of live DNA memory with integrity verification."""

    def __init__(self, root: str | Path = ".dna_minne") -> None:
        self.path = Path(root) / "memory.jsonl"

    @staticmethod
    def _canonical(event: dict[str, Any]) -> bytes:
        body = {k: v for k, v in event.items() if k != "sha256"}
        return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

    def read(self, limit: int | None = None) -> list[DNAMemoryEvent]:
        if not self.path.exists():
            return []
        rows = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if limit is not None:
            rows = rows[-limit:]
        out = []
        for row in rows:
            if row.get("type") != "DNA_MEMORY" or row.get("operation") != "write":
                raise ValueError("invalid DNA memory event")
            expected = hashlib.sha256(self._canonical(row)).hexdigest()
            if row.get("sha256") != expected:
                raise ValueError(f"DNA integrity failure: {row.get('id')}")
            out.append(DNAMemoryEvent(**row))
        return out

    def latest(self) -> DNAMemoryEvent | None:
        rows = self.read(1)
        return rows[0] if rows else None

    def stream(self, poll_seconds: float = 0.25) -> Iterator[DNAMemoryEvent]:
        import time
        seen = 0
        while True:
            rows = self.read()
            for row in rows[seen:]:
                yield row
            seen = len(rows)
            time.sleep(poll_seconds)
