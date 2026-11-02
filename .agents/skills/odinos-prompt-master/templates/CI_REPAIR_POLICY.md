# CI repair policy — OdinOS / UPI

## Allowed automation

- Read logs, branch metadata, diffs, and public prompt templates.
- Run checks on a local checkout or disposable CI workspace.
- Propose narrowly scoped patches with explanation and citations to logs.
- Open a PR only when repository permissions and user instructions permit it.

## Mandatory stop conditions

- No source of truth for a proposed change.
- Required scientific record schema is missing or invalid.
- The proposed patch weakens validation, bypasses a failing gate, or silently rewrites scientific evidence.
- A change would access secrets, modify branch protection, push to `main`, or merge without explicit approval.
- Repeated same error, no progress, or more than three fix cycles.

## Evidence report format

- Branch / commit SHA / workflow run URL
- Failing job and exact failing step
- Error text and file:line
- Root cause (confirmed vs hypothesis)
- Minimal patch and rationale
- Commands run and exit codes
- Remaining risks and explicitly unvalidated records
- PR URL (if created); merge status separately verified
