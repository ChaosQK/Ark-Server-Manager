# ARK Server Manager

A desktop application for managing ARK: Survival Evolved and ARK: Survival Ascended dedicated servers on Windows. Built with Python and a modern HTML/CSS/JS interface via PyWebView.

![Dashboard](https://img.shields.io/badge/platform-Windows-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Install & Update** - Download SteamCMD and install/update your ARK server with one click. Supports branch selection (Live, Experimental, Public Beta, or custom)
- **Import Existing Server** - Point the app at an already-installed server; game type is auto-detected and config files are edited in-place
- **Start / Stop / Restart** - Launch and manage the server process with auto-restart support
- **Live Logs** - Real-time server log viewer with search, colour-coded output, and copy-to-clipboard
- **GameUserSettings.ini** - Full settings editor with 60+ fields, category jump chips, live search filter, presets (Official, Boosted ×3/×5/×10, Solo), and custom key/value support
- **Game.ini** - Difficulty, day/night cycle, per-level player and dino stats, engram points, and raw editor
- **Launch Arguments** - Configure map, ports, server name, password, flags, cluster settings, and active events
- **Mods** - Install and manage Steam Workshop mods by ID with metadata lookup
- **RCON Console** - Live remote console with quick-command buttons
- **Backups** - Manual and scheduled backups of your save data with retention management
- **Multi-profile** - Create and switch between multiple server profiles
- **Global Search** - Ctrl+F to instantly find any setting, flag, or option across all pages

---

## Requirements

- Windows 10/11
- Python 3.10+
- Internet connection (for SteamCMD download and mod metadata)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/ark-server-manager.git
cd ark-server-manager
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Launch the app**

Double-click `launch.bat`, or run:

```bash
python main_web.py
```

---

## Standalone Executable

To build a single self-contained `ArkServerManager.exe` (no Python installation required on the target machine):

**Run `build.bat`** - it installs PyInstaller, bundles all assets, and outputs `dist\ArkServerManager.exe`.

```
build.bat
```

> **Prerequisite:** [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) must be installed on the machine running the `.exe`. It ships with Windows 11 and most up-to-date Windows 10 installs, so it is usually already present.

The executable is fully standalone - copy `dist\ArkServerManager.exe` anywhere and run it directly. User data (config, backups) is stored in `%LOCALAPPDATA%\ARKServerManager\` as usual.

---

## Importing an Existing Server

If you already have an ARK server installed, go to **Install / Update** and use the **Import Existing Server** card:

1. Click **Browse…** and select the server's root directory (the folder containing `ShooterGame\`)
2. Click **Import** - the game type (ASE/ASA) is auto-detected from the installed executables
3. `GameUserSettings.ini` and `Game.ini` are read and written **directly** from the server's own `ShooterGame\Saved\Config\WindowsServer\` folder - no separate copy is kept

> If the config folder does not exist yet (fresh install, no first-launch), it will be created automatically the first time you save settings from the app.

---

## First-Time Setup

1. Go to **Install / Update**
2. Click **Download SteamCMD…** and choose a folder (e.g. `C:\SteamCMD`)
3. Set your **Server Installation Directory** (e.g. `C:\ARKServer`)
4. Select your game (**ASE** or **ASA**) and optionally a branch
5. Click **Install / Update Server** and wait for SteamCMD to finish
6. Go to **Launch Args** and set your server name, ports, and admin password
7. Configure **GameUserSettings** to your liking
8. Click **Start Server** on the Dashboard

---

## Project Structure

```
ark-server-manager/
├── main_web.py          # Entry point (PyWebView); handles frozen/PyInstaller paths
├── api.py               # Python ↔ JS API bridge
├── launch.bat           # Windows launcher (runs from source)
├── build.bat            # Builds dist\ArkServerManager.exe via PyInstaller
├── requirements.txt
│
├── core/
│   ├── ini_parser.py    # Custom ARK INI parser (handles duplicate keys)
│   ├── server_process.py# Server start/stop/monitor, log tailer
│   ├── steamcmd.py      # SteamCMD download, install, workshop mods
│   ├── rcon_client.py   # Source RCON protocol implementation
│   ├── backup_manager.py# Backup creation, scheduling, restore
│   ├── mod_manager.py   # Workshop mod install and management
│   └── update_checker.py# Server update detection
│
├── web/
│   ├── index.html       # App shell (SPA)
│   ├── style.css        # Catppuccin Mocha dark theme
│   └── app.js           # All UI logic, pages, search, event bus
│
└── ui/                  # Legacy tkinter UI (kept as fallback)
    ├── tab_cmdargs.py   # launch args builder (also used by api.py)
    └── tab_settings_gus.py  # GUS field definitions (also used by api.py)
```

---

## Configuration

All user data is stored in `%LOCALAPPDATA%\ARKServerManager\` (e.g. `C:\Users\<you>\AppData\Local\ARKServerManager\`). Nothing is written to the project or install directory.

> **Note:** When a server install directory is configured, `GameUserSettings.ini` and `Game.ini` are read and written **directly** in `<server_dir>\ShooterGame\Saved\Config\WindowsServer\` - not in AppData.

| Path | Description |
|------|-------------|
| `%LOCALAPPDATA%\ARKServerManager\config.json` | Global config: SteamCMD path, active profile, profile list |
| `%LOCALAPPDATA%\ARKServerManager\profiles\<name>\GameUserSettings.ini` | Fallback GUS (used only if no server dir is set) |
| `%LOCALAPPDATA%\ARKServerManager\profiles\<name>\Game.ini` | Fallback Game.ini (used only if no server dir is set) |
| `<server_dir>\ShooterGame\Saved\Config\WindowsServer\` | Live config location when a server dir is configured |
| `%LOCALAPPDATA%\ARKServerManager\backups\` | Timestamped backup archives |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Open global settings search |
| `Esc` | Close search overlay |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pywebview >= 6.0` | Native desktop window rendering HTML/CSS/JS |
| `requests >= 2.28` | SteamCMD download, Steam Workshop API |
| `Pillow >= 9.0` | Image handling (legacy tkinter UI) |

---

## Notes

- The server is launched with `CREATE_NO_WINDOW` - no separate console window appears. All output is streamed through the **Logs** page.
- ARK logs are read by tailing `ShooterGame/Saved/Logs/ShooterGame.log` directly.
- RCON requires `RCONEnabled=True` in your launch args (enabled by default) and a matching RCON password set in **GameUserSettings**.
- Mods are installed via SteamCMD and copied to `ShooterGame/Content/Mods/`. ASE only.

---

## License

MIT
