"""Dashboard tab — server status, controls, update check."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from ui.widgets.status_indicator import StatusIndicator
from core.update_checker import check_for_update

BG = "#1e1e2e"
BG2 = "#181825"
FG = "#cdd6f4"
ACCENT = "#89b4fa"


class DashboardTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._build()

    def _build(self) -> None:
        # Main content area with padding
        content = tk.Frame(self, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # --- Status card ---
        status_frame = ttk.LabelFrame(content, text="Server Status", padding=12)
        status_frame.pack(fill=tk.X, pady=(0, 12))

        row1 = tk.Frame(status_frame, bg=BG)
        row1.pack(fill=tk.X)

        self._indicator = StatusIndicator(row1, "stopped", bg=BG)
        self._indicator.pack(side=tk.LEFT)

        self._uptime_var = tk.StringVar(value="")
        tk.Label(row1, textvariable=self._uptime_var,
                  bg=BG, fg="#585b70", font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        row2 = tk.Frame(status_frame, bg=BG)
        row2.pack(fill=tk.X, pady=(8, 0))

        self._map_var = tk.StringVar(value="Map: —")
        self._port_var = tk.StringVar(value="Port: —")
        self._pid_var = tk.StringVar(value="PID: —")

        for var in (self._map_var, self._port_var, self._pid_var):
            tk.Label(row2, textvariable=var, bg=BG, fg=FG,
                      font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 24))

        # --- Controls ---
        ctrl_frame = ttk.LabelFrame(content, text="Controls", padding=12)
        ctrl_frame.pack(fill=tk.X, pady=(0, 12))

        btn_row = tk.Frame(ctrl_frame, bg=BG)
        btn_row.pack(fill=tk.X)

        self._start_btn = ttk.Button(btn_row, text="▶  Start",
                                      style="Accent.TButton", command=self._start)
        self._start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._stop_btn = ttk.Button(btn_row, text="■  Stop",
                                     style="Danger.TButton", command=self._stop,
                                     state=tk.DISABLED)
        self._stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._restart_btn = ttk.Button(btn_row, text="↺  Restart",
                                        command=self._restart, state=tk.DISABLED)
        self._restart_btn.pack(side=tk.LEFT)

        opt_row = tk.Frame(ctrl_frame, bg=BG)
        opt_row.pack(fill=tk.X, pady=(10, 0))

        profile = self._app.get_active_profile()
        self._auto_restart_var = tk.BooleanVar(value=profile.get("auto_restart", False))
        ttk.Checkbutton(opt_row, text="Auto-restart on crash",
                         variable=self._auto_restart_var,
                         command=self._save_auto_restart).pack(side=tk.LEFT)

        # --- Update ---
        update_frame = ttk.LabelFrame(content, text="Server Update", padding=12)
        update_frame.pack(fill=tk.X, pady=(0, 12))

        self._build_var = tk.StringVar(value="Build: —")
        tk.Label(update_frame, textvariable=self._build_var,
                  bg=BG, fg=FG, font=("Segoe UI", 10)).pack(side=tk.LEFT)

        self._update_btn = ttk.Button(update_frame, text="Check for Updates",
                                       command=self._check_update)
        self._update_btn.pack(side=tk.RIGHT)

        self._update_status_var = tk.StringVar(value="")
        self._update_lbl = tk.Label(update_frame, textvariable=self._update_status_var,
                                     bg=BG, fg="#f9e2af", font=("Segoe UI", 10))
        self._update_lbl.pack(side=tk.RIGHT, padx=12)

        # --- Quick stats (refreshed by uptime poll) ---
        self._refresh_info()
        self._poll_pid()

    def refresh(self) -> None:
        """Called on profile switch."""
        profile = self._app.get_active_profile()
        self._auto_restart_var.set(profile.get("auto_restart", False))
        self._refresh_info()

    def _refresh_info(self) -> None:
        profile = self._app.get_active_profile()
        la = profile.get("launch_args", {})
        self._map_var.set(f"Map: {profile.get('map', '—')}")
        self._port_var.set(f"Port: {la.get('Port', 7777)} / {la.get('QueryPort', 27015)}")

    def on_status_change(self, status: str) -> None:
        self._indicator.set_status(status)
        running = status == "running"
        starting = status == "starting"
        self._start_btn.config(state=tk.DISABLED if (running or starting) else tk.NORMAL)
        self._stop_btn.config(state=tk.NORMAL if (running or starting) else tk.DISABLED)
        self._restart_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        if status == "stopped":
            self._pid_var.set("PID: —")
            self._uptime_var.set("")

    def _poll_pid(self) -> None:
        pid = self._app.server.pid
        self._pid_var.set(f"PID: {pid}" if pid else "PID: —")
        ut = self._app.server.uptime
        if ut:
            h, rem = divmod(int(ut.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            self._uptime_var.set(f"  Uptime: {h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self._poll_pid)

    def _start(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            messagebox.showwarning("Not Configured",
                                    "Set the server install directory in the Install tab first.")
            return

        # Build launch args from profile
        from ui.tab_cmdargs import build_launch_args
        args = build_launch_args(profile)

        self._app.server.start(
            server_dir,
            profile.get("game", "ase"),
            args,
            auto_restart=self._auto_restart_var.get(),
            auto_restart_delay=profile.get("auto_restart_delay_seconds", 30),
        )
        # Switch to logs tab
        self._app._notebook.select(6)  # Logs tab index

    def _stop(self) -> None:
        if messagebox.askyesno("Stop Server", "Stop the server? Players will be disconnected."):
            self._app.server.stop(graceful=True)

    def _restart(self) -> None:
        profile = self._app.get_active_profile()
        from ui.tab_cmdargs import build_launch_args
        args = build_launch_args(profile)
        self._app.server.restart(
            profile.get("server_install_dir", ""),
            profile.get("game", "ase"),
            args,
        )

    def _save_auto_restart(self) -> None:
        self._app.get_active_profile()["auto_restart"] = self._auto_restart_var.get()
        self._app.save_config()

    def _check_update(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        game = profile.get("game", "ase")
        self._update_status_var.set("Checking...")
        self._update_btn.config(state=tk.DISABLED)

        def _cb(available, local, remote):
            self.after(0, self._on_update_result, available, local, remote)

        check_for_update(server_dir, game, _cb)

    def _on_update_result(self, available: bool, local: str, remote: str) -> None:
        self._update_btn.config(state=tk.NORMAL)
        self._build_var.set(f"Build: {local}")
        if available:
            self._update_status_var.set(f"Update available! → {remote}")
            self._update_lbl.config(fg="#f9e2af")
        else:
            self._update_status_var.set("Up to date")
            self._update_lbl.config(fg="#a6e3a1")
