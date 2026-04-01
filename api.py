"""
Python API bridge between pywebview and the ARK server manager core modules.
All public methods are callable from JavaScript via window.pywebview.api.*
"""
from __future__ import annotations
import json
import os
import queue
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from core.ini_parser import ArkIniFile
from core.server_process import ServerProcess
from core.steamcmd import SteamCMDRunner, find_steamcmd, download_steamcmd
from core.backup_manager import BackupManager
from core.mod_manager import ModManager, get_mod_info
from core.rcon_client import RconClient, RconError
from core.update_checker import check_for_update

MANAGER_DIR = os.path.dirname(os.path.abspath(__file__))

# User data lives in %LOCALAPPDATA%\ARKServerManager so the install directory
# can be read-only and config/profiles are not committed to source control.
_APPDATA_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "ARKServerManager"
)
os.makedirs(_APPDATA_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(_APPDATA_DIR, "config.json")


def _ok(data=None):
    return {"ok": True, "data": data}

def _err(msg: str):
    return {"ok": False, "error": str(msg)}


class Api:
    def __init__(self):
        self._config: dict = self._load_config()
        self._events: queue.Queue = queue.Queue()
        self._server = ServerProcess(_APPDATA_DIR)
        self._server.add_status_callback(self._on_server_status)
        self._rcon = RconClient()
        self._backup_mgr = BackupManager(_APPDATA_DIR)
        self._mod_mgr: ModManager | None = None
        self._steamcmd: SteamCMDRunner | None = None
        self._install_log_queue: queue.Queue = queue.Queue()
        self._log_file_pos: dict[str, int] = {}
        self._init_steamcmd()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _init_steamcmd(self):
        exe = find_steamcmd(self._config.get("steamcmd_path", ""))
        self._steamcmd = SteamCMDRunner(exe or "")
        self._mod_mgr = ModManager(self._steamcmd)

    def _push(self, event_type: str, data: Any = None):
        try:
            self._events.put_nowait({"type": event_type, "data": data})
        except queue.Full:
            pass

    def _on_server_status(self, status: str):
        self._push("server_status", status)

    def _load_config(self) -> dict:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return self._default_config()

    def _save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)

    def _default_config(self) -> dict:
        return {
            "version": 1, "steamcmd_path": "", "active_profile": "default",
            "profiles": {"default": self._default_profile()},
            "window": {"geometry": "1280x820"},
        }

    def _default_profile(self) -> dict:
        return {
            "server_install_dir": "", "game": "ase", "map": "TheIsland",
            "mods": [], "auto_restart": False, "auto_restart_delay_seconds": 30,
            "backup": {"enabled": False, "interval_minutes": 60, "keep_count": 10},
            "rcon": {"host": "localhost", "port": 27020, "password": ""},
            "launch_args": {
                "MaxPlayers": 70, "Port": 7777, "QueryPort": 27015,
                "RCONEnabled": True, "RCONPort": 27020, "flags": ["-log", "-NoBattlEye"],
            },
        }

    def _get_profile(self, name: str | None = None) -> dict:
        name = name or self._config.get("active_profile", "default")
        return self._config.setdefault("profiles", {}).setdefault(name, self._default_profile())

    def _gus_path(self, profile_name: str | None = None) -> str:
        profile = self._get_profile(profile_name)
        server_dir = profile.get("server_install_dir", "")
        if server_dir:
            return os.path.join(server_dir, "ShooterGame", "Saved",
                                "Config", "WindowsServer", "GameUserSettings.ini")
        name = profile_name or self._config.get("active_profile", "default")
        return os.path.join(_APPDATA_DIR, "profiles", name, "GameUserSettings.ini")

    def _game_ini_path(self, profile_name: str | None = None) -> str:
        profile = self._get_profile(profile_name)
        server_dir = profile.get("server_install_dir", "")
        if server_dir:
            return os.path.join(server_dir, "ShooterGame", "Saved",
                                "Config", "WindowsServer", "Game.ini")
        name = profile_name or self._config.get("active_profile", "default")
        return os.path.join(_APPDATA_DIR, "profiles", name, "Game.ini")

    # ------------------------------------------------------------------ #
    #  Events (polled by JS every 200ms)                                   #
    # ------------------------------------------------------------------ #

    def get_events(self):
        events = []
        while not self._events.empty():
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                break
        return events

    # ------------------------------------------------------------------ #
    #  Config & profiles                                                   #
    # ------------------------------------------------------------------ #

    def get_config(self):
        return _ok(self._config)

    def get_profile(self):
        return _ok(self._get_profile())

    def get_profile_names(self):
        return _ok(list(self._config.get("profiles", {}).keys()))

    def switch_profile(self, name: str):
        profiles = self._config.get("profiles", {})
        if name not in profiles:
            profiles[name] = self._default_profile()
        self._config["active_profile"] = name
        self._save_config()
        return _ok(name)

    def add_profile(self, name: str):
        name = name.strip()
        if not name:
            return _err("Profile name cannot be empty")
        profiles = self._config.setdefault("profiles", {})
        if name in profiles:
            return _err(f"Profile '{name}' already exists")
        profiles[name] = self._default_profile()
        self._config["active_profile"] = name
        self._save_config()
        return _ok(name)

    def save_profile_basic(self, data: dict):
        """Save server_install_dir, game, map into the active profile."""
        profile = self._get_profile()
        for k in ("server_install_dir", "game", "map", "branch", "auto_restart",
                  "auto_restart_delay_seconds"):
            if k in data:
                profile[k] = data[k]
        self._save_config()
        return _ok()

    def save_launch_args(self, data: dict):
        profile = self._get_profile()
        profile["launch_args"] = data
        if "game" in data:
            profile["game"] = data["game"]
        if "map" in data:
            profile["map"] = data["map"]
        self._save_config()
        return _ok()

    def save_rcon_settings(self, data: dict):
        profile = self._get_profile()
        profile["rcon"] = data
        self._save_config()
        return _ok()

    def save_backup_settings(self, data: dict):
        profile = self._get_profile()
        profile["backup"] = data
        self._save_config()
        return _ok()

    # ------------------------------------------------------------------ #
    #  GUS Settings                                                        #
    # ------------------------------------------------------------------ #

    def get_gus_values(self):
        """Return flat dict of all GUS key→value pairs plus a __sections__ map."""
        path = self._gus_path()
        values = {}
        sections_map = {}
        if os.path.isfile(path):
            ini = ArkIniFile(path)
            ini.load()
            for section in ini.get_sections():
                for k, v in ini.get_section_items(section):
                    values[k] = v
                    sections_map[k] = section
        values["__sections__"] = sections_map
        return _ok(values)

    def save_gus_values(self, values: dict, custom_entries=None):
        """Write flat dict of key→value pairs to the profile's GUS.ini.
        custom_entries is an optional list of {s, k, v} dicts for arbitrary keys."""
        from ui.tab_settings_gus import SECTIONS_FIELDS
        path = self._gus_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ini = ArkIniFile(path)
        if os.path.isfile(path):
            ini.load()
        # Build key→section map from known fields
        key_section = {}
        for fields in SECTIONS_FIELDS.values():
            for f in fields:
                key_section[f["k"]] = f["s"]
        for key, value in values.items():
            if key == "__sections__":
                continue
            section = key_section.get(key, "ServerSettings")
            ini.set_value(section, key, str(value))
        # Write custom entries with their explicit sections
        if custom_entries:
            for entry in custom_entries:
                s = str(entry.get("s", "ServerSettings")).strip()
                k = str(entry.get("k", "")).strip()
                v = str(entry.get("v", ""))
                if k:
                    ini.set_value(s, k, v)
        ini.save()
        return _ok()

    def sync_gus_to_server(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        src = self._gus_path()
        dst_dir = os.path.join(server_dir, "ShooterGame", "Saved", "Config", "WindowsServer")
        dst = os.path.join(dst_dir, "GameUserSettings.ini")
        if os.path.abspath(src) == os.path.abspath(dst):
            return _ok()  # Already saving directly to server config
        if not os.path.isfile(src):
            return _err("Profile GUS.ini not found - save it first")
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        return _ok()

    def load_gus_from_server(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        src = os.path.join(server_dir, "ShooterGame", "Saved",
                           "Config", "WindowsServer", "GameUserSettings.ini")
        if not os.path.isfile(src):
            return _err(f"File not found: {src}")
        dst = self._gus_path()
        if os.path.abspath(src) == os.path.abspath(dst):
            return _ok()  # Already reading directly from server config
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return _ok()

    # ------------------------------------------------------------------ #
    #  Game.ini                                                            #
    # ------------------------------------------------------------------ #

    def get_game_ini_values(self):
        path = self._game_ini_path()
        section = "/script/shootergame.shootergamemode"
        result = {}
        if os.path.isfile(path):
            ini = ArkIniFile(path)
            ini.load()
            result = {k: v for k, v in ini.get_section_items(section)}
            # Engram points (duplicate keys)
            result["_engram_points"] = ini.get_all_values(section, "OverridePlayerLevelEngramPoints")
        return _ok(result)

    def get_game_ini_text(self):
        path = self._game_ini_path()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
                return _ok(f.read())
        return _ok("")

    def save_game_ini_text(self, text: str):
        path = self._game_ini_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(text)
        return _ok()

    def save_game_ini_values(self, values: dict):
        section = "/script/shootergame.shootergamemode"
        path = self._game_ini_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ini = ArkIniFile(path)
        if os.path.isfile(path):
            ini.load()
        engrams = values.pop("_engram_points", [])
        for k, v in values.items():
            ini.set_value(section, k, str(v))
        ini.set_all_values(section, "OverridePlayerLevelEngramPoints",
                            [str(p) for p in engrams if str(p).strip()])
        ini.save()
        return _ok()

    def sync_game_ini_to_server(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        src = self._game_ini_path()
        dst_dir = os.path.join(server_dir, "ShooterGame", "Saved", "Config", "WindowsServer")
        dst = os.path.join(dst_dir, "Game.ini")
        if os.path.abspath(src) == os.path.abspath(dst):
            return _ok()  # Already saving directly to server config
        if not os.path.isfile(src):
            return _err("Profile Game.ini not found - save it first")
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        return _ok()

    def load_game_ini_from_server(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        src = os.path.join(server_dir, "ShooterGame", "Saved",
                           "Config", "WindowsServer", "Game.ini")
        if not os.path.isfile(src):
            return _err(f"File not found: {src}")
        dst = self._game_ini_path()
        if os.path.abspath(src) == os.path.abspath(dst):
            return _ok()  # Already reading directly from server config
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return _ok()

    # ------------------------------------------------------------------ #
    #  Server control                                                      #
    # ------------------------------------------------------------------ #

    def _build_launch_args_from_profile(self) -> list[str]:
        from ui.tab_cmdargs import build_launch_args
        return build_launch_args(self._get_profile())

    def start_server(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        args = self._build_launch_args_from_profile()
        ok = self._server.start(
            server_dir, profile.get("game", "ase"), args,
            auto_restart=profile.get("auto_restart", False),
            auto_restart_delay=profile.get("auto_restart_delay_seconds", 30),
        )
        if ok:
            threading.Thread(target=self._start_server_log_drain, daemon=True).start()
        return _ok() if ok else _err("Failed to start - check that the server is installed")

    def stop_server(self):
        self._server.stop(graceful=True)
        return _ok()

    def restart_server(self):
        profile = self._get_profile()
        args = self._build_launch_args_from_profile()
        self._server.restart(profile.get("server_install_dir", ""),
                              profile.get("game", "ase"), args)
        return _ok()

    def get_server_status(self):
        ut = self._server.uptime
        uptime_str = ""
        if ut:
            h, r = divmod(int(ut.total_seconds()), 3600)
            m, s = divmod(r, 60)
            uptime_str = f"{h:02d}:{m:02d}:{s:02d}"
        return _ok({
            "status": self._server.status,
            "pid": self._server.pid,
            "uptime": uptime_str,
        })

    # ------------------------------------------------------------------ #
    #  SteamCMD / Install                                                  #
    # ------------------------------------------------------------------ #

    def get_steamcmd_info(self):
        path = self._config.get("steamcmd_path", "")
        detected = find_steamcmd(path)
        return _ok({"configured": path, "detected": detected or ""})

    def set_steamcmd_path(self, path: str):
        self._config["steamcmd_path"] = path
        self._steamcmd.exe = path
        self._save_config()
        return _ok()

    def download_steamcmd(self, dest_dir: str):
        def _run():
            try:
                def _cb(msg, frac):
                    self._push("install_log", msg)
                    self._push("install_progress", round(frac * 100))
                exe = download_steamcmd(dest_dir, _cb)
                self._config["steamcmd_path"] = exe
                self._steamcmd.exe = exe
                self._save_config()
                self._push("install_done", {"ok": True, "msg": "SteamCMD downloaded."})
            except Exception as e:
                self._push("install_done", {"ok": False, "msg": str(e)})
        threading.Thread(target=_run, daemon=True).start()
        return _ok()

    def install_server(self):
        scmd = self._config.get("steamcmd_path", "") or find_steamcmd()
        if not scmd or not os.path.isfile(scmd):
            return _err("SteamCMD not found - set the path or download it first")
        profile = self._get_profile()
        install_dir = profile.get("server_install_dir", "")
        if not install_dir:
            return _err("Server install directory not set")
        game = profile.get("game", "ase")
        branch = profile.get("branch", "") or ""
        self._steamcmd.exe = scmd
        self._steamcmd.install_or_update_server(
            install_dir, game, self._install_log_queue, self._on_install_done, branch=branch
        )
        # Drain install log queue to events
        threading.Thread(target=self._drain_install_log, daemon=True).start()
        return _ok()

    def _drain_install_log(self):
        import time
        # Drain until the install_done callback sets a sentinel None
        while True:
            try:
                line = self._install_log_queue.get(timeout=0.2)
                if line is None:
                    break
                self._push("install_log", line)
            except queue.Empty:
                continue

    def _start_server_log_drain(self):
        """Drain server log_queue into the in-memory buffer (ServerProcess._log_buffer).
        We do NOT push server_log events - the JS logs page polls get_log_lines() instead,
        which avoids flooding the event queue with thousands of lines and blocking the JS thread."""
        while True:
            try:
                self._server.log_queue.get(timeout=1.0)
                # ServerProcess._log() already writes to _log_buffer; just drain the queue
            except queue.Empty:
                if self._server.status == "stopped" and self._server.log_queue.empty():
                    break

    def get_log_lines(self, n: int = 500):
        """Return the last n lines from the server log buffer."""
        lines = list(self._server._log_buffer)[-int(n):]
        return _ok(lines)

    def _on_install_done(self, success: bool):
        self._install_log_queue.put(None)  # sentinel to stop drain thread
        self._push("install_done", {"ok": success,
                                     "msg": "Done!" if success else "Install failed."})

    def cancel_install(self):
        if self._steamcmd:
            self._steamcmd.cancel()
        return _ok()

    def check_update(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        game = profile.get("game", "ase")
        def _cb(available, local, remote):
            self._push("update_check", {"available": available,
                                         "local": local, "remote": remote})
        check_for_update(server_dir, game, _cb)
        return _ok()

    # ------------------------------------------------------------------ #
    #  Logs                                                                #
    # ------------------------------------------------------------------ #

    def get_log_lines(self, max_lines: int = 500):
        lines = list(self._server._log_buffer)[-max_lines:]
        return _ok(lines)

    def get_log_files(self):
        logs_dir = os.path.join(MANAGER_DIR, "logs")
        if not os.path.isdir(logs_dir):
            return _ok([])
        files = sorted(
            [f for f in os.listdir(logs_dir) if f.endswith(".log")],
            reverse=True,
        )
        return _ok(files)

    def get_log_file_content(self, filename: str):
        log_path = os.path.join(MANAGER_DIR, "logs", os.path.basename(filename))
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                return _ok(f.read())
        except OSError as e:
            return _err(str(e))

    # ------------------------------------------------------------------ #
    #  Mods                                                                #
    # ------------------------------------------------------------------ #

    def get_mods(self):
        profile = self._get_profile()
        return _ok(profile.get("mods", []))

    def fetch_mod_info(self, mod_id: str):
        info = get_mod_info(str(mod_id))
        return _ok(info)

    def install_mod(self, mod_id: str):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        scmd_path = self._config.get("steamcmd_path", "")
        steamcmd_dir = os.path.dirname(scmd_path) if scmd_path else ""
        if not steamcmd_dir or not server_dir:
            return _err("Configure SteamCMD and server directory first")
        log_q: queue.Queue = queue.Queue()

        def _done(success: bool):
            if success:
                mods = profile.setdefault("mods", [])
                if not any(str(m.get("id")) == str(mod_id) for m in mods):
                    info = get_mod_info(mod_id)
                    mods.append({"id": mod_id, "name": info["title"], "enabled": True})
                    self._save_config()
            self._push("mod_install_done", {"mod_id": mod_id, "ok": success})

        self._mod_mgr.install_mod(mod_id, steamcmd_dir, server_dir, log_q, _done)

        def _drain():
            import time
            for _ in range(600):
                while not log_q.empty():
                    try:
                        self._push("install_log", log_q.get_nowait())
                    except queue.Empty:
                        break
                time.sleep(0.2)
        threading.Thread(target=_drain, daemon=True).start()
        return _ok()

    def remove_mod(self, mod_id: str):
        profile = self._get_profile()
        profile["mods"] = [m for m in profile.get("mods", [])
                            if str(m.get("id")) != str(mod_id)]
        self._save_config()
        return _ok()

    def toggle_mod(self, mod_id: str):
        profile = self._get_profile()
        for m in profile.get("mods", []):
            if str(m.get("id")) == str(mod_id):
                m["enabled"] = not m.get("enabled", True)
        self._save_config()
        return _ok()

    # ------------------------------------------------------------------ #
    #  Backups                                                             #
    # ------------------------------------------------------------------ #

    def get_backups(self):
        entries = self._backup_mgr.list_backups()
        return _ok([{
            "path": str(e.path),
            "label": e.label,
            "timestamp": e.timestamp_str,
            "size": e.size_str,
        } for e in entries])

    def create_backup(self):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        def _run():
            result = self._backup_mgr.create_backup(
                server_dir, label="manual",
                progress_cb=lambda m: self._push("backup_log", m),
            )
            self._push("backup_done", {"ok": bool(result)})
        threading.Thread(target=_run, daemon=True).start()
        return _ok()

    def restore_backup(self, backup_path: str):
        profile = self._get_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            return _err("Server install directory not set")
        def _run():
            ok = self._backup_mgr.restore_backup(
                Path(backup_path), server_dir,
                progress_cb=lambda m: self._push("backup_log", m),
            )
            self._push("backup_done", {"ok": ok})
        threading.Thread(target=_run, daemon=True).start()
        return _ok()

    def delete_backup(self, backup_path: str):
        ok = self._backup_mgr.delete_backup(Path(backup_path))
        return _ok() if ok else _err("Delete failed")

    def apply_backup_schedule(self, data: dict):
        profile = self._get_profile()
        profile["backup"] = data
        self._save_config()
        self._backup_mgr.stop_schedule()
        if data.get("enabled") and profile.get("server_install_dir"):
            self._backup_mgr.schedule_backup(
                profile["server_install_dir"],
                int(data.get("interval_minutes", 60)),
                int(data.get("keep_count", 10)),
                on_complete=lambda m: self._push("backup_log", m),
            )
        return _ok()

    # ------------------------------------------------------------------ #
    #  RCON                                                                #
    # ------------------------------------------------------------------ #

    def rcon_connect(self, host: str, port: int, password: str):
        try:
            self._rcon.connect(host, int(port), password)
            return _ok()
        except RconError as e:
            return _err(str(e))

    def rcon_command(self, command: str):
        if not self._rcon.connected:
            return _err("Not connected")
        try:
            resp = self._rcon.send_command(command)
            return _ok(resp or "(no response)")
        except RconError as e:
            self._rcon.connected = False
            return _err(str(e))

    def rcon_disconnect(self):
        self._rcon.disconnect()
        return _ok()

    def rcon_status(self):
        return _ok({"connected": self._rcon.connected})

    # ------------------------------------------------------------------ #
    #  File dialogs (must be called from main thread via pywebview)        #
    # ------------------------------------------------------------------ #

    def browse_folder(self):
        try:
            import webview
            result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
            if result:
                return _ok(result[0])
        except Exception:
            pass
        return _ok(None)

    def browse_file(self, exts: str = ""):
        try:
            import webview
            ft = (exts,) if exts else ("All files (*.*)",)
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG, file_types=ft)
            if result:
                return _ok(result[0])
        except Exception:
            pass
        return _ok(None)

    def open_folder_in_explorer(self, path: str):
        import subprocess
        if os.path.isdir(path):
            subprocess.Popen(["explorer", path])
        return _ok()

    # ------------------------------------------------------------------ #
    #  Misc                                                                #
    # ------------------------------------------------------------------ #

    def import_server(self, server_dir: str):
        """Import an existing ARK server installation into the active profile.
        Auto-detects game type (ASE/ASA) and reports which config files are present."""
        server_dir = server_dir.strip()
        if not server_dir or not os.path.isdir(server_dir):
            return _err(f"Directory not found: {server_dir}")

        ase_exe = os.path.join(server_dir, "ShooterGame", "Binaries", "Win64", "ShooterGameServer.exe")
        asa_exe = os.path.join(server_dir, "ShooterGame", "Binaries", "Win64", "ArkAscendedServer.exe")
        if os.path.isfile(asa_exe):
            game = "asa"
        elif os.path.isfile(ase_exe):
            game = "ase"
        else:
            game = None  # Can't detect; user can change it manually

        profile = self._get_profile()
        profile["server_install_dir"] = server_dir
        if game:
            profile["game"] = game
        self._save_config()

        cfg_dir = os.path.join(server_dir, "ShooterGame", "Saved", "Config", "WindowsServer")
        return _ok({
            "server_dir": server_dir,
            "game": game or profile.get("game", "ase"),
            "game_detected": game is not None,
            "has_gus": os.path.isfile(os.path.join(cfg_dir, "GameUserSettings.ini")),
            "has_game_ini": os.path.isfile(os.path.join(cfg_dir, "Game.ini")),
        })

    def get_manager_dir(self):
        return _ok(_APPDATA_DIR)
