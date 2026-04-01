"""Backup tab - create, restore, schedule, and manage server backups."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"


class BackupTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._build()
        self.refresh()

    def _build(self) -> None:
        content = tk.Frame(self, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # --- Schedule ---
        sched_frame = ttk.LabelFrame(content, text="Scheduled Backups", padding=10)
        sched_frame.pack(fill=tk.X, pady=(0, 8))

        profile = self._app.get_active_profile()
        backup_cfg = profile.get("backup", {})

        self._sched_enabled_var = tk.BooleanVar(value=backup_cfg.get("enabled", False))
        ttk.Checkbutton(sched_frame, text="Enable automatic backup every",
                         variable=self._sched_enabled_var).grid(
            row=0, column=0, sticky="w")

        self._interval_var = tk.StringVar(value=str(backup_cfg.get("interval_minutes", 60)))
        ttk.Entry(sched_frame, textvariable=self._interval_var, width=6).grid(
            row=0, column=1, padx=4)
        tk.Label(sched_frame, text="minutes", bg=BG, fg=FG).grid(row=0, column=2, sticky="w")

        tk.Label(sched_frame, text="   Keep last", bg=BG, fg=FG).grid(
            row=0, column=3, padx=(16, 4), sticky="w")
        self._keep_var = tk.StringVar(value=str(backup_cfg.get("keep_count", 10)))
        ttk.Entry(sched_frame, textvariable=self._keep_var, width=5).grid(row=0, column=4)
        tk.Label(sched_frame, text="backups", bg=BG, fg=FG).grid(row=0, column=5, sticky="w")

        ttk.Button(sched_frame, text="Apply Schedule",
                   command=self._apply_schedule, style="Accent.TButton").grid(
            row=1, column=0, columnspan=6, sticky="w", pady=(8, 0))

        # --- Backup list ---
        list_frame = ttk.LabelFrame(content, text="Backup List", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols = ("timestamp", "label", "size")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        self._tree.heading("timestamp", text="Date / Time")
        self._tree.heading("label", text="Label")
        self._tree.heading("size", text="Size")
        self._tree.column("timestamp", width=180)
        self._tree.column("label", width=120)
        self._tree.column("size", width=90, anchor="e")

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(fill=tk.BOTH, expand=True)

        # --- Buttons ---
        btn_row = tk.Frame(content, bg=BG)
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="Create Backup Now",
                   style="Accent.TButton", command=self._create_backup).pack(
            side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Restore Selected",
                   command=self._restore_backup).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Delete Selected",
                   style="Danger.TButton", command=self._delete_backup).pack(
            side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Open Folder",
                   command=self._open_folder).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Refresh",
                   command=self.refresh).pack(side=tk.RIGHT)

        # Status line
        self._status_var = tk.StringVar(value="")
        tk.Label(content, textvariable=self._status_var, bg=BG, fg="#a6e3a1",
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))

    def refresh(self) -> None:
        profile = self._app.get_active_profile()
        backup_cfg = profile.get("backup", {})
        self._sched_enabled_var.set(backup_cfg.get("enabled", False))
        self._interval_var.set(str(backup_cfg.get("interval_minutes", 60)))
        self._keep_var.set(str(backup_cfg.get("keep_count", 10)))

        self._tree.delete(*self._tree.get_children())
        for entry in self._app.backup_mgr.list_backups():
            self._tree.insert("", tk.END, iid=str(entry.path),
                               values=(entry.timestamp_str, entry.label, entry.size_str))

    def _apply_schedule(self) -> None:
        profile = self._app.get_active_profile()
        try:
            interval = int(self._interval_var.get())
            keep = int(self._keep_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Interval and keep count must be integers.")
            return

        profile.setdefault("backup", {}).update({
            "enabled": self._sched_enabled_var.get(),
            "interval_minutes": interval,
            "keep_count": keep,
        })
        self._app.save_config()

        self._app.backup_mgr.stop_schedule()
        if self._sched_enabled_var.get() and profile.get("server_install_dir"):
            self._app.backup_mgr.schedule_backup(
                profile["server_install_dir"], interval, keep,
                on_complete=lambda msg: self._status_var.set(msg),
            )
            self._status_var.set(f"Auto-backup every {interval} min, keep {keep}.")
        else:
            self._status_var.set("Auto-backup disabled.")

    def _create_backup(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            messagebox.showwarning("No Server", "Set server install directory first.")
            return
        self._status_var.set("Creating backup...")

        import threading
        def _run():
            result = self._app.backup_mgr.create_backup(
                server_dir, label="manual",
                progress_cb=lambda m: self.after(0, self._status_var.set, m),
            )
            self.after(0, self.refresh)
            if not result:
                self.after(0, messagebox.showerror, "Backup Failed",
                            "Could not create backup. Check server install dir.")

        threading.Thread(target=_run, daemon=True).start()

    def _restore_backup(self) -> None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a backup to restore.")
            return
        backup_path = sel[0]
        if not messagebox.askyesno("Restore Backup",
                                    f"Restore backup:\n{backup_path}\n\n"
                                    "This will overwrite the server's Saved directory!"):
            return
        if self._app.server.status in ("running", "starting"):
            messagebox.showwarning("Server Running",
                                    "Stop the server before restoring a backup.")
            return
        profile = self._app.get_active_profile()
        from pathlib import Path
        import threading

        def _run():
            ok = self._app.backup_mgr.restore_backup(
                Path(backup_path), profile.get("server_install_dir", ""),
                progress_cb=lambda m: self.after(0, self._status_var.set, m),
            )
            if not ok:
                self.after(0, messagebox.showerror, "Restore Failed",
                            "Restore encountered an error. Check status line.")

        threading.Thread(target=_run, daemon=True).start()

    def _delete_backup(self) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        backup_path = sel[0]
        if not messagebox.askyesno("Delete Backup",
                                    f"Permanently delete:\n{backup_path}?"):
            return
        from pathlib import Path
        self._app.backup_mgr.delete_backup(Path(backup_path))
        self.refresh()

    def _open_folder(self) -> None:
        folder = self._app.backup_mgr.backups_dir
        os.makedirs(folder, exist_ok=True)
        subprocess.Popen(["explorer", folder])
