"""Command-line interface for the standalone ResonanceFS prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .errors import ResonanceFSError
from .policy import Phi1766Policy
from .repository import ResonanceRepository


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonancefs",
        description="Exact content snapshots with a separate spectral observability index.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize a repository")
    init.add_argument("repository", type=Path)
    init.add_argument("--policy", type=Path)

    commit = commands.add_parser("commit", help="Commit a source directory")
    commit.add_argument("repository", type=Path)
    commit.add_argument("source", type=Path)
    commit.add_argument("--message", default="")

    inspect = commands.add_parser("inspect", help="Verify a snapshot and all exact objects")
    inspect.add_argument("repository", type=Path)
    inspect.add_argument("snapshot", nargs="?")

    restore = commands.add_parser("restore", help="Restore a verified snapshot")
    restore.add_argument("repository", type=Path)
    restore.add_argument("snapshot")
    restore.add_argument("destination", type=Path)
    restore.add_argument("--overwrite", action="store_true")
    restore.add_argument("--include-quarantined", action="store_true")

    listing = commands.add_parser("list", help="List verified snapshot metadata")
    listing.add_argument("repository", type=Path)
    return parser


def run(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        if args.command == "init":
            policy = Phi1766Policy.load(args.policy) if args.policy else Phi1766Policy()
            repository = ResonanceRepository.initialize(args.repository, policy=policy)
            _emit(
                {
                    "ok": True,
                    "repository": str(repository.root),
                    "policy_id": repository.policy.policy_id,
                    "policy_hash": repository.policy.policy_hash,
                }
            )
            return 0

        repository = ResonanceRepository(args.repository)
        if args.command == "commit":
            commit_result = repository.commit_directory(args.source, message=args.message)
            _emit(
                {
                    "ok": True,
                    "snapshot_id": commit_result.snapshot_id,
                    "parent_snapshot_id": commit_result.parent_snapshot_id,
                    "file_count": commit_result.file_count,
                    "classifications": commit_result.classifications,
                }
            )
            return 0
        if args.command == "inspect":
            inspection = repository.inspect(args.snapshot)
            _emit(inspection)
            return 0 if inspection["ok"] else 2
        if args.command == "restore":
            restore_result = repository.restore(
                args.snapshot,
                args.destination,
                overwrite=args.overwrite,
                include_quarantined=args.include_quarantined,
            )
            _emit({"ok": True, **restore_result})
            return 0
        if args.command == "list":
            _emit({"ok": True, "snapshots": list(repository.list_snapshots())})
            return 0
    except (OSError, ValueError, KeyError, ResonanceFSError) as exc:
        _emit({"ok": False, "error": str(exc)})
        return 2
    return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
