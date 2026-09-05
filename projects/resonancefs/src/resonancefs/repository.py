"""Snapshot repository joining exact storage to spectral observability."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import IntegrityError, ResonanceFSError
from .hashing import canonical_json, digest_json
from .policy import Phi1766Policy
from .spectral import SpectralProfile, coherence, profile_bytes, profile_file
from .storage import ContentAddressedStore, FileObject

SNAPSHOT_FORMAT = "resonancefs-snapshot"
SNAPSHOT_VERSION = "1.0.0"


@dataclass(frozen=True)
class SnapshotResult:
    snapshot_id: str
    parent_snapshot_id: str | None
    file_count: int
    classifications: dict[str, int]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _safe_relative(path: str) -> PurePosixPath:
    relative = PurePosixPath(path)
    if relative.is_absolute() or not relative.parts or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise IntegrityError(f"unsafe snapshot path: {path!r}")
    return relative


class ResonanceRepository:
    """A local immutable snapshot and content-addressed object repository."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.policy_path = self.root / "policy.json"
        self.snapshots = self.root / "snapshots"
        self.head_path = self.root / "HEAD"
        if not self.policy_path.is_file():
            raise ResonanceFSError(f"not a ResonanceFS repository: {self.root}")
        self.policy = Phi1766Policy.load(self.policy_path)
        self.store = ContentAddressedStore(self.root)
        self.snapshots.mkdir(parents=True, exist_ok=True)

    @classmethod
    def initialize(
        cls, root: Path, *, policy: Phi1766Policy | None = None
    ) -> ResonanceRepository:
        root = root.resolve()
        selected = policy or Phi1766Policy()
        policy_path = root / "policy.json"
        if policy_path.exists():
            existing = Phi1766Policy.load(policy_path)
            if existing.policy_hash != selected.policy_hash:
                raise ResonanceFSError("repository already has a different Phi1766 policy")
        else:
            _atomic_write(
                policy_path,
                (canonical_json(selected.to_dict()) + "\n").encode("utf-8"),
            )
        (root / "snapshots").mkdir(parents=True, exist_ok=True)
        return cls(root)

    @property
    def head(self) -> str | None:
        if not self.head_path.is_file():
            return None
        value = self.head_path.read_text(encoding="ascii").strip()
        return value or None

    def _snapshot_path(self, snapshot_id: str) -> Path:
        if len(snapshot_id) != 64 or any(
            character not in "0123456789abcdef" for character in snapshot_id
        ):
            raise IntegrityError("invalid snapshot identity")
        return self.snapshots / f"{snapshot_id}.json"

    def load_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        path = self._snapshot_path(snapshot_id)
        try:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise IntegrityError(f"missing snapshot: {snapshot_id}") from exc
        if not isinstance(snapshot, dict):
            raise IntegrityError("snapshot must be a JSON object")
        recorded_id = snapshot.get("snapshot_id")
        body = {key: value for key, value in snapshot.items() if key != "snapshot_id"}
        if recorded_id != snapshot_id or digest_json(body) != snapshot_id:
            raise IntegrityError(f"snapshot hash mismatch: {snapshot_id}")
        if snapshot.get("format") != SNAPSHOT_FORMAT:
            raise IntegrityError("unknown snapshot format")
        if snapshot.get("version") != SNAPSHOT_VERSION:
            raise IntegrityError("unsupported snapshot version")
        policy_value = snapshot.get("policy")
        if not isinstance(policy_value, dict):
            raise IntegrityError("snapshot has no embedded policy")
        try:
            embedded_policy = Phi1766Policy.from_dict(policy_value)
        except ResonanceFSError as exc:
            raise IntegrityError(str(exc)) from exc
        if embedded_policy.policy_hash != snapshot.get("policy_hash"):
            raise IntegrityError("snapshot policy hash mismatch")
        if not isinstance(snapshot.get("files"), dict):
            raise IntegrityError("snapshot files must be an object")
        return snapshot

    def _source_files(self, source: Path) -> list[Path]:
        source = source.resolve()
        if not source.is_dir():
            raise ResonanceFSError(f"source is not a directory: {source}")
        files: list[Path] = []
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ResonanceFSError(f"symbolic links are not accepted: {path}")
            if not path.is_file():
                continue
            resolved = path.resolve()
            try:
                resolved.relative_to(self.root)
            except ValueError:
                files.append(resolved)
        return files

    def commit_directory(
        self,
        source: Path,
        *,
        message: str = "",
        created_at: str | None = None,
    ) -> SnapshotResult:
        """Commit exact bytes and derived profiles from a directory."""
        source = source.resolve()
        parent_id = self.head
        parent = self.load_snapshot(parent_id) if parent_id else None
        parent_files = (
            parent["files"]
            if parent is not None and parent["policy_hash"] == self.policy.policy_hash
            else {}
        )
        records: dict[str, dict[str, Any]] = {}
        counts = {"BASELINE": 0, "NORMAL": 0, "INSPECT": 0, "QUARANTINE": 0}

        for path in self._source_files(source):
            relative = path.relative_to(source).as_posix()
            _safe_relative(relative)
            exact = self.store.store_file(path, chunk_size=self.policy.chunk_size)
            spectral = profile_file(
                path,
                bins=self.policy.spectral_bins,
                max_samples=self.policy.max_samples,
            )
            comparison: dict[str, Any]
            old_record = parent_files.get(relative)
            if isinstance(old_record, dict) and isinstance(old_record.get("spectral"), dict):
                old_profile = SpectralProfile.from_dict(old_record["spectral"])
                score = coherence(
                    old_profile,
                    spectral,
                    amplitude_weight=self.policy.amplitude_weight,
                    histogram_weight=self.policy.histogram_weight,
                    phase_weight=self.policy.phase_weight,
                )
                classification = self.policy.classify(score)
                comparison = {
                    "baseline_snapshot_id": parent_id,
                    "coherence": score,
                    "classification": classification,
                }
            else:
                classification = "BASELINE"
                comparison = {
                    "baseline_snapshot_id": None,
                    "coherence": None,
                    "classification": classification,
                }
            counts[classification] += 1
            records[relative] = {
                "exact": exact.to_dict(),
                "spectral": spectral.to_dict(),
                "comparison": comparison,
            }

        body = {
            "format": SNAPSHOT_FORMAT,
            "version": SNAPSHOT_VERSION,
            "status": "prototype",
            "created_at": created_at or _utcnow(),
            "message": message,
            "parent_snapshot_id": parent_id,
            "policy": self.policy.to_dict(),
            "policy_hash": self.policy.policy_hash,
            "files": records,
        }
        snapshot_id = digest_json(body)
        document = {**body, "snapshot_id": snapshot_id}
        snapshot_path = self._snapshot_path(snapshot_id)
        if not snapshot_path.exists():
            _atomic_write(
                snapshot_path,
                (canonical_json(document) + "\n").encode("utf-8"),
            )
        _atomic_write(self.head_path, f"{snapshot_id}\n".encode("ascii"))
        return SnapshotResult(
            snapshot_id=snapshot_id,
            parent_snapshot_id=parent_id,
            file_count=len(records),
            classifications=counts,
        )

    def inspect(self, snapshot_id: str | None = None) -> dict[str, Any]:
        selected = snapshot_id or self.head
        if selected is None:
            raise ResonanceFSError("repository has no snapshots")
        snapshot = self.load_snapshot(selected)
        snapshot_policy = Phi1766Policy.from_dict(snapshot["policy"])
        errors: list[dict[str, str]] = []
        files = snapshot["files"]
        for relative, record in files.items():
            try:
                _safe_relative(relative)
                exact = FileObject.from_dict(record["exact"])
                exact_errors = self.store.verify_file_object(exact)
                errors.extend(
                    {"path": relative, "layer": "exact", "error": error}
                    for error in exact_errors
                )
                if not exact_errors:
                    rebuilt = profile_bytes(
                        self.store.read_file(exact),
                        bins=snapshot_policy.spectral_bins,
                        max_samples=snapshot_policy.max_samples,
                    )
                    recorded_profile = SpectralProfile.from_dict(record["spectral"])
                    if rebuilt.to_dict() != recorded_profile.to_dict():
                        errors.append(
                            {
                                "path": relative,
                                "layer": "spectral",
                                "error": "spectral profile does not match exact bytes",
                            }
                        )
            except (KeyError, TypeError, ValueError, IntegrityError) as exc:
                errors.append({"path": str(relative), "layer": "manifest", "error": str(exc)})
        return {
            "snapshot_id": selected,
            "ok": not errors,
            "file_count": len(files),
            "errors": errors,
        }

    def restore(
        self,
        snapshot_id: str,
        destination: Path,
        *,
        overwrite: bool = False,
        include_quarantined: bool = False,
    ) -> dict[str, Any]:
        """Restore only after every exact object in the snapshot verifies."""
        report = self.inspect(snapshot_id)
        if not report["ok"]:
            raise IntegrityError("snapshot failed inspection and cannot be restored")
        snapshot = self.load_snapshot(snapshot_id)
        destination = destination.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        restored: list[str] = []
        skipped: list[str] = []
        for relative, record in snapshot["files"].items():
            classification = record["comparison"]["classification"]
            if classification == "QUARANTINE" and not include_quarantined:
                skipped.append(relative)
                continue
            safe = _safe_relative(relative)
            target = destination.joinpath(*safe.parts)
            resolved_target = target.resolve(strict=False)
            if os.path.commonpath((str(destination), str(resolved_target))) != str(destination):
                raise IntegrityError(f"restore path escapes destination: {relative}")
            self.store.write_file(
                FileObject.from_dict(record["exact"]),
                target,
                overwrite=overwrite,
            )
            restored.append(relative)
        return {
            "snapshot_id": snapshot_id,
            "restored": restored,
            "skipped_quarantined": skipped,
        }

    def list_snapshots(self) -> Iterable[dict[str, Any]]:
        """Yield verified snapshot summaries from newest filename-independent metadata."""
        snapshots = []
        for path in self.snapshots.glob("*.json"):
            snapshot_id = path.stem
            snapshot = self.load_snapshot(snapshot_id)
            snapshots.append(
                {
                    "snapshot_id": snapshot_id,
                    "created_at": snapshot["created_at"],
                    "parent_snapshot_id": snapshot["parent_snapshot_id"],
                    "message": snapshot["message"],
                    "file_count": len(snapshot["files"]),
                    "head": snapshot_id == self.head,
                }
            )
        yield from sorted(snapshots, key=lambda item: item["created_at"])
