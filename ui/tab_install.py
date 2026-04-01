"""Install tab - SteamCMD path, server directory, install/update."""
from __future__ import annotations
import os
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from core.steamcmd import find_steamcmd, download_steamcmd, SteamCMDRunner

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"


class InstallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._log_queue: queue.Queue = queue.Queue()
        self._build()
        self.refresh()

    def _build(self) -> None:
        content = tk.Frame(self, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # --- SteamCMD ---
        scmd_frame = ttk.LabelFrame(content, text="SteamCMD", padding=12)
        scmd_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(scmd_frame, text="SteamCMD Path:", bg=BG, fg=FG).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._scmd_var = tk.StringVar()
        ttk.Entry(scmd_frame, textvariable=self._scmd_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(scmd_frame, text="Browse...",
                   command=self._browse_scmd).grid(row=0, column=2)
        ttk.Button(scmd_frame, text="Auto-detect",
                   command=self._autodetect_scmd).grid(row=0, column=3, padx=(8, 0))

        self._scmd_status = tk.Label(scmd_frame, text="", bg=BG, fg="#f38ba8",
                                      font=("Segoe UI", 9))
        self._scmd_status.grid(row=1, column=1, columnspan=3, sticky="w", pady=(4, 0))

        ttk.Button(scmd_frame, text="Download SteamCMD (if not installed)",
                   command=self._download_scmd).grid(row=2, column=0, columnspan=4,
                                                       sticky="w", pady=(8, 0))
        scmd_frame.columnconfigure(1, weight=1)

        # --- Server install dir ---
        dir_frame = ttk.LabelFrame(content, text="Server Installation", padding=12)
        dir_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(dir_frame, text="Install Directory:", bg=BG, fg=FG).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self._dir_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(dir_frame, text="Browse...",
                   command=self._browse_dir).grid(row=0, column=2)

        tk.Label(dir_frame, text="Game:", bg=BG, fg=FG).grid(
            row=1, column=0, sticky="w", pady=(8, 0))
        self._game_var = tk.StringVar(value="ase")
        game_combo = ttk.Combobox(dir_frame, textvariable=self._game_var,
                                   values=["ase", "asa"], state="readonly", width=8)
        game_combo.grid(row=1, column=1, sticky="w", pady=(8, 0))
        tk.Label(dir_frame, text="  ase = ARK: Survival Evolved  |  asa = ARK: Survival Ascended",
                  bg=BG, fg="#585b70", font=("Segoe UI", 9)).grid(
            row=1, column=2, sticky="w", pady=(8, 0))

        dir_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_row = tk.Frame(dir_frame, bg=BG)
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(12, 0))

        self._install_btn = ttk.Button(btn_row, text="Install / Update Server",
                                        style="Accent.TButton",
                                        command=self._install)
        self._install_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._cancel_btn = ttk.Button(btn_row, text="Cancel",
                                       command=self._cancel, state=tk.DISABLED)
        self._cancel_btn.pack(side=tk.LEFT)

        # Progress
        self._progress = ttk.Progressbar(content, mode="indeterminate")
        self._progress.pack(fill=tk.X, pady=(0, 8))

        # Log output
        log_frame = ttk.LabelFrame(content, text="Output", padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True)

        from ui.widgets.log_viewer import LogViewer
        self._log = LogViewer(log_frame, height=14)
        self._log.pack(fill=tk.BOTH, expand=True)

        ttk.Button(log_frame, text="Clear", command=self._log.clear).pack(
            anchor="e", pady=(4, 0))

    def refresh(self) -> None:
        profile = self._app.get_active_profile()
        self._dir_var.set(profile.get("server_install_dir", ""))
        self._game_var.set(profile.get("game", "ase"))
        scmd = self._app.config.get("steamcmd_path", "")
        self._scmd_var.set(scmd)
        self._update_scmd_status(scmd)

    def _update_scmd_status(self, path: str) -> None:
        if path and os.path.isfile(path):
            self._scmd_status.config(text=f"✓ Found: {path}", fg="#a6e3a1")
        else:
            detected = find_steamcmd()
            if detected:
                self._scmd_status.config(text=f"✓ Auto-detected: {detected}", fg="#a6e3a1")
            else:
                self._scmd_status.config(text="✗ SteamCMD not found. Download it below.",
                                          fg="#f38ba8")

    def _browse_scmd(self) -> None:
        path = filedialog.askopenfilename(
            title="Select steamcmd.exe",
            filetypes=[("Executable", "steamcmd.exe"), ("All files", "*.*")],
        )
        if path:
            self._scmd_var.set(path)
            self._save_scmd(path)

    def _autodetect_scmd(self) -> None:
        found = find_steamcmd()
        if found:
            self._scmd_var.set(found)
            self._save_scmd(found)
        else:
            messagebox.showinfo("Not Found", "SteamCMD not found in common locations.")

    def _save_scmd(self, path: str) -> None:
        self._app.config["steamcmd_path"] = path
        self._app.steamcmd.exe = path
        self._app.save_config()
        self._update_scmd_status(path)

    def _browse_dir(self) -> None:
        d = filedialog.askdirectory(title="Select Server Install Directory")
        if d:
            self._dir_var.set(d)
            self._save_dir(d)

    def _save_dir(self, path: str) -> None:
        profile = self._app.get_active_profile()
        profile["server_install_dir"] = path
        profile["game"] = self._game_var.get()
        self._app.save_config()

    def _download_scmd(self) -> None:
        dest = filedialog.askdirectory(title="Choose folder to install SteamCMD into")
        if not dest:
            return
        self._install_btn.config(state=tk.DISABLED)
        self._progress.start(10)

        import threading
        def _run():
            try:
                def _cb(msg, frac):
                    self.after(0, self._log.append, msg + "\n")

                exe = download_steamcmd(dest, _cb)
                self.after(0, self._scmd_var.set, exe)
                self.after(0, self._save_scmd, exe)
            except Exception as e:
                self.after(0, self._log.append, f"Download failed: {e}\n")
            finally:
                self.after(0, self._progress.stop)
                self.after(0, self._install_btn.config, {"state": tk.NORMAL})

        threading.Thread(target=_run, daemon=True).start()

    def _install(self) -> None:
        scmd = self._scmd_var.get() or find_steamcmd()
        if not scmd or not os.path.isfile(scmd):
            messagebox.showwarning("SteamCMD Missing",
                                    "SteamCMD not found. Download it first.")
            return
        install_dir = self._dir_var.get()
        if not install_dir:
            messagebox.showwarning("No Directory", "Select a server install directory first.")
            return

        game = self._game_var.get()
        self._save_dir(install_dir)
        self._app.steamcmd.exe = scmd
        self._app.config["steamcmd_path"] = scmd
        self._app.save_config()

        self._install_btn.config(state=tk.DISABLED)
        self._cancel_btn.config(state=tk.NORMAL)
        self._progress.start(10)
        self._log.clear()
        self._log.append("[Manager] Starting server install/update...\n")

        self._app.steamcmd.install_or_update_server(
            install_dir, game, self._log_queue, self._on_install_done
        )
        self._poll_log()

    def _poll_log(self) -> None:
        while not self._log_queue.empty():
            try:
                line = self._log_queue.get_nowait()
                self._log.append(line)
            except queue.Empty:
                break
        if self._install_btn["state"] == str(tk.DISABLED):
            self.after(100, self._poll_log)

    def _on_install_done(self, success: bool) -> None:
        self.after(0, self._finish_install, success)

    def _finish_install(self, success: bool) -> None:
        self._progress.stop()
        self._install_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(state=tk.DISABLED)
        msg = "Install/update complete!" if success else "Install/update failed. Check output."
        self._log.append(f"\n[Manager] {msg}\n")

    def _cancel(self) -> None:
        self._app.steamcmd.cancel()
        self._cancel_btn.config(state=tk.DISABLED)
