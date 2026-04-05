# NITROTOOLS PUBG MOBILE 🎮⚡

[![Author](https://img.shields.io/badge/Author-NITRO-red)](https://github.com/Nitrodz00/NITRO-TOOLS)
[![GitHub Release Date](https://img.shields.io/github/release-date/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/Nitrodz00/NITRO-TOOLS/total?color=brightgreen)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub issues](https://img.shields.io/github/issues-raw/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/issues)

> **NITROTOOLS** — The ultimate PUBG Mobile performance optimization tool for **Gameloop 64-bit** emulator.  
> Designed to give you the **smoothest 120 FPS** gaming experience with zero input lag and zero stutter.

---

## ⚡ Features

### 🎨 Graphics Optimizer
- Unlock all graphics settings including **Super Smooth**, Smooth, Balanced, HD, HDR, Ultra HD
- Override Gameloop's locked presets directly via `Active.sav`
- Force maximum draw distance and anti-aliasing

### 🚀 Gameloop Engine Tweaks (64-bit)
- Targets `AndroidEmulatorEn.exe` directly (not AppMarket) for raw performance
- **VSync OFF** — eliminates frame drops and display lag
- **ScreenRawInput = 1** — perfect 1:1 mouse accuracy
- **EnableRootAuthority = 1** — full engine access

### 🌐 Network Optimization
- `TcpAckFrequency` tweaks for minimum ping
- `NetworkThrottlingIndex` registry fix for maximum bandwidth priority
- DNS Changer — Google, Cloudflare, Quad9, Cisco, Yandex

### 🧹 System Cleaner
- Wipes Gameloop ShaderCache, logs, and temp files before every game launch
- Cleans Windows `%temp%`, `C:\Windows\Temp`, and `Prefetch`

### ⚙️ Auto-Priority Enforcer
- Automatically forces `AndroidEmulatorEn.exe` to **High Priority** every 60 seconds in the background

### 🖥️ Other Tools
- iPad View (resolution changer)
- Desktop shortcut creator (all PUBG Mobile versions)
- PC Optimizer (registry tweaks for gaming)
- Force Close Gameloop

---

## 📥 Download

**Latest build (public, no login required):**  
[https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest](https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest)

- Open **Assets** on the latest release and download **`NITROTOOLS_PUBG_MOBILE_v*.exe`** (Windows 64-bit).
- Releases are produced automatically when a version tag is pushed (see below). Anyone can download the attached `.exe`.

> ⚠️ Run as **Administrator** for full functionality.

### Publish a new downloadable release (maintainers)

1. Bump `APP_VERSION` in `main.py` (e.g. `v2.2.0`) and commit.
2. Create and push a matching Git tag:
   ```bash
   git tag v2.2.0
   git push origin v2.2.0
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
