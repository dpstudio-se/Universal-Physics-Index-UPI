"""Native Windows access probes. Never modify canonical payloads or their ACLs."""

import ctypes
import hashlib
import json
import os
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path


def probe(path: Path, access: int) -> dict:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    # OPEN_EXISTING, share read/write/delete, backup semantics for directory handles.
    handle = kernel.CreateFileW(str(path), access, 7, None, 3, 0x02000000, None)
    error = ctypes.get_last_error()
    granted = handle != ctypes.c_void_p(-1).value
    if granted:
        kernel.CloseHandle(handle)
    return {
        "access_mask": access,
        "granted": granted,
        "winerror": 0 if granted else error,
        "outcome": "FAIL" if granted else "PASS" if error == 5 else "UNKNOWN",
    }


def main():
    if sys.platform != "win32":
        print(json.dumps({"state": "STOP", "reason": "Windows runtime required"}))
        return 1
    root = Path(sys.argv[1]).resolve()
    targets = {
        "existing_baseline_not_deployed_cip_manifest": "examples/feedback/canonical_baseline.json",
        "verifier_source": "src/upi/chamber.py",
        "canonical_upi": "data/mechanics/hyperbolic_orbit.json",
        "other_worktree_candidate": ".worktrees/publish/examples/feedback/candidates/3i_atlas_upi_case.json",
    }
    records = {}
    for name, relative in targets.items():
        path = root / relative
        if not path.is_file():
            records[name] = {"outcome": "UNKNOWN", "reason": "Not present"}
            continue
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        records[name] = {
            "path": relative,
            "before_sha256": before,
            "rights": {
                label: probe(path, mask)
                for label, mask in [("write_data", 2), ("delete", 0x10000), ("write_dacl", 0x40000)]
            },
            "parent_delete_child": probe(path.parent, 0x40),
            "after_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    result = {
        "state": "STOP",
        "promotion": "BLOCKED",
        "verification_type": "software_test",
        "identity": subprocess.check_output(["whoami", "/user", "/fo", "csv", "/nh"])
        .decode()
        .strip(),
        "pid": os.getpid(),
        "repo": str(root),
        "head": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
        .decode()
        .strip(),
        "probe_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": records,
        "scope": "Actual Windows OPEN_EXISTING access requests from current token; no write/delete executed.",
        "unavailable": [
            "protected production CIP manifest/trust configuration",
            "dedicated verifier service identity and protected executable",
            "production checkpoint store and recovery service",
            "verifier-controlled production promotion state",
            "chamber-only active agent launch policy",
        ],
        "next_action": "Use an authorized unfiltered administrator session to provision a protected "
        "Windows service boundary and relaunch the writer with chamber-only authority; "
        "then exercise mutation attacks on administrator-created canaries at each real target.",
    }
    print(json.dumps(result, indent=2))
    return 1  # No path from this preflight to a production-isolation PASS.


if __name__ == "__main__":
    sys.exit(main())
