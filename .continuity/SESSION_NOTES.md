# Session Notes

## Goals
- Make the SFTP updater work on Windows and Linux.

## Blockers
- `continuity` CLI not on PATH; decision not logged to decisions.jsonl.
- Publishing (SFTP) not attempted: needs the user's password; README says auth was rejected earlier.

## Key Decisions
- Installed uv 0.12.23 to C:\Users\dpstudio\.local\bin (not on PATH in Git Bash; PowerShell from Git Bash also lacks PATHEXT, so set it before running Update-UPI.ps1).
- Both uv calls in Update-UPI.ps1 and update-upi.sh were missing `--with jsonschema`, so build-only crashed on import; fixed.
- `-BuildOnly` now builds dist/upi + dist/upi-webbhotell-v1.zip; tests/test_static_site.py: 14 passed (use --basetemp=dist/.pytest-tmp, %TEMP% pytest dir is permission-denied).
- Update-UPI.ps1 now finds the venv python on both Windows and Linux; added update-upi.sh (uv, else python3 + paramiko) and a README section. site.py was already pure Python. Credentials come from UPI_SFTP_PASSWORD or a prompt. Uncommitted.
- README.md and README.sv.md rewritten: new "AI / AGI / ASI / LLM remote" and "Research mode with UPI as the core" sections, update-upi.sh, /api/remote and /llms.txt in quick start. Why: give any model one vendor-neutral discovery entry point with UPI as the source of truth in research mode.
- Added discovery layer only (no new write path, no scheduler/daemon/public-API claims): src/upi/remote.py, GET /api/remote, /.well-known/upi-remote.json, /llms.txt in server.py, openapi.yaml entries, docs/UPI_AI_REMOTE.md, root llms.txt (generated from render_llms_txt()), tests/test_remote.py (4 tests). Models still cannot write EST or canonical data/; human merge approval unchanged.
- Verification: test_remote + test_contribute + test_static_site 30 passed; full suite 431 passed, 2 unrelated failures (test_atlas_gates: commit b2663cb0 lacks data in local history; test_taurus: shadow assertion). ruff clean on touched files; 15 pre-existing ruff errors elsewhere.
- Side effect to clean up: the full pytest run appended 14 test-generated lines to data/research/mirror_loop_checkpoints.jsonl (revert with git checkout -- that file; revert was blocked by the auto-mode classifier, left for the user). Temp helpers dist/_gen_llms.py, dist/_verify.ps1, dist/_verify2.ps1, dist/.pytest-tmp are uncommitted (dist/ not tracked).
- Scope separation: UPI repo is unrelated to dpstudio-se/upi-built-by-agi-teax-main (grok.me). Added identity notices to README.md/README.sv.md, new docs/SCOPE.md, AGENTS.md, .github/copilot-instructions.md, docs/UPI_AI_REMOTE.md, CLAUDE.md/GEMINI.md/.cursorrules (above the Continuity marker; may be overwritten), and src/upi/remote.py (guardrail + manifest "scope" + llms.txt regenerated). Removed the "RNA explorer" framing from README and ARCHITECTURE.md; docs/VSCODE_AGENT_PROMPT.md stripped of TanStack/grok.me material. Historical docs (CHANGELOG, RNA_UI_INBOX, ISSUE_AUDIT_2026_09_14, etc.) left as records. Targeted tests pass (30).
- Nothing committed or pushed (9747f71 still unpushed). UI-modes / in-browser LLM plan is on hold.

