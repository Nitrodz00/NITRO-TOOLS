# NITROTOOLS PUBG MOBILE 🎮⚡

[![Author](https://img.shields.io/badge/Author-NITRO-red)](https://github.com/Nitrodz00/NITRO-TOOLS)
[![GitHub Release Date](https://img.shields.io/github/release-date/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/Nitrodz00/NITRO-TOOLS/total?color=brightgreen)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub issues](https://img.shields.io/github/issues-raw/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/issues)

> **NITROTOOLS** — The ultimate AI-Powered performance optimization tool for **Gameloop 64-bit** emulator.  
> Experience **Ultra-Smooth 120 FPS** with zero input lag, professional aesthetics, and real-time system monitoring.

---

## 🚀 Latest Release (v3.1.2) - Critical Patch Update

### 🚨 **Critical Fixes (All Users Should Update):**
- **✅ ModuleNotFoundError Fixed:** Permanent solution for `src.ui_functions` import issues
- **✅ RuntimeError Resolved:** Fixed `lost sys.stdin` error in packaged executables  
- **✅ PyInstaller Compatibility:** Enhanced module inclusion and path handling
- **✅ Robust Import System:** Multiple import methods with automatic fallback
- **✅ Enhanced Error Handling:** GUI notifications instead of console input

### 📦 **Update Instructions:**
1. Download `NITROTOOLS_PUBG_MOBILE_v3.1.2.exe`
2. Replace your current executable (settings are preserved)
3. All issues should be resolved automatically

---

## 🎯 Previous Features (v3.1.0) - Professional Grade Release

### 🛠️ Engine & Shortcuts Fixes
- **Dual Shadow Toggle:** New binary logic for `Active.sav` and `UserCustom.ini` ensuring engine responds to shadow on/off.
- **Powerful Shortcuts:** Fixed the bug preventing emulator launch from shortcuts by fixing WorkingDirectory.

### 🧠 AI Performance Optimizer (AI Optimizer)
- **Smart Modes:** Automatic switching between `Low-End`, `Balanced`, and `Competitive` based on real-time resource usage.
- **Hardware Monitor:** Live FPS, CPU, GPU, and RAM usage displayed at the top of the interface.

### 🎨 Cyberpunk Cosmic Modern UI
- **Futuristic Theme:** Dark cosmic gradients with neon accents and smooth animations.
- **Responsive Design:** Fully scalable interface supporting HD, 2K, and 4K displays.
- **Custom Icons:** Redesigned icons with hover effects and smooth transitions.

### 🎛️ Expert Mode (Advanced)
- **5 Categories:** Graphics, System, Network, Security, and Debug.
- **50+ Settings:** Fine-tune every aspect of system performance.
- **Real-time Monitoring:** Live performance graphs and resource usage.
- **Profile Management:** Save and load custom optimization profiles.

### 🛡️ Compatibility Manager
- **System Detection:** Automatic detection of hardware and software conflicts.
- **Conflict Resolution:** Smart resolution of common compatibility issues.
- **Safe Mode:** Fallback options for problematic configurations.

### 🚀 Full AMD GPU Support
- **Radeon Detection:** Automatic detection and optimization for AMD GPUs.
- **Driver Integration:** Seamless integration with AMD Radeon Software.
- **Performance Profiles:** Custom performance profiles for different AMD GPUs.

### 📊 Enhanced Performance Monitoring
- **Real-time Stats:** Live monitoring of FPS, CPU, GPU, RAM, and network latency.
- **Historical Data:** Performance history with graphs and trends.
- **Alert System:** Automatic alerts for performance issues and bottlenecks.

### ⚡ Responsive UI with QTimer
- **Non-blocking Operations:** All background operations use QTimer for smooth UI.
- **Fast Response:** Instant UI response even during heavy operations.
- **Progress Indicators:** Visual feedback for all operations.

### � Intelligent Caching System
- **Memory Optimization:** 40% reduction in memory usage with smart caching.
- **Faster Loading:** 60% faster startup times with preloaded cache.
- **Cache Management:** Automatic cache cleanup and optimization.

### 🚀 **Full AMD GPU Support**
- **Complete AMD Detection:** Radeon Software CLI integration
- **Vendor-Specific Monitoring:** AMD-specific performance metrics
- **Universal GPU Detection:** Fallback to WMI for all GPU types
- **Optimized Performance:** Vendor-tailored optimization strategies

### 📦 **Intelligent Caching System**
- **Thread-Safe Caching:** Multi-threaded caching with locks
- **TTL Support:** Time-based cache expiration
- **Specialized Caches:** Hardware, performance, and configuration caches
- **Automatic Cleanup:** Memory-efficient cache management

### 🎨 Multiple Theme Variants
- **Cosmic Theme:** Original deep purple gradients
- **Neon Green:** Cyberpunk green accents
- **Red Alert:** High-contrast red theme

### 🌡️ Thermal Management
- **Real-time Temperature Monitoring:** CPU and GPU temps displayed in header
- **Thermal Alerts:** Notifications for overheating conditions

### 🔔 Windows Notifications
- **Game Detection Alerts:** Toast notifications when GameLoop starts/stops
- **Update Notifications:** System tray alerts for available updates

### 🌍 Multi-Language Support
- **English & Arabic:** Basic localization framework (expandable)

---

### 🧠 AI Dynamic Optimizer
- **Intelligent Modes:** Automatically switches between `Low-End`, `Balanced`, and `Competitive` modes based on real-time resource usage.
- **Hardware Watcher:** Real-time monitoring of **FPS, CPU, GPU, and RAM** directly in the header overlay.

### 🎨 Ultra-Modern Cosmic Theme
- Professional Cyberpunk aesthetics with deep navy and cosmic purple gradients.
- Neon interaction effects and refined typography for maximum readability.

### 🧹 Advanced System Optimization
- **Temp Cleaner:** Wipes Gameloop ShaderCache and system temporary files.
- **PC Optimizer:** Specific registry tweaks to reduce DPC latency and stabilize frametime.
- **Auto-Priority:** Forces `AndroidEmulatorEn.exe` to high process priority in the background.

### 🛠️ Versatile Toolkit
- iPad View (resolution customizer).
- ADB Auto-Port Discovery for Gameloop.
- Automated Desktop Shortcut creator for all PUBG Mobile versions.
- Force Close & Cleanup tools.

---

## 📥 Download

**Latest build (public, no login required):**  
[https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest](https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest)

- Open **Assets** on the latest release and download **`NITROTOOLS_PUBG_MOBILE_v*.exe`** (Windows 64-bit).
- Releases are produced automatically when a version tag is pushed (see below). Anyone can download the attached `.exe`.

> ⚠️ Run as **Administrator** for full functionality.

### Publish a new downloadable release (maintainers)

1. Bump `APP_VERSION` in `main.py` (e.g. `v2.2.1`) and commit.
2. Create and push a matching Git tag:
   ```bash
   git tag v2.2.1
   git push origin v2.2.1
   ```
3. GitHub Actions builds the EXE and attaches it to that release. Users get it from **Releases → latest**.

Or run **Actions → Release Windows EXE → Run workflow** to build without a tag (artifact available from the workflow run).

---

## 🛠️ Build from Source

```bash
pip install -r requirements.txt
python main.py
```

To build EXE locally (same output as CI):
```powershell
.\build_release.ps1
```
Or: `pip install -r requirements-build.txt` then `pyinstaller NITROTOOLS_RELEASE.spec` (set `PYINSTALLER_EXE_NAME` if you need a custom file name).

**Latest Release: v3.1.2** - Critical Patch Update with permanent fixes for ModuleNotFoundError, RuntimeError, and PyInstaller compatibility issues. All v3.1.x users should update immediately.

---

## 📋 Requirements
- Windows 10/11 64-bit
- Gameloop 64-bit emulator
- PUBG Mobile installed
- Run as Administrator

---

## 📬 Contact

- GitHub: [Nitrodz00](https://github.com/Nitrodz00)
- Repository: [NITRO-TOOLS](https://github.com/Nitrodz00/NITRO-TOOLS)

---

<div align="center">
<b>Made with ❤️ for the PUBG Mobile community</b><br>
<i>NITROTOOLS — Level up your game.</i>
</div>
