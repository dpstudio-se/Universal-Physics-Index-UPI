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

