# SHIFTEDMIND

> **Mind the device. Shift the frame.**

A modular Android security toolkit built from scratch with a custom
terminal interface. SHIFTEDMIND wraps ADB into an interactive CLI for
device reconnaissance, package analysis, file operations, and — most
importantly — static APK analysis.

Built for learning mobile security hands-on.

---

## Features

| # | Module | What it does |
|---|--------|--------------|
| 1 | **Device Info** | Model, Android version, SDK, ABI, build ID |
| 2 | **Battery & Power** | Battery stats, screen state |
| 3 | **Packages** | List / search / launch / stop / clear / uninstall apps |
| 4 | **Network** | IPs, WiFi info, open ports, ping |
| 5 | **Files** | Browse /sdcard, pull files, push files |
| 6 | **Capture** | Screenshots, screen recording |
| 7 | **Logcat** | Dump filtered logs, clear buffer |
| 8 | **Switch Device** | Multi-device support |
| 9 | **APK Analyzer** | Pull APKs + static analysis (permissions, exported components, hardcoded URLs, certs, hashes) |

---

## Requirements

- **Python 3.10+**
- **ADB** (Android Platform Tools) on your PATH
- A USB-debuggable Android device (or an emulator)
- Python deps: `rich`, `androguard`

---

## Install

git clone https://github.com/Eno-obongumana/SHIFTEDMIND.git
cd SHIFTEDMIND

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

Verify ADB:

adb devices

---

## Usage

python main.py

Or with the launcher:

./shift

---

## Project Layout

shiftedmind/
├── core/
│   ├── adb.py
│   ├── config.py
│   └── logger.py
├── modules/
│   ├── device.py
│   ├── packages.py
│   ├── network.py
│   ├── files.py
│   ├── logcat.py
│   ├── capture.py
│   ├── apk.py
│   └── apk_menu.py
├── ui/
│   ├── banner.py
│   ├── widgets.py
│   └── menu.py
├── data/
├── main.py
└── requirements.txt



## Legal

See DISCLAIMER.md. Only use on devices and applications you own
or have explicit permission to test.

Licensed under the MIT License — see LICENSE.
