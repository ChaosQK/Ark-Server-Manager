"""
Root application window. Manages config, profiles, notebook tabs, and status bar.
"""
from __future__ import annotations
import json
import os
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from core.server_process import ServerProcess
from core.steamcmd import SteamCMDRunner, find_steamcmd
from core.backup_manager import BackupManager
from core.mod_manager import ModManager

# Tab imports (lazy to allow individual module errors to surface cleanly)
from ui.tab_dashboard import DashboardTab
from ui.tab_install import InstallTab
from ui.tab_settings_gus import SettingsGUSTab
from ui.tab_settings_game import SettingsGameTab
from ui.tab_cmdargs import CmdArgsTab
from ui.tab_mods import ModsTab
from ui.tab_logs import LogsTab
from ui.tab_backup import BackupTab
from ui.tab_rcon import RconTab

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
TAB_BG = "#181825"


def _apply_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("TButton",
                    background="#313244", foreground=FG,
                    borderwidth=0, focusthickness=0, relief="flat",
                    padding=(8, 4))
    style.map("TButton",
              background=[("active", "#45475a"), ("pressed", "#585b70")])
    style.configure("Accent.TButton",
                    background=ACCENT, foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
    style.map("Accent.TButton",
              background=[("active", "#74c7ec"), ("pressed", "#89dceb")])
    style.configure("Danger.TButton",
                    background="#f38ba8", foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
    style.map("Danger.TButton",
              background=[("active", "#eba0ac")])
    style.configure("TEntry",
                    fieldbackground="#313244", foreground=FG,
                    insertcolor=FG, borderwidth=1,
                    relief="flat")
    style.configure("TCombobox",
                    fieldbackground="#313244", foreground=FG,
                    selectbackground="#45475a", selectforeground=FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", "#313244")])
    style.configure("TCheckbutton",
                    background=BG, foreground=FG,
                    indicatorcolor="#313244", indicatorrelief="flat")
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT)])
    style.configure("TNotebook", background=TAB_BG, borderwidth=0, tabmargins=0)
    style.configure("TNotebook.Tab",
                    background="#313244", foreground=FG,
                    padding=(12, 6), borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", BG)],
              foreground=[("selected", ACCENT)])
    style.configure("TLabelframe", background=BG, foreground=ACCENT,
                    relief="flat", borderwidth=1)
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"))
    style.configure("TScrollbar", background="#313244", troughcolor=BG,
                    arrowcolor=FG, borderwidth=0)
    style.configure("Treeview",
                    background="#181825", foreground=FG,
                    fieldbackground="#181825", rowheight=24,
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    background="#313244", foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Treeview",
              background=[("selected", "#45475a")],
              foreground=[("selected", FG)])
    style.configure("TProgressbar",
                    background=ACCENT, troughcolor="#313244",
                    borderwidth=0, thickness=6)
    style.configure("Separator.TFrame", background="#313244")


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ARK Server Manager")
        self.root.configure(bg=BG)
        self.root.minsize(900, 620)

        self._manager_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_path = os.path.join(self._manager_dir, "config.json")
        self.config = self._load_config()

        _apply_theme(root)
        self._set_icon()
        self._restore_geometry()

        # Core services
        self.server = ServerProcess(self._manager_dir)
        self.server.add_status_callback(self._on_server_status)

        steamcmd_exe = find_steamcmd(self.config.get("steamcmd_path", ""))
        self.steamcmd = SteamCMDRunner(steamcmd_exe or "")
        self.backup_mgr = BackupManager(self._manager_dir)
        self.mod_mgr = ModManager(self.steamcmd)

        # Status bar vars
        self._status_text = tk.StringVar(value="Stopped")
        self._players_text = tk.StringVar(value="Players: —")
        self._uptime_text = tk.StringVar(value="")
        self._profile_var = tk.StringVar(value=self.config.get("active_profile", "default"))

        self._build_ui()
        self._start_uptime_poll()

        # Restore backup schedule if configured
        profile = self.get_active_profile()
        backup_cfg = profile.get("backup", {})
        if backup_cfg.get("enabled") and profile.get("server_install_dir"):
            self.backup_mgr.schedule_backup(
                profile["server_install_dir"],
                backup_cfg.get("interval_minutes", 60),
                backup_cfg.get("keep_count", 10),
            )

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def _load_config(self) -> dict:
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {
                "version": 1,
                "steamcmd_path": "",
                "active_profile": "default",
                "profiles": {"default": self._default_profile()},
                "window": {"geometry": "1280x820"},
            }

    def save_config(self) -> None:
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except OSError as e:
            messagebox.showerror("Save Error", f"Could not save config:\n{e}")

    def _default_profile(self) -> dict:
        return {
            "server_install_dir": "",
            "game": "ase",
            "map": "TheIsland",
            "mods": [],
            "auto_restart": False,
            "auto_restart_delay_seconds": 30,
            "backup": {"enabled": False, "interval_minutes": 60, "keep_count": 10},
            "rcon": {"host": "localhost", "port": 27020, "password": ""},
            "launch_args": {
                "MaxPlayers": 70, "Port": 7777, "QueryPort": 27015,
                "RCONEnabled": True, "flags": ["-log", "-NoBattlEye"],
            },
        }

    def get_active_profile(self) -> dict:
        name = self.config.get("active_profile", "default")
        profiles = self.config.setdefault("profiles", {})
        if name not in profiles:
            profiles[name] = self._default_profile()
        return profiles[name]

    def get_profile_names(self) -> list[str]:
        return list(self.config.get("profiles", {}).keys())

    def add_profile(self, name: str) -> None:
        self.config.setdefault("profiles", {})[name] = self._default_profile()
        self.save_config()

    def switch_profile(self, name: str) -> None:
        self.config["active_profile"] = name
        self._profile_var.set(name)
        self.save_config()
        self._reload_tabs()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _set_icon(self) -> None:
        ico = os.path.join(self._manager_dir, "assets", "icon.ico")
        if os.path.isfile(ico):
            try:
                self.root.iconbitmap(ico)
            except tk.TclError:
                pass

    def _restore_geometry(self) -> None:
        geom = self.config.get("window", {}).get("geometry", "1280x820")
        self.root.geometry(geom)

    def _build_ui(self) -> None:
        # Top bar: title + profile selector
        topbar = tk.Frame(self.root, bg="#181825", height=44)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        tk.Label(topbar, text="  ARK Server Manager", bg="#181825", fg=ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=8)

        # Profile selector on the right
        tk.Label(topbar, text="Profile:", bg="#181825", fg=FG,
                 font=("Segoe UI", 10)).pack(side=tk.RIGHT, padx=(0, 4))
        profiles = self.get_profile_names()
        self._profile_combo = ttk.Combobox(topbar, textvariable=self._profile_var,
                                            values=profiles, state="readonly", width=18)
        self._profile_combo.pack(side=tk.RIGHT, padx=(0, 8), pady=8)
        self._profile_combo.bind("<<ComboboxSelected>>",
                                  lambda _: self.switch_profile(self._profile_var.get()))

        ttk.Button(topbar, text="+", width=3,
                   command=self._new_profile_dialog).pack(side=tk.RIGHT, padx=2)

        # Separator
        tk.Frame(self.root, bg="#313244", height=1).pack(fill=tk.X)

        # Notebook
        self._notebook = ttk.Notebook(self.root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self._tabs: dict[str, tk.Frame] = {}
        self._build_tabs()

        # Status bar
        self._build_statusbar()

    def _build_tabs(self) -> None:
        profile = self.get_active_profile()

        tabs = [
            ("Dashboard",   DashboardTab),
            ("Install",     InstallTab),
            ("Settings",    SettingsGUSTab),
            ("Game.ini",    SettingsGameTab),
            ("Launch Args", CmdArgsTab),
            ("Mods",        ModsTab),
            ("Logs",        LogsTab),
            ("Backups",     BackupTab),
            ("RCON",        RconTab),
        ]
        for label, TabClass in tabs:
            frame = tk.Frame(self._notebook, bg=BG)
            self._notebook.add(frame, text=f"  {label}  ")
            try:
                tab = TabClass(frame, self)
                tab.pack(fill=tk.BOTH, expand=True)
                self._tabs[label] = tab
            except Exception as e:
                tk.Label(frame, text=f"Error loading tab:\n{e}",
                          bg=BG, fg="#f38ba8").pack(padx=20, pady=20)

    def _reload_tabs(self) -> None:
        """Refresh all tabs after profile switch."""
        for tab in self._tabs.values():
            if hasattr(tab, "refresh"):
                try:
                    tab.refresh()
                except Exception:
                    pass

    def _build_statusbar(self) -> None:
        bar = tk.Frame(self.root, bg="#181825", height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        tk.Frame(bar, bg="#313244", height=1).pack(fill=tk.X, side=tk.TOP)

        tk.Label(bar, textvariable=self._status_text,
                  bg="#181825", fg=FG, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=12)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, pady=4)
        tk.Label(bar, textvariable=self._players_text,
                  bg="#181825", fg=FG, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=12)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, pady=4)
        tk.Label(bar, textvariable=self._uptime_text,
                  bg="#181825", fg=FG, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=12)

        # Right side: manager dir
        tk.Label(bar, text=f"  {self._manager_dir}",
                  bg="#181825", fg="#585b70", font=("Segoe UI", 8)).pack(side=tk.RIGHT, padx=8)

    # ------------------------------------------------------------------
    # Events / polling
    # ------------------------------------------------------------------

    def _on_server_status(self, status: str) -> None:
        color_map = {
            "running":  "#a6e3a1",
            "starting": "#f9e2af",
            "stopped":  "#f38ba8",
            "crashed":  "#fab387",
        }
        color = color_map.get(status, FG)
        self._status_text.set(f"  ● {status.capitalize()}")
        # Update dashboard if loaded
        dash = self._tabs.get("Dashboard")
        if dash and hasattr(dash, "on_status_change"):
            self.root.after(0, dash.on_status_change, status)

    def _start_uptime_poll(self) -> None:
        def _poll():
            ut = self.server.uptime
            if ut:
                h, rem = divmod(int(ut.total_seconds()), 3600)
                m, s = divmod(rem, 60)
                self._uptime_text.set(f"Uptime: {h:02d}:{m:02d}:{s:02d}")
            else:
                self._uptime_text.set("")
            self.root.after(1000, _poll)
        _poll()

    def _new_profile_dialog(self) -> None:
        from tkinter.simpledialog import askstring
        name = askstring("New Profile", "Profile name:", parent=self.root)
        if name and name.strip():
            name = name.strip()
            if name in self.get_profile_names():
                messagebox.showwarning("Duplicate", f"Profile '{name}' already exists.")
                return
            self.add_profile(name)
            self._profile_combo["values"] = self.get_profile_names()
            self.switch_profile(name)

    def _on_close(self) -> None:
        # Save window geometry
        self.config.setdefault("window", {})["geometry"] = self.root.geometry()
        self.save_config()
        # Stop backup scheduler
        self.backup_mgr.stop_schedule()
        self.root.destroy()
