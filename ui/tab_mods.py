"""Mod manager tab - install/remove/update Workshop mods."""
from __future__ import annotations
import os
import queue
import tkinter as tk
from tkinter import ttk, messagebox

from core.mod_manager import get_mod_info

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"


class ModsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._log_queue: queue.Queue = queue.Queue()
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Top: mod list
        list_frame = ttk.LabelFrame(self, text="Installed Mods", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(12, 0))

        cols = ("enabled", "id", "name", "status")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        self._tree.heading("enabled", text="On")
        self._tree.heading("id", text="Mod ID")
        self._tree.heading("name", text="Name")
        self._tree.heading("status", text="Status")
        self._tree.column("enabled", width=40, anchor="center")
        self._tree.column("id", width=100)
        self._tree.column("name", width=300)
        self._tree.column("status", width=120)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(list_frame, bg=BG)
        btn_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_row, text="Toggle Enable",
                   command=self._toggle_mod).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Remove Selected",
                   style="Danger.TButton", command=self._remove_mod).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Update All",
                   command=self._update_all).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Refresh",
                   command=self.refresh).pack(side=tk.RIGHT)

        # Add mod section
        add_frame = ttk.LabelFrame(self, text="Add Mod from Workshop", padding=8)
        add_frame.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(add_frame, text="Workshop ID:", bg=BG, fg=FG).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._mod_id_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self._mod_id_var, width=16).grid(
            row=0, column=1, sticky="w")
        ttk.Button(add_frame, text="Fetch Info",
                   command=self._fetch_info).grid(row=0, column=2, padx=(8, 0))

        self._mod_info_var = tk.StringVar(value="")
        tk.Label(add_frame, textvariable=self._mod_info_var,
                  bg=BG, fg="#a6e3a1", font=("Segoe UI", 9)).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        ttk.Button(add_frame, text="Install Mod",
                   style="Accent.TButton", command=self._install_mod).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        add_frame.columnconfigure(1, weight=1)

        # Log
        log_frame = ttk.LabelFrame(self, text="Output", padding=4)
        log_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        from ui.widgets.log_viewer import LogViewer
        self._log = LogViewer(log_frame, height=6)
        self._log.pack(fill=tk.X)

    def refresh(self) -> None:
        profile = self._app.get_active_profile()
        mods = profile.get("mods", [])
        server_dir = profile.get("server_install_dir", "")

        self._tree.delete(*self._tree.get_children())
        for mod in mods:
            mod_id = str(mod.get("id", ""))
            name = mod.get("name", f"Mod {mod_id}")
            enabled = mod.get("enabled", True)
            installed = (self._app.mod_mgr.is_mod_installed(mod_id, server_dir)
                          if server_dir else False)
            status = "Installed" if installed else "Not on disk"
            self._tree.insert("", tk.END, iid=mod_id,
                               values=("✓" if enabled else "✗", mod_id, name, status))

    def _selected_mod_id(self) -> str | None:
        sel = self._tree.selection()
        return sel[0] if sel else None

    def _toggle_mod(self) -> None:
        mod_id = self._selected_mod_id()
        if not mod_id:
            return
        profile = self._app.get_active_profile()
        mods = profile.get("mods", [])
        for m in mods:
            if str(m.get("id")) == mod_id:
                m["enabled"] = not m.get("enabled", True)
                break
        self._app.save_config()
        self.refresh()

    def _remove_mod(self) -> None:
        mod_id = self._selected_mod_id()
        if not mod_id:
            return
        if not messagebox.askyesno("Remove Mod", f"Remove mod {mod_id} from profile?\n"
                                    "(Files on disk are NOT deleted.)"):
            return
        profile = self._app.get_active_profile()
        profile["mods"] = [m for m in profile.get("mods", [])
                            if str(m.get("id")) != mod_id]
        self._app.save_config()
        self.refresh()

    def _fetch_info(self) -> None:
        mod_id = self._mod_id_var.get().strip()
        if not mod_id:
            return
        self._mod_info_var.set("Fetching...")
        import threading
        def _run():
            info = get_mod_info(mod_id)
            self.after(0, self._mod_info_var.set,
                        f"  {info['title']}  (updated: {info.get('time_updated', '?')})")
        threading.Thread(target=_run, daemon=True).start()

    def _install_mod(self) -> None:
        mod_id = self._mod_id_var.get().strip()
        if not mod_id:
            messagebox.showwarning("No Mod ID", "Enter a Workshop mod ID first.")
            return
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        steamcmd_dir = os.path.dirname(self._app.config.get("steamcmd_path", ""))
        if not steamcmd_dir or not self._app.steamcmd.exe:
            messagebox.showwarning("SteamCMD", "Configure SteamCMD in the Install tab first.")
            return
        if not server_dir:
            messagebox.showwarning("No Server", "Set server install directory first.")
            return

        self._log.clear()
        self._log.append(f"[Manager] Installing mod {mod_id}...\n")

        def _done(success: bool):
            if success:
                # Add to profile mods list if not already there
                mods = profile.setdefault("mods", [])
                ids = [str(m.get("id")) for m in mods]
                if mod_id not in ids:
                    info = get_mod_info(mod_id)
                    mods.append({"id": mod_id, "name": info["title"], "enabled": True})
                    self._app.save_config()
                self.after(0, self.refresh)
            self.after(0, self._log.append,
                        f"[Manager] Mod {mod_id} {'installed' if success else 'FAILED'}.\n")

        self._app.mod_mgr.install_mod(
            mod_id, steamcmd_dir, server_dir, self._log_queue, _done
        )
        self._poll_log()

    def _update_all(self) -> None:
        profile = self._app.get_active_profile()
        mods = profile.get("mods", [])
        enabled_mods = [m for m in mods if m.get("enabled", True)]
        if not enabled_mods:
            messagebox.showinfo("No Mods", "No enabled mods to update.")
            return
        server_dir = profile.get("server_install_dir", "")
        steamcmd_dir = os.path.dirname(self._app.config.get("steamcmd_path", ""))
        self._log.clear()
        self._log.append(f"[Manager] Updating {len(enabled_mods)} mods...\n")

        def _install_next(idx: int):
            if idx >= len(enabled_mods):
                self.after(0, self._log.append, "[Manager] All mods updated.\n")
                self.after(0, self.refresh)
                return
            mod = enabled_mods[idx]
            mod_id = str(mod.get("id"))
            self._log_queue.put(f"[Manager] Updating mod {mod_id} ({idx+1}/{len(enabled_mods)})...\n")

            def _done(success):
                _install_next(idx + 1)

            self._app.mod_mgr.install_mod(
                mod_id, steamcmd_dir, server_dir, self._log_queue, _done
            )

        _install_next(0)
        self._poll_log()

    def _poll_log(self) -> None:
        while not self._log_queue.empty():
            try:
                self._log.append(self._log_queue.get_nowait())
            except queue.Empty:
                break
        self.after(150, self._poll_log)
