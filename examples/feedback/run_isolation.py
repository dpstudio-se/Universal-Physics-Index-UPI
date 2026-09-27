"""Run actual Linux boundary controls and retain a version-bound, separate receipt."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from upi.atlas_gates import binding_snapshot, digest_json, file_hash

TESTS = [
    "candidate_write_allowed",
    "other_chamber",
    "own_manifest",
    "verifier_rules",
    "trust_configuration",
    "promotion_state",
    "checkpoint_replacement",
    "checkpoint_delete",
    "symlink_escape",
    "rules_permission_change",
    "write_outside_scope",
    "distinct_identities",
    "verifier_read_only",
    "invalid_checkpoint_no_change",
    "validated_atomic_recovery",
    "active_writer_recovery_stop",
    "missing_checkpoint_stop",
    "altered_verifier_stop",
    "unsafe_permissions_stop",
]


def main():
    repo = Path(__file__).resolve().parents[2]
    binding = binding_snapshot(repo)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = repo / "examples/feedback/runs" / (stamp + "-isolation")
    output.mkdir(parents=True)
    scripts = [repo / "examples/feedback/cip_linux_boundary.sh", repo / "src/upi/cip_linux.sh"]
    if sys.platform == "win32":
        linux_paths = ["/mnt/host/" + p.drive[0].lower() + p.as_posix()[2:] for p in scripts]
        command = ["wsl", "-d", "docker-desktop", "--", "sh", *linux_paths]
        version_command = ["wsl", "-d", "docker-desktop", "--", "uname", "-a"]
    else:
        command = ["sh", *map(str, scripts)]
        version_command = ["uname", "-a"]
    run = subprocess.run(command, capture_output=True, timeout=120)
    log = output / "boundary.log"
    log.write_bytes(run.stdout + run.stderr)
    names = [
        line[5:]
        for line in run.stdout.decode("utf-8", errors="replace").splitlines()
        if line.startswith("PASS ")
    ]
    unchanged = binding_snapshot(repo) == binding
    passed = run.returncode == 0 and names == TESTS and unchanged
    receipt = {
        "verification_type": "software_test",
        "binding": binding,
        "binding_sha256": digest_json(binding),
        "inputs_unchanged": unchanged,
        "state": "PASS" if passed else "STOP",
        "command": command,
        "exit_code": run.returncode,
        "exact_test_set": TESTS,
        "test_set_sha256": digest_json(TESTS),
        "results": [
            {
                "nodeid": name,
                "outcome": "passed",
                "verification_type": "software_test",
                "binding_sha256": digest_json(binding),
            }
            for name in names
        ],
        "log_path": log.relative_to(repo).as_posix(),
        "log_sha256": file_hash(log),
        "kernel": subprocess.check_output(version_command)
        .decode("utf-8", errors="replace")
        .strip(),
        "scope": "Fresh Linux fixture: DAC, separate UIDs, Landlock and single-file atomic rename.",
        "production_isolation": "STOP",
        "promotion": "BLOCKED",
        "trust_scope": "Local execution record; not an independently signed deployment attestation.",
    }
    path = output / "isolation_receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "state": receipt["state"],
                "tests": len(names),
                "receipt": str(path),
                "binding": receipt["binding_sha256"],
            }
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
