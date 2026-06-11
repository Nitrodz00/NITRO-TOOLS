# NITROTOOLS PUBG MOBILE 🎮⚡

[![Author](https://img.shields.io/badge/Author-NITRO-red)](https://github.com/Nitrodz00/NITRO-TOOLS)
[![GitHub Release Date](https://img.shields.io/github/release-date/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/Nitrodz00/NITRO-TOOLS/total?color=brightgreen)](https://github.com/Nitrodz00/NITRO-TOOLS/releases)
[![GitHub issues](https://img.shields.io/github/issues-raw/Nitrodz00/NITRO-TOOLS)](https://github.com/Nitrodz00/NITRO-TOOLS/issues)

> **NITROTOOLS** — The ultimate AI-Powered performance optimization tool for **Gameloop 64-bit** emulator.  
> Experience **Ultra-Smooth 120 FPS** with zero input lag, professional aesthetics, and real-time system monitoring.

---

## 🚀 Latest Release: v3.1.9

### 🔧 What's Fixed
- **Shortcut name** — Desktop shortcut is now "PUBG Mobile Global" (no NITRO suffix)
- **Shortcut launch** — GameLoop starts minimized, no AppMarket popup
- **PUBG Global icon** — New updated icon for desktop shortcut
- **Shadow lock** — `chattr +i` immutable lock + `Scalability.ini` to prevent game from overwriting shadow settings
- **Style button** — Cyan border highlight on selected style (Classic, Colorful, Realistic, Soft, Movie)
- **GFX modes** — Style applies to Battle, Lobby, Training & Art modes
- **Real FPS** — Header shows real FPS via ADB when connected (`~` = estimated)
- **FPS color** — Magenta for medium FPS, cyan for high, red for low
- **AI Optimizer** — Pauses during GFX apply to avoid conflicts

### ✨ New Features (Latest Patches)
- **iPad Resolution** — 5 presets including new **1720×1440** and **1280×960**
- **Apply To Mode** — Choose: `Screen + Game` / `Game Only` / `Screen Only`
- **Screen Resolution Change** — Instantly changes Windows display resolution via win32api
- **Toolkit tab** — Renamed from "Other" for clarity

### ⚡ Partial Update System
From v3.1.9 onwards, fixes are delivered as **patch ZIPs (~160KB)** — no full installer needed.  
Just press **CHECK FOR UPDATES** and patches apply automatically in seconds.  
**Any new file or module** added in a patch is auto-loaded — zero maintenance required.

---

## 📥 Download & Install (New Users)

### Step 1 — Download
**[⬇️ Download NITROTOOLS_Setup_v3.1.9.exe](https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest)**

### Step 2 — Install
1. Right-click the installer → **Run as Administrator**
2. Follow the setup wizard (~30 seconds)
3. Launch **NITROTOOLS PUBG MOBILE** from the desktop shortcut

### Step 3 — Done ✅
Future updates apply automatically — press **CHECK FOR UPDATES** anytime.

---

## ⚡ Quick Start

1. **TOOLKIT** → `COMPETITIVE MODE (MAX)`
2. **SYSTEM** → `ONE-CLICK AI OPTIMIZER`
3. Enable `AUTO-BOOST` — keep running in background

🎮 **Done! Enjoy smooth lag-free gaming.**

---

## 🔄 Updating from Any Version
1. Open the tool → click **CHECK FOR UPDATES NOW**
2. - **Patch update** (same version) → downloads ~20KB ZIP, applies instantly, restarts
   - **Full upgrade** (new version) → downloads installer, runs automatically
3. Settings are always preserved

---

## 🎯 Features

### 🧠 AI Dynamic Optimizer
- **Smart Modes** — Auto-switches between `Low-End`, `Balanced`, and `Competitive` based on real-time CPU/GPU/RAM usage
- **Hardware Watcher** — Live FPS, CPU, GPU, and RAM monitoring in the header overlay
- **ML Learning** — Learns your hardware patterns for optimal settings over time

### ⚙️ GFX Settings Control
- **Graphics Quality** — Smooth, Balanced, HD, HDR, Ultra HD
- **FPS Unlock** — 30, 40, 60, 90, 120 FPS options
- **Shadow Toggle** — Enable/disable shadows with dual Active.sav + UserCustom.ini logic
- **Style Presets** — Classic, Colorful, Realistic, Soft, Movie
- **Profile Save/Load** — Save your custom GFX profiles

### 🎛️ Expert Mode (50+ Settings)
- **5 Categories** — CPU, GPU, Memory, Network, Advanced Tweaks
- **Fine-grained Control** — CPU affinity, shader cache, VSync, RAM cleanup intervals
- **Profile Management** — Export/import custom optimization profiles

### 🖥️ GPU Support (NVIDIA + AMD + Intel)
- **Auto Detection** — nvidia-smi, Radeon CLI, WMI fallback
- **Vendor-Specific Optimization** — Tailored registry tweaks per GPU vendor
- **NVIDIA Inspector** — Automatic NVIDIA profile optimization

### 📊 Real-time Performance Monitoring
- **Live Stats** — FPS, CPU%, GPU%, RAM, GPU Temperature, Network Latency
- **Performance Alerts** — Automatic warnings for thermal throttling, VRAM pressure, high latency
- **Intelligent Caching** — Thread-safe TTL cache reducing memory usage by 40%

### 🎨 Cyberpunk Cosmic UI
- **Futuristic Theme** — Dark cosmic gradients with neon accents
- **Responsive Design** — HD, 2K, 4K display support
- **Multiple Themes** — Cosmic, Neon Green, Red Alert

### 🧰 Toolkit
- **Desktop Shortcuts** — Auto-create PUBG shortcuts with correct icons (Global, KR, VN, TW, BGMI)
- **iPad Resolution** — Custom resolution/aspect ratio for competitive advantage
- **DNS Optimizer** — Quick-switch DNS servers (Google, Cloudflare, etc.)
- **Temp Cleaner** — Wipes ShaderCache and system temp files
- **Force Close** — Kill all GameLoop processes instantly
- **Ping Stabilizer** — Network optimization for lower latency

### ⚡ System Tweaks
- **High Priority** — Force game process to high priority
- **CPU Affinity** — Dedicate CPU cores to the game
- **RAM Cleaner** — Clear standby memory list
- **Power Plan** — Switch to High/Ultimate Performance
- **Auto-Boost** — Persistent background optimization while gaming

### 🛡️ Compatibility Manager
- **Hardware Detection** — Auto-detect conflicts and limitations
- **Feature Gating** — Disable incompatible features automatically
- **System Report** — Export full compatibility report

### 🔔 System Integration
- **Tray Icon** — Minimize to system tray
- **Game Detection** — Auto-detect GameLoop launch/exit
- **Auto-Update** — In-app update checking with integrity verification (SHA256)
- **Single Instance** — Prevent multiple copies running

---

## 📥 Download

**Latest build (public, no login required):**  
[https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest](https://github.com/Nitrodz00/NITRO-TOOLS/releases/latest)

> ⚠️ Run as **Administrator** for full functionality.

---

## 🛠️ Build from Source

```bash
pip install -r requirements.txt
python main.py
```

Build EXE locally:
```powershell
.\build_release.ps1
```

---

## 📋 Requirements
- Windows 10/11 64-bit
- Gameloop 64-bit emulator
- PUBG Mobile installed
- Run as Administrator

---

## 📬 Contact

- **Discrod:** (https://discord.gg/4bvrf3sM)
- **GitHub:** [Nitrodz00](https://github.com/Nitrodz00)
- **Repository:** [NITRO-TOOLS](https://github.com/Nitrodz00/NITRO-TOOLS)

---

<div align="center">
<b>Made with ❤️ for the PUBG Mobile community</b><br>
<i>NITROTOOLS — Level up your game.</i>
</div>
