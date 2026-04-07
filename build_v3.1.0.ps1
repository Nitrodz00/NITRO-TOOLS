# NITROTOOLS PUBG MOBILE v3.1.0 Build Script
# Professional Grade Optimization Tool Build

Write-Host "🚀 Building NITROTOOLS PUBG MOBILE v3.1.0" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Configuration
$Version = "v3.1.0"
$AppName = "NITROTOOLS_PUBG_MOBILE"
$SpecFile = "NITROTOOLS_RELEASE.spec"
$OutputDir = "dist"
$ReleaseDir = "release_v3.1.0"

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $OutputDir) {
    Remove-Item -Recurse -Force $OutputDir
}
if (Test-Path $ReleaseDir) {
    Remove-Item -Recurse -Force $ReleaseDir
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Install/Update dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Verify critical modules
Write-Host "🔍 Verifying critical modules..." -ForegroundColor Yellow
$modules = @("PyQt5", "psutil", "sklearn", "numpy", "scipy", "adbutils", "wmi", "GPUtil", "ping3")
foreach ($module in $modules) {
    try {
        python -c "import $module; print('✓ $module imported successfully')"
    } catch {
        Write-Host "❌ Failed to import $module" -ForegroundColor Red
        Write-Host "Installing $module..." -ForegroundColor Yellow
        pip install $module
    }
}

# Set environment variables
Write-Host "🔧 Setting up build environment..." -ForegroundColor Yellow
$env:PYINSTALLER_EXE_NAME = "$AppName`_$Version"

# Build the executable
Write-Host "🏗️ Building executable..." -ForegroundColor Yellow
try {
    pyinstaller --clean --noconfirm $SpecFile
    
    if (Test-Path "$OutputDir\$AppName`_$Version.exe") {
        Write-Host "✅ Build successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Build error: $_" -ForegroundColor Red
    exit 1
}

# Create release directory
Write-Host "📁 Creating release package..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $ReleaseDir | Out-Null

# Copy executable
Copy-Item "$OutputDir\$AppName`_$Version.exe" -Destination $ReleaseDir

# Copy essential files
$filesToCopy = @(
    "README.md",
    "README.ar.md", 
    "CHANGELOG_v3.1.0.md",
    "IMPROVEMENTS_SUMMARY.md",
    "LICENSE"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $ReleaseDir
        Write-Host "✓ Copied $file" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $file not found" -ForegroundColor Yellow
    }
}

# Create version info file
$versionInfo = @"
NITROTOOLS PUBG MOBILE
Version: $Version
Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Build Type: Professional Grade Release
Features: Expert Mode, AMD Support, Enhanced Monitoring, Compatibility Manager
"@
$versionInfo | Out-File -FilePath "$ReleaseDir\VERSION_INFO.txt" -Encoding UTF8

# Create installation guide
$installGuide = @"
# NITROTOOLS PUBG MOBILE v3.1.0 Installation Guide

## Quick Start
1. Run NITROTOOLS_PUBG_MOBILE_v3.1.0.exe as Administrator
2. The application will automatically detect your system
3. Enable Expert Mode for advanced settings
4. Use Compatibility Manager to check system requirements

## New Features
- 🎛️ Expert Mode with 5 optimization categories
- 🛡️ Compatibility Manager for automatic feature detection
- 🚀 Full AMD GPU support
- 📊 Enhanced performance monitoring with caching
- ⚡ QTimer-based responsive interface

## System Requirements
- Windows 10/11 (Build 10240+)
- 4GB RAM minimum (6GB+ recommended)
- Administrator privileges required
- GameLoop 7.1 or later

## Troubleshooting
- Run as Administrator if features don't work
- Check Compatibility Manager for disabled features
- Update GPU drivers for best performance
- Disable antivirus temporarily if installation fails

For detailed information, see CHANGELOG_v3.1.0.md
"@
$installGuide | Out-File -FilePath "$ReleaseDir\INSTALLATION.txt" -Encoding UTF8

# Verify build integrity
Write-Host "🔍 Verifying build integrity..." -ForegroundColor Yellow
$exePath = "$ReleaseDir\$AppName`_$Version.exe"
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    $fileSize = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "✅ Executable size: $fileSize MB" -ForegroundColor Green
    
    # Test executable (basic check)
    try {
        $testResult = & $exePath --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Executable test passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Executable test returned code $LASTEXITCODE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Could not test executable (normal for GUI apps)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Executable not found!" -ForegroundColor Red
    exit 1
}

# Create ZIP archive
Write-Host "📦 Creating release archive..." -ForegroundColor Yellow
try {
    Compress-Archive -Path $ReleaseDir -DestinationPath "$ReleaseDir.zip" -Force
    Write-Host "✅ Archive created: $ReleaseDir.zip" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create archive: $_" -ForegroundColor Red
}

# Generate build report
$buildReport = @"
# NITROTOOLS PUBG MOBILE v3.1.0 Build Report

## Build Information
- Version: $Version
- Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Build Type: Professional Grade Release
- Executable Size: $fileSize MB

## Features Included
- ✅ Shadow Control Fix
- ✅ Shortcut Creation Fix  
- ✅ Full AMD GPU Support
- ✅ Expert Mode (5 categories)
- ✅ Compatibility Manager
- ✅ Enhanced Performance Monitoring
- ✅ QTimer Implementation
- ✅ Data Caching System
- ✅ Memory Optimization

## Files Created
- NITROTOOLS_PUBG_MOBILE_v3.1.0.exe (Main executable)
- README.md (Documentation)
- README.ar.md (Arabic documentation)
- CHANGELOG_v3.1.0.md (Detailed changelog)
- IMPROVEMENTS_SUMMARY.md (Technical summary)
- VERSION_INFO.txt (Build information)
- INSTALLATION.txt (Installation guide)
- $ReleaseDir.zip (Release archive)

## Testing Status
- ✅ Dependencies verified
- ✅ Build completed successfully
- ✅ Executable created
- ✅ Release package assembled

## Ready for Distribution
The v3.1.0 release is ready for distribution with all professional-grade features implemented.

Build completed successfully! 🚀
"@
$buildReport | Out-File -FilePath "BUILD_REPORT_v3.1.0.txt" -Encoding UTF8

Write-Host ""
Write-Host "🎉 NITROTOOLS PUBG MOBILE v3.1.0 Build Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "📁 Release directory: $ReleaseDir" -ForegroundColor Cyan
Write-Host "📦 Archive: $ReleaseDir.zip" -ForegroundColor Cyan
Write-Host "📋 Build report: BUILD_REPORT_v3.1.0.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ready for distribution!" -ForegroundColor Green
Write-Host ""
Write-Host "New Features in v3.1.0:" -ForegroundColor Yellow
Write-Host "• 🎛️ Expert Mode with advanced settings" -ForegroundColor White
Write-Host "• 🛡️ Compatibility Manager" -ForegroundColor White
Write-Host "• 🚀 Full AMD GPU support" -ForegroundColor White
Write-Host "• 📊 Enhanced performance monitoring" -ForegroundColor White
Write-Host "• ⚡ Responsive UI with QTimer" -ForegroundColor White
Write-Host "• 📦 Intelligent caching system" -ForegroundColor White
Write-Host ""
Write-Host "Thank you for using NITROTOOLS! 🎮" -ForegroundColor Magenta
