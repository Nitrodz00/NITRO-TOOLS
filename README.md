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

Download the latest `NitroTools.exe` from the [Releases page](https://github.com/Nitrodz00/NITRO-TOOLS/releases).

> ⚠️ Run as **Administrator** for full functionality.

---

## 🛠️ Build from Source

```bash
pip install -r requirements.txt
python main.py
```

To build EXE:
```bash
pyinstaller --noconfirm --clean --onefile --windowed --add-data "assets;assets" --hidden-import pkg_resources --hidden-import setuptools --collect-all adbutils --icon "assets/icons/logo.ico" "main.py" --name "NitroTools"
```

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
