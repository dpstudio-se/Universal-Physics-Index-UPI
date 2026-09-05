import json
from pathlib import Path

import pytest

from resonancefs.cli import run
from resonancefs.errors import IntegrityError, PolicyError
from resonancefs.hashing import digest_bytes, merkle_root
from resonancefs.policy import Phi1766Policy
from resonancefs.repository import ResonanceRepository
from resonancefs.spectral import coherence, profile_bytes, profile_file

T0 = "2026-09-03T12:00:00Z"


def test_exact_identity_and_spectral_identity_are_separate() -> None:
    data = bytes(range(256)) * 16
    changed = bytes(255 - value for value in data)
    original_profile = profile_bytes(data)
    same_profile = profile_bytes(data)
    changed_profile = profile_bytes(changed)

    assert digest_bytes(data) != digest_bytes(changed)
    assert coherence(original_profile, same_profile) == pytest.approx(1.0)
    assert 0 <= coherence(original_profile, changed_profile) < 1


def test_profile_file_matches_profile_bytes(tmp_path: Path) -> None:
    data = bytes((index * 37) % 256 for index in range(10_000))
    path = tmp_path / "sample.bin"
    path.write_bytes(data)

    assert profile_file(path).to_dict() == profile_bytes(data).to_dict()


def test_merkle_root_commits_chunk_order() -> None:
    first = digest_bytes(b"first")
    second = digest_bytes(b"second")

    assert merkle_root([first, second]) != merkle_root([second, first])
    assert merkle_root([]) == merkle_root([])


def test_snapshot_round_trip_and_verified_restore(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "notes.txt").write_text("resonance\n", encoding="utf-8")
    (source / "empty.bin").write_bytes(b"")
    repository = ResonanceRepository.initialize(tmp_path / "store")

    result = repository.commit_directory(source, message="baseline", created_at=T0)
    report = repository.inspect(result.snapshot_id)
    restored = tmp_path / "restored"
    restore_report = repository.restore(result.snapshot_id, restored)

    assert result.file_count == 2
    assert result.classifications["BASELINE"] == 2
    assert report == {
        "snapshot_id": result.snapshot_id,
        "ok": True,
        "file_count": 2,
        "errors": [],
    }
    assert (restored / "notes.txt").read_text(encoding="utf-8") == "resonance\n"
    assert (restored / "empty.bin").read_bytes() == b""
    assert sorted(restore_report["restored"]) == ["empty.bin", "notes.txt"]


def test_phi1766_classifies_drift_and_quarantine_is_not_restored_by_default(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    path = source / "payload.bin"
    original = bytes(range(256)) * 32
    path.write_bytes(original)
    repository = ResonanceRepository.initialize(tmp_path / "store")
    baseline = repository.commit_directory(source, created_at=T0)

    unchanged = repository.commit_directory(
        source, created_at="2026-09-03T12:00:01Z"
    )
    unchanged_record = repository.load_snapshot(unchanged.snapshot_id)["files"][
        "payload.bin"
    ]
    assert unchanged_record["comparison"]["classification"] == "NORMAL"
    assert unchanged_record["comparison"]["coherence"] == pytest.approx(1.0)

    path.write_bytes(bytes(255 - value for value in original))
    drifted = repository.commit_directory(
        source, created_at="2026-09-03T12:00:02Z"
    )
    record = repository.load_snapshot(drifted.snapshot_id)["files"]["payload.bin"]

    assert baseline.parent_snapshot_id is None
    assert record["comparison"]["classification"] == "QUARANTINE"
    restored = repository.restore(drifted.snapshot_id, tmp_path / "quarantine-restore")
    assert restored["restored"] == []
    assert restored["skipped_quarantined"] == ["payload.bin"]


def test_corrupt_chunk_blocks_inspection_and_restore(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "payload.bin").write_bytes(b"trusted bytes")
    repository = ResonanceRepository.initialize(tmp_path / "store")
    snapshot = repository.commit_directory(source, created_at=T0)
    record = repository.load_snapshot(snapshot.snapshot_id)["files"]["payload.bin"]
    chunk_hash = record["exact"]["chunks"][0]
    repository.store.object_path(chunk_hash).write_bytes(b"corrupt")

    report = repository.inspect(snapshot.snapshot_id)

    assert report["ok"] is False
    assert any("hash mismatch" in item["error"] for item in report["errors"])
    with pytest.raises(IntegrityError, match="failed inspection"):
        repository.restore(snapshot.snapshot_id, tmp_path / "blocked")


def test_snapshot_manifest_tampering_is_detected(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("one", encoding="utf-8")
    repository = ResonanceRepository.initialize(tmp_path / "store")
    snapshot = repository.commit_directory(source, created_at=T0)
    manifest_path = repository.snapshots / f"{snapshot.snapshot_id}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["message"] = "tampered"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(IntegrityError, match="snapshot hash mismatch"):
        repository.load_snapshot(snapshot.snapshot_id)


def test_invalid_phi1766_thresholds_fail_closed() -> None:
    with pytest.raises(PolicyError, match="thresholds"):
        Phi1766Policy(inspect_below=0.5, quarantine_below=0.8)


def test_cli_init_commit_inspect_and_restore(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "hello.txt").write_text("hello", encoding="utf-8")
    store = tmp_path / "store"

    assert run(["init", str(store)]) == 0
    capsys.readouterr()
    assert run(["commit", str(store), str(source), "--message", "cli test"]) == 0
    commit_output = json.loads(capsys.readouterr().out)
    snapshot_id = commit_output["snapshot_id"]
    assert run(["inspect", str(store), snapshot_id]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True
    destination = tmp_path / "destination"
    assert run(["restore", str(store), snapshot_id, str(destination)]) == 0
    capsys.readouterr()
    assert (destination / "hello.txt").read_text(encoding="utf-8") == "hello"
