# NITROTOOLS PUBG MOBILE 🎮⚡

[![Author](https://img.shields.io/badge/Author-NITRO-red)](https://github.com/Nitrodz00/NITRO-TOOLS)
[![GitHub Release Date](https://img.shields.io/github/release-date/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/Nitrodz00/NITRO-TOOLS/total?color=brightgreen)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub issues](https://img.shields.io/github/issues-raw/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/issues)

> **NITROTOOLS** — The ultimate AI-Powered performance optimization tool for **Gameloop 64-bit** emulator.  
> Experience **Ultra-Smooth 120 FPS** with zero input lag, professional aesthetics, and real-time system monitoring.

---

## 🚀 Latest Features (v2.5.0)

### 🔒 Enhanced Security & Stability
- **File Integrity Checks:** Automatic verification of update downloads
- **Improved Admin Handling:** Better error management for permission issues

### 🧠 Advanced AI & ML
- **Machine Learning FPS Prediction:** AI optimizer now uses ML models for smarter performance tuning
- **Adaptive Learning:** System learns from your hardware patterns for optimal settings

### 🎨 Multiple Theme Variants
- **Cosmic Theme:** Original deep purple gradients
- **Neon Green:** Cyberpunk green accents
- **Red Alert:** High-contrast red theme

### 🌡️ Thermal Management
- **Real-time Temperature Monitoring:** CPU and GPU temps displayed in header
- **Thermal Alerts:** Notifications for overheating conditions

### 🖥️ Expanded Hardware Support
- **AMD GPU Detection:** Full support for Radeon graphics cards
- **Universal Compatibility:** Better detection across different hardware configs

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

**Latest Release: v2.5.0** - Major enhancements including ML-powered AI, thermal management, multiple themes, and improved security.

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
