# Publish the UPI laboratory on One.com

The static laboratory runs without Python on the web host. Settings are stored
in the visitor's browser using the Save button; JSON import/export transfers
parameters between devices. There is no website login or shared settings database.
SFTP authentication remains on the operator's computer, outside the website.

## Build and preview

From this checkout (Python 3.10+):

```powershell
.venv/Scripts/python.exe -m upi.site
.venv/Scripts/python.exe -m http.server 8090 --directory dist
```

Open `http://127.0.0.1:8090/upi/`. `dist/upi/` contains only the static UI,
content-addressed assets and a manifest. Relative links work under `/upi/`.
The build does not include `.env`, source data, passwords or the Python server.
Every build also refreshes `dist/upi-webbhotell-v1.zip` from exactly these five
files and verifies the archive before replacing the previous package. Upload and
extract the ZIP in your domain's document root using One.com's File Manager;
the archive contains the `upi/` directory. Keep the existing site's root index.

## Update in one command

With `uv` installed, run from PowerShell:

```powershell
./Update-UPI.ps1
```

If Windows blocks unsigned local scripts, the following applies the exception
only to this invocation; it does not change the machine's execution policy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./Update-UPI.ps1
```

The script builds the current local source and publishes it over SFTP to `upi`
under the authenticated account's home directory. It prompts for the password
without echoing it; automation may provide `UPI_SFTP_PASSWORD` in the process
environment. Never put credentials in `dist/upi` or client-side JavaScript.

Use the actual SFTP host/user and web root shown by One.com:

```powershell
./Update-UPI.ps1 -SftpHost ftp.wadenholt.se -SftpUser wadenholt.se -RemoteDirectory public_html/upi
./Update-UPI.ps1 -BuildOnly
```

BuildOnly uses the existing Windows virtual environment without installing SFTP
dependencies. Publishing uses an isolated Paramiko environment through `uv`.

`public_html/upi` above is an example, not a verified directory for this account.
The site's intended public URL is `https://wadenholt.se/upi/`; confirm the hosting
document root before uploading. The script does not pull or merge Git changes:
review/update your local checkout first, then run the script again.

For other shells use `python -m upi.site --publish` with Paramiko installed in
the execution environment. Optional arguments include `--host`, `--user`,
`--remote-dir`, `--port`, and `--host-key-sha256`.

## Publication and recovery

Assets use content hashes so old and new pages can coexist. Each upload is read
back and compared byte-for-byte before publication. Existing assets are reused
only if their bytes agree. The entry point is replaced last using the SFTP atomic
rename extension. Unsupported atomic rename leaves the previous entry point live.
Unrelated existing index files and symlink destinations are rejected.

The script prints a release directory containing `manifest.json` and, on updates,
`previous-index.html`. To roll back, download that previous file and upload it as
`index.html` in the same UPI folder using SFTP/File Manager. Old hashed assets are
retained; the script never recursively deletes remote files. Storage may grow
with releases. Do not remove assets still referenced by a rollback version.

The default SSH fingerprint is the key first observed in this session on
`ftp.wadenholt.se:22`:
`SHA256:iDgAh/1dj9HyXk3nOztS6nK7jJI1IyR2uUrxDCF9kI8`.
It is pinned against subsequent changes, not independently certified by One.com.
Verify a changed key with the host before overriding it. Known-host mismatches
are never ignored.

## Evidence and remaining boundary

`verification_type: software_test`. Unit tests exercise deterministic builds,
path restrictions, rollback preservation, corrupted uploads and failed atomic
replacement using an in-memory SFTP double. They do not establish hosting access.

EST: The earlier real SSH connection reached One.com's proxy but authentication
was rejected. STOP / stop_reason: valid SFTP credentials and the account's web
document root are not yet confirmed. Smallest next observation: successful SFTP
login and read-only directory inspection using the control-panel details.

After publication, fetch the public HTML and its assets over HTTPS and compare
their hashes to the local manifest. Open `/upi/` at desktop and mobile sizes,
save a frequency, reload, import JSON and export the resulting calculation.
Any missing asset, hash mismatch, stale index or failed control falsifies the
corresponding deployment claim.

Local verification on 2026-09-08 (Python 3.14.7, Node 26.7.0): 13 publisher/build
tests and the HTTP delivery test passed. Edge loaded the static `/upi/` version,
preserved saved values after reload, accepted valid JSON, rejected invalid JSON
without changing values, cleared saved settings, and rendered at 390px without
horizontal overflow or JavaScript exceptions. The PowerShell BuildOnly command
also passed. These are local software results, not evidence of remote deployment.
