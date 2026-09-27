param(
    [switch]$BuildOnly,
    [string]$SftpHost = 'ftp.wadenholt.se',
    [string]$SftpUser = 'wadenholt.se',
    [string]$RemoteDirectory = 'upi'
)
$ErrorActionPreference = 'Stop'
$upiPreviousPythonPath = $env:PYTHONPATH
Push-Location $PSScriptRoot
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
    $upiArgs = @('-m', 'upi.site', '--host', $SftpHost, '--user', $SftpUser,
        '--remote-dir', $RemoteDirectory)
    $upiPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
    if ($BuildOnly -and (Test-Path -LiteralPath $upiPython)) {
        & $upiPython @upiArgs
    } elseif ($BuildOnly) {
        & uv run --no-project --cache-dir .uv-cache python @upiArgs
    } else {
        & uv run --no-project --with paramiko --cache-dir .uv-cache python @upiArgs --publish
    }
    if ($LASTEXITCODE -ne 0) { throw 'UPI update failed. See the error above.' }
} finally {
    $env:PYTHONPATH = $upiPreviousPythonPath
    Pop-Location
}
