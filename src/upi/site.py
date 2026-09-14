"""Build and publish the static laboratory. No credentials enter the site bundle."""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

STATIC = Path(__file__).parent / "contribute" / "static"
ASSETS = ("lab.css", "lab-math.js", "lab.js")
MARKER = "<!-- upi-static-laboratory -->"
ONE_HOST_KEY = "SHA256:iDgAh/1dj9HyXk3nOztS6nK7jJI1IyR2uUrxDCF9kI8"


def build_site(destination: Path) -> dict[str, bytes]:
    """Create a self-contained bundle; content-address assets for cache safety."""
    files = {}
    html = (STATIC / "lab.html").read_text(encoding="utf-8")
    for name in ASSETS:
        raw = (STATIC / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()[:16]
        asset = f"assets/{digest}-{name}"
        files[asset] = raw
        html = html.replace(f"/static/{name}", asset)
    html = html.replace('href="/lab"', 'href="./"')
    html = html.replace('href="/">Index →</a>', 'href="#settings">Inställningar</a>')
    files["index.html"] = (MARKER + "\n" + html).encode("utf-8")
    files["manifest.json"] = (json.dumps({
        "application": "upi-static-laboratory", "version": "1.0.0",
        "files": {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()},
        "verification_type": "software_test",
    }, indent=2) + "\n").encode()
    for name, raw in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return files


def remote_parts(path: str) -> list[str]:
    """Only relative directories below the authenticated account's home."""
    parts = path.split("/")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", part) for part in parts):
        raise ValueError("Remote directory must be relative, e.g. upi or public_html/upi.")
    return parts


def build_archive(files: dict[str, bytes], destination: Path) -> None:
    """Archive only this build's allowlisted files, never stale output or secrets."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".zip.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for name, raw in files.items():
                archive.writestr("upi/" + name, raw)
        with ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise OSError("Archive integrity verification failed")
            for name, raw in files.items():
                if archive.read("upi/" + name) != raw:
                    raise OSError(f"Archive content mismatch: {name}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def read_remote(sftp: Any, name: str) -> bytes | None:
    try:
        with sftp.open(name, "rb") as handle:
            return bytes(handle.read())
    except FileNotFoundError:
        return None


def ensure_directory(sftp: Any, name: str) -> None:
    try:
        info = sftp.lstat(name)
    except FileNotFoundError:
        sftp.mkdir(name)
        info = sftp.lstat(name)
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"Refusing non-directory or symlink: {name}")


def upload_checked(sftp: Any, name: str, raw: bytes) -> None:
    with sftp.open(name, "wb") as handle:
        handle.write(raw)
    if read_remote(sftp, name) != raw:
        raise OSError(f"Uploaded bytes differ: {name}; live index was not switched.")


def publish(sftp: Any, files: dict[str, bytes], remote: str) -> str:
    """Upload assets first, preserve old HTML, then atomically replace entry point."""
    parts = remote_parts(remote)
    for i in range(len(parts)):
        ensure_directory(sftp, "/".join(parts[:i + 1]))
    for name in ("index.html", "manifest.json"):
        try:
            mode = sftp.lstat(f"{remote}/{name}").st_mode
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"Refusing non-regular file or symlink: {name}")
    previous = read_remote(sftp, f"{remote}/index.html")
    if previous is not None and MARKER.encode() not in previous:
        raise ValueError("Existing index is not owned by UPI; choose an empty directory.")
    release = hashlib.sha256(files["index.html"]).hexdigest()[:16]
    ensure_directory(sftp, f"{remote}/assets")
    ensure_directory(sftp, f"{remote}/upi-releases")
    release_dir = f"{remote}/upi-releases/{release}"
    ensure_directory(sftp, release_dir)
    # Stage in a new directory to avoid following pre-existing links.
    import uuid

    staging = f"{release_dir}/{uuid.uuid4().hex}"
    sftp.mkdir(staging)
    if previous is not None:
        upload_checked(sftp, f"{staging}/previous-index.html", previous)
    for name, raw in files.items():
        if not name.startswith("assets/"):
            continue
        target = f"{remote}/{name}"
        try:
            mode = sftp.lstat(target).st_mode
        except FileNotFoundError:
            mode = None
        if mode is not None:
            if not stat.S_ISREG(mode) or read_remote(sftp, target) != raw:
                raise ValueError(f"Conflicting asset: {name}")
        else:
            temp = f"{staging}/{Path(name).name}"
            upload_checked(sftp, temp, raw)
            sftp.rename(temp, target)
    upload_checked(sftp, f"{staging}/manifest.json", files["manifest.json"])
    upload_checked(sftp, f"{staging}/index.html", files["index.html"])
    # No remove-then-rename fallback: unsupported atomic replacement must fail closed.
    sftp.posix_rename(f"{staging}/index.html", f"{remote}/index.html")
    return staging


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/upi"))
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--host", default="ftp.wadenholt.se")
    parser.add_argument("--user", default="wadenholt.se")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--remote-dir", default="upi")
    parser.add_argument("--host-key-sha256", default=ONE_HOST_KEY)
    args = parser.parse_args()
    try:
        remote_parts(args.remote_dir)
        files = build_site(args.output)
        print(f"Built {len(files)} files in {args.output}")
        archive = args.output.parent / "upi-webbhotell-v1.zip"
        build_archive(files, archive)
        print(f"Verified archive: {archive}")
        if not args.publish:
            return 0
        import paramiko

        class PinnedKey(paramiko.MissingHostKeyPolicy):
            def missing_host_key(self, client: Any, hostname: str, key: Any) -> None:
                observed = "SHA256:" + base64.b64encode(
                    hashlib.sha256(key.asbytes()).digest()
                ).decode().rstrip("=")
                if observed != args.host_key_sha256:
                    raise paramiko.SSHException(f"Host key mismatch: {observed}")
                client.get_host_keys().add(hostname, key.get_name(), key)

        password = os.environ.get("UPI_SFTP_PASSWORD") or getpass.getpass("SFTP password: ")
        with paramiko.SSHClient() as client:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(PinnedKey())
            client.connect(args.host, port=args.port, username=args.user, password=password,
                           look_for_keys=False, allow_agent=False, timeout=20,
                           auth_timeout=20, banner_timeout=20)
            with client.open_sftp() as sftp:
                location = publish(sftp, files, args.remote_dir)
                print(f"Published {args.remote_dir}/index.html; backup/manifest: {location}")
        return 0
    except Exception as error:
        print(f"STOP: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
