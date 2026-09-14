# Windows workstation isolation preflight: STOP

Inspected before changing permissions: active checkout `b2663cb0d9296cb616865d93d549a44159867601`
with existing uncommitted work; publication checkout `95fb28cf76d73a8a687e64448e1822ab0869b7ba`.
No ACL, service, user account, canonical payload or checkpoint was changed by this audit.

EST: ordinary tool processes run as CodexSandboxOffline (SID ending -1003), member of
CodexSandboxUsers. That group has inherited Modify on the entire active workspace.
The agent owns the observed orbital record, baseline artifact and verifier source file.
The filesystem is NTFS. A separate owner-context inventory runs as dpstudio (-1000),
with Administrators marked deny-only: it is a filtered token, not an elevated administrator.
OpenSCManager(SC_MANAGER_CREATE_SERVICE) returned access denied, Windows error 5, from
that token. No dedicated UPI/CIP verifier service/account was found. The process inventory
found the VS Code Codex executable, but no persistent Python/node UPI server at that moment.

The Linux UID/capability/Landlock boundary, root-owned hierarchy and single-file rename
controls in PR #22 do not apply to this Windows session. NTFS permissions are available;
the required deployed trust separation is not. A second process with the same owner
authority is not an independent verifier. Agent access to owner-context escalation must
also be mediated by an external supervisor, not treated as a trusted prompt convention.

## Minimum design

An administrator provisions a dedicated protected directory, e.g. ProgramData/UPI-CIP,
outside the managed agent-write workspace, with protected DACLs and administrative ownership.
The writer receives Modify only on its own chamber; it must not own protected objects or
hold WRITE_DAC/WRITE_OWNER/DELETE on them or DELETE_CHILD on their parents. A dedicated
service identity reads candidates, owns promotion state and runs an immutable verifier
configuration; a separate recovery broker performs authorized writes after verified review.
The candidate writer must not control those service binaries, configurations or identities.
Existing open writer handles must be drained by the launcher before changing the boundary.

Each accepted version must register a protected, content-addressed checkpoint before its
accepted head becomes visible. The broker verifies its digest, schema/domain verdict and
trust chain before same-volume atomic replacement, with a serialized writer lifecycle and
explicit Windows failure/crash semantics. Neither that service nor Windows recovery has
been implemented or certified in this session. Avoid locking down the current dirty repo
without a migration plan: managed sandbox grants and agent-owned files defeat that shortcut.

## Executable evidence

Run the native probe from the SAME ordinary agent token:

```powershell
.venv\Scripts\python.exe .worktrees/publish/examples/feedback/windows_preflight.py .
```

The probe uses CreateFileW on actual existing targets, requests WRITE_DATA, DELETE and
WRITE_DAC, and checks parent DELETE_CHILD. It hashes payloads before/after and performs
no truncation/deletion. An allowed handle is a failed security requirement, not PASS.
Access denied is distinguished from missing files and other errors. These are native
access requests, not mocked permissions or completed destructive attack tests.

| Layer | Result |
| --- | --- |
| Application protection | PR #22 requires isolation policy; missing policy blocks |
| Windows filesystem | Broad agent authority; required production deny boundary absent |
| Verifier isolation | STOP: no dedicated service identity; installation access denied |
| Checkpoints | STOP: no protected production checkpoint deployment |
| Recovery | STOP: no Windows broker or atomic recovery verification |
| Software tests | Native token/access probes only; previous Linux tests do not apply |

Unperformed attacks: actual mutation of own deployed manifest, another deployed chamber,
trust root, verifier configuration, canonical records, checkpoints and promotion state.
The targets/services are not fully deployed; destroying current repository data would not
demonstrate a deny boundary. Next action: provision using a real elevated administrator and
configure the active writer launcher, then run all attacks on canaries governed by the exact
production DACLs, followed by Windows recovery fault injection. Until then production
isolation and promotion remain STOP/BLOCKED. 3I/ATLAS remains independently STOP/BLOCKED.

Windows references: [file access rights](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights),
[service access rights](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights).
