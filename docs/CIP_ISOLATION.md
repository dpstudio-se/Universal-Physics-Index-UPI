# CIP Linux isolation backend and executable boundary fixture

The backend `src/upi/cip_linux.sh` supplies guarded writer/verifier launch and recovery
primitives. The test provisioner `examples/feedback/cip_linux_boundary.sh` creates a
fresh installation under Linux `/tmp`; it does not change Windows ACLs, host users,
canonical UPI, 3I/ATLAS or production trust roots. No accounts are created: reserved
numeric UIDs 41001 (writer A), 41002 (writer B) and 41003 (verifier) are used in children.

The trusted directories and policy/checkpoint files are owned by root. Each candidate
is a separate UID-owned file in a root-owned directory. The writer's Landlock domain
allows writes/truncation only on its own candidate inode, with read/execute access
elsewhere. All capabilities and supplementary groups are dropped, and no-new-privs
prevents privilege gain on exec. The verifier has a different UID and a read/execute-only
Landlock domain. Neither inherits the broker lock descriptor. Missing kernel support,
bad policy digest, unexpected ownership/modes, symbolic links or candidate hard links
fail closed. These controls are OS-enforced; they are not Python mocks of PermissionError.

## Recovery and its exact scope

A checkpoint is an immutable-by-agent, root-owned payload plus its protected expected
SHA-256. The root broker validates ownership/modes and checksum, rejects recovery while
writer UID processes exist, stages and hashes the complete payload on the same filesystem,
syncs the staging file and atomically renames it over the candidate. The root-owned parent
prevents candidate symlink substitution. Failure before rename leaves the candidate intact.
The fixture demonstrates invalid-checkpoint rejection with unchanged candidate bytes and
successful recovery with an exact post-restore hash match. No candidate is used as fallback.

This is single-file atomic visibility, not a multi-file transaction or a tested guarantee
of directory-entry durability through sudden power loss. The trusted launcher must hold
the same exclusive broker lock for ALL writer launches and recovery, and reserve the UIDs
for this installation. It must not reuse them for unrelated processes. A restored file may
be changed again by an authorized writer after a new launch; that is a new candidate edit.
Root remains trusted and can change the fixture by design. A root compromise, kernel exploit,
or candidate access to the host Docker/WSL management interface is outside this boundary.

The fixture provisions one synthetic accepted checkpoint. Production acceptance must first
complete CIP/domain/human gates and durably store the verified checkpoint and protected head
before advertising an accepted state. No production checkpoint-acceptance service or migration
of existing chambers has been performed here. Do not infer scientific acceptance from recovery.

## Executable tests and receipts

From this Windows workspace, with authorized WSL access, run:

```powershell
.venv\Scripts\python.exe examples/feedback/run_isolation.py
.venv\Scripts\python.exe examples/feedback/run_validation.py
```

The first runner creates a separate receipt under `examples/feedback/runs/*-isolation/`.
It records the actual kernel, command, exact 19 test names, raw log hash, candidate/source/
code binding and input-drift check. It fails if the exact expected controls did not execute.
The second runner records the full existing application suites with the same input binding
when no inputs change. Both are `verification_type: software_test`; neither is an independent
signed attestation. Linux fixture results must not be relabeled as Windows host isolation.

Controls attempt writes to another chamber, own manifest, verifier rules, trust configuration,
promotion state and checkpoint, checkpoint deletion, symlink escape, rule chmod, writes outside
scope and verifier writes. Positive controls verify allowed candidate writes and distinct UIDs.
Recovery and permission fault injection are performed by the trusted test controller only.

## Separate reported layers

| Layer | What the tests establish | Remaining boundary |
| --- | --- | --- |
| Repository integrity | Hash-bound code/test inputs and existing CIP checks | Workspace remains agent-writable |
| Chamber isolation | Actual UID/DAC/Landlock denied writes in fresh Linux fixture | Active Codex session is not launched inside it |
| Verifier isolation | Different UID; candidate write denied; writer cannot modify protected rules | No independent production verifier/attestation identity installed |
| Recovery integrity | Validated single-file atomic replacement; invalid snapshot leaves candidate unchanged | Production accepted-state storage/registration and power-failure testing absent |
| Application behavior | Promotion requires chamber_integrity AND chamber_isolation policy checks | No production isolation policy installed; missing check blocks |

Production isolation remains **STOP / BLOCKED**. Next action: provision a dedicated protected
Linux installation and supervisor, copy/pin the reviewed broker and verifier there, reserve
service identities, remove agent access to the supervisor and host management plane, enforce
the common lifecycle lock, and rerun these attacks using the actual deployed candidate runner.
Bind the resulting deployment evidence in server-owned `chamber_isolation` policy. Do not
use a fixture PASS or a client-supplied flag as that policy. This requires a deployment target
and identity configuration; no such production target has been specified or modified.

3I/ATLAS remains subject to its independent scientific/canonical STOP gates. No promotion occurs.
