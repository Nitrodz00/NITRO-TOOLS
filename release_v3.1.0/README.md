# NITROTOOLS PUBG MOBILE 🎮⚡

[![Author](https://img.shields.io/badge/Author-NITRO-red)](https://github.com/Nitrodz00/NITRO-TOOLS)
[![GitHub Release Date](https://img.shields.io/github/release-date/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/Nitrodz00/NITRO-TOOLS/total?color=brightgreen)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub issues](https://img.shields.io/github/issues-raw/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/issues)

> **NITROTOOLS** — The ultimate AI-Powered performance optimization tool for **Gameloop 64-bit** emulator.  
> Experience **Ultra-Smooth 120 FPS** with zero input lag, professional aesthetics, and real-time system monitoring.

---

## 🚀 Latest Features (v3.1.0) - Professional Grade Release

### 🎛️ **NEW: Expert Mode**
- **Advanced Settings Panel:** 5 categories of fine-tuned controls
  - **CPU Optimization:** Affinity control, priority boosting, hyperthreading management
  - **GPU Optimization:** Shader cache control, texture quality, VSync modes  
  - **Memory Optimization:** RAM cleanup intervals, pagefile optimization, memory compression
  - **Network Optimization:** TCP tweaks, DNS caching, QoS priority
  - **Advanced Tweaks:** Registry optimizations, service management, kernel-level tweaks
- **Profile Management:** Save and load custom optimization profiles
- **Import/Export Settings:** Share configurations between devices
- **Real-time Application:** Apply changes instantly without restart

### 🛡️ **NEW: Compatibility Manager**
- **Automatic System Analysis:** Comprehensive hardware and software detection
- **Feature Compatibility Matrix:** Intelligent detection of incompatible features
- **Automatic Feature Disabling:** Prevents crashes on unsupported systems
- **Manual Override Options:** Power users can enable/disable features manually
- **Detailed System Reports:** Export comprehensive compatibility information

### � **Enhanced Performance Monitoring**
- **GPU Memory Tracking:** Real-time VRAM usage and percentage
- **Network Latency Monitoring:** Ping tracking with alerts
- **Disk Usage Monitoring:** Storage space tracking
- **Performance History:** 100-entry buffer with trend analysis
- **Intelligent Alerts:** Temperature, memory, and performance warnings
- **Performance Snapshots:** Caching system for historical analysis

### 🛠️ **Critical Fixes**
- **Shadow Control Fix:** Shadow enable/disable now works properly in-game
- **Shortcut Creation Fix:** Fixed "Failed to start emulator" error
- **QTimer Implementation:** Replaced all sleep() calls for responsive UI
- **Memory Optimization:** ~40% reduction in memory usage

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

**Latest Release: v3.0.2** - Major binary shadow fix, robust GameLoop shortcut creation, and improved automation for all emulator versions.

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
