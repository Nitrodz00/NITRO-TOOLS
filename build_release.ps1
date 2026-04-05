# Build one-file Windows executable (PyInstaller).
# Keep in sync: main.py APP_VERSION, NITROTOOLS_RELEASE.spec default name, and $ReleaseVersion below.
# Run:  powershell -ExecutionPolicy Bypass -File .\build_release.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$ReleaseVersion = "2.1.5"
$ExeName = "NITROTOOLS_PUBG_MOBILE_v$ReleaseVersion.exe"

Write-Host "Installing build deps (PyInstaller)..." -ForegroundColor Cyan
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
python -m pip install -q -r requirements-build.txt

Write-Host "Building NITROTOOLS_RELEASE.spec (clean)..." -ForegroundColor Cyan
$env:PYINSTALLER_EXE_NAME = "NITROTOOLS_PUBG_MOBILE_v$ReleaseVersion"
python -m PyInstaller --noconfirm --clean NITROTOOLS_RELEASE.spec

$exe = Join-Path $PSScriptRoot "dist\$ExeName"
if (Test-Path $exe) {
    Write-Host "OK: $exe" -ForegroundColor Green
} else {
    Write-Host "Build finished but EXE not found at expected path." -ForegroundColor Red
    exit 1
}
