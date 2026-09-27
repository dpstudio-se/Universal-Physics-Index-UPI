"""Exact immutable storage; spectral profiles never replace these bytes."""

from __future__ import annotations

import os
import tempfile
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .errors import IntegrityError
from .hashing import digest_bytes, merkle_root


@dataclass(frozen=True)
class FileObject:
    size: int
    content_hash: str
    chunk_size: int
    chunks: tuple[str, ...]
    merkle_root: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> FileObject:
        return cls(
            size=int(value["size"]),
            content_hash=str(value["content_hash"]),
            chunk_size=int(value["chunk_size"]),
            chunks=tuple(str(item) for item in value["chunks"]),
            merkle_root=str(value["merkle_root"]),
        )


class ContentAddressedStore:
    """A SHA-256 object store with atomic writes and read-time verification."""

    def __init__(self, root: Path):
        self.root = root
        self.objects = root / "objects" / "sha256"
        self.objects.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_digest(digest: str) -> None:
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise IntegrityError("invalid SHA-256 object identity")

    def object_path(self, digest: str) -> Path:
        self._validate_digest(digest)
        return self.objects / digest[:2] / digest[2:]

    def put(self, data: bytes) -> str:
        digest = digest_bytes(data)
        destination = self.object_path(digest)
        if destination.exists():
            if digest_bytes(destination.read_bytes()) != digest:
                raise IntegrityError(f"existing object is corrupt: {digest}")
            return digest
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".incoming-", dir=destination.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if digest_bytes(temporary.read_bytes()) != digest:
                raise IntegrityError("temporary object changed before commit")
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        return digest

    def get(self, digest: str) -> bytes:
        path = self.object_path(digest)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise IntegrityError(f"missing object: {digest}") from exc
        if digest_bytes(data) != digest:
            raise IntegrityError(f"object hash mismatch: {digest}")
        return data

    def store_file(self, path: Path, *, chunk_size: int) -> FileObject:
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        content_digest = sha256()
        chunks: list[str] = []
        size = 0
        with path.open("rb") as handle:
            while True:
                block = handle.read(chunk_size)
                if not block:
                    break
                size += len(block)
                content_digest.update(block)
                chunks.append(self.put(block))
        return FileObject(
            size=size,
            content_hash=content_digest.hexdigest(),
            chunk_size=chunk_size,
            chunks=tuple(chunks),
            merkle_root=merkle_root(chunks),
        )

    def verify_file_object(self, file_object: FileObject) -> list[str]:
        errors: list[str] = []
        if merkle_root(file_object.chunks) != file_object.merkle_root:
            errors.append("chunk list does not match the recorded Merkle root")
        digest = sha256()
        observed_size = 0
        for chunk in file_object.chunks:
            try:
                data = self.get(chunk)
            except IntegrityError as exc:
                errors.append(str(exc))
                continue
            observed_size += len(data)
            digest.update(data)
        if observed_size != file_object.size:
            errors.append(
                f"file size mismatch: expected {file_object.size}, observed {observed_size}"
            )
        if digest.hexdigest() != file_object.content_hash:
            errors.append("file content hash does not match reconstructed chunks")
        return errors

    def read_file(self, file_object: FileObject) -> bytes:
        errors = self.verify_file_object(file_object)
        if errors:
            raise IntegrityError("; ".join(errors))
        return b"".join(self.get(chunk) for chunk in file_object.chunks)

    def write_file(
        self,
        file_object: FileObject,
        destination: Path,
        *,
        overwrite: bool = False,
    ) -> None:
        if destination.exists() and not overwrite:
            raise FileExistsError(destination)
        data = self.read_file(file_object)
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".restore-", dir=destination.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
