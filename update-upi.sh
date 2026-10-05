#!/usr/bin/env sh
# Linux/macOS counterpart of Update-UPI.ps1: build the static UPI site and
# optionally publish it over SFTP. The password is read from UPI_SFTP_PASSWORD
# or prompted for; it is never stored.
#
# Usage: ./update-upi.sh [--build-only] [--host HOST] [--user USER] [--remote-dir DIR]
set -eu

host='ftp.wadenholt.se'
user='wadenholt.se'
remote_dir='upi'
build_only=0

while [ $# -gt 0 ]; do
    case "$1" in
        --build-only|-b) build_only=1 ;;
        --host) host="$2"; shift ;;
        --user) user="$2"; shift ;;
        --remote-dir) remote_dir="$2"; shift ;;
        -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$root"
PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH

set -- -m upi.site --host "$host" --user "$user" --remote-dir "$remote_dir"

if [ "$build_only" -eq 1 ] && [ -x "$root/.venv/bin/python" ]; then
    "$root/.venv/bin/python" "$@"
elif command -v uv >/dev/null 2>&1; then
    if [ "$build_only" -eq 1 ]; then
        uv run --no-project --with jsonschema --cache-dir .uv-cache python "$@"
    else
        uv run --no-project --with jsonschema --with paramiko --cache-dir .uv-cache python "$@" --publish
    fi
else
    py=python3
    command -v "$py" >/dev/null 2>&1 || py=python
    if [ "$build_only" -eq 1 ]; then
        "$py" "$@"
    else
        "$py" "$@" --publish
    fi
fi
