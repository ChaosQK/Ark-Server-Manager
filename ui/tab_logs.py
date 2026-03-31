"""Logs tab — live server output with search and file browser."""
from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk
import subprocess

from ui.widgets.log_viewer import LogViewer

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"


class LogsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._build()
        self._start_poll()

    def _build(self) -> None:
        # Toolbar
        toolbar = tk.Frame(self, bg="#181825")
        toolbar.pack(fill=tk.X)

        self._autoscroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-scroll",
                         variable=self._autoscroll_var,
                         command=self._toggle_autoscroll).pack(side=tk.LEFT, padx=8, pady=6)

        ttk.Button(toolbar, text="Clear",
                   command=self._clear).pack(side=tk.LEFT, pady=6)
        ttk.Button(toolbar, text="Open Log Folder",
                   command=self._open_folder).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Label(toolbar, text="Search:", bg="#181825", fg=FG).pack(
            side=tk.LEFT, padx=(8, 4), pady=6)
        self._search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self._search_var, width=20)
        search_entry.pack(side=tk.LEFT, pady=6)
        self._search_var.trace_add("write", lambda *_: self._do_search())

        self._match_var = tk.StringVar(value="")
        tk.Label(toolbar, textvariable=self._match_var, bg="#181825",
                  fg="#585b70", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

        # Log file selector
        tk.Label(toolbar, text="Log file:", bg="#181825", fg=FG).pack(
            side=tk.RIGHT, padx=(0, 4), pady=6)
        self._file_var = tk.StringVar(value="Live")
        self._file_combo = ttk.Combobox(toolbar, textvariable=self._file_var,
                                         values=["Live"], state="readonly", width=22)
        self._file_combo.pack(side=tk.RIGHT, padx=(0, 8), pady=6)
        self._file_combo.bind("<<ComboboxSelected>>", self._on_file_select)

        tk.Frame(self, bg="#313244", height=1).pack(fill=tk.X)

        self._log_view = LogViewer(self, height=30)
        self._log_view.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _start_poll(self) -> None:
        self._poll()
        self._refresh_file_list_periodically()

    def _poll(self) -> None:
        q = self._app.server.log_queue
        count = 0
        while not q.empty() and count < 200:
            try:
                line = q.get_nowait()
                if self._file_var.get() == "Live":
                    self._log_view.append(line, autoscroll=self._autoscroll_var.get())
                count += 1
            except Exception:
                break
        self.after(150, self._poll)

    def _refresh_file_list_periodically(self) -> None:
        self._refresh_file_list()
        self.after(10000, self._refresh_file_list_periodically)

    def _refresh_file_list(self) -> None:
        logs_dir = os.path.join(self._app._manager_dir, "logs")
        files = []
        if os.path.isdir(logs_dir):
            files = sorted(
                [f for f in os.listdir(logs_dir) if f.endswith(".log")],
                reverse=True,
            )
        values = ["Live"] + files
        self._file_combo["values"] = values

    def _on_file_select(self, event=None) -> None:
        chosen = self._file_var.get()
        if chosen == "Live":
            return
        log_path = os.path.join(self._app._manager_dir, "logs", chosen)
        if not os.path.isfile(log_path):
            return
        self._log_view.clear()
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    self._log_view.append(line, autoscroll=False)
            self._log_view.see(tk.END)
        except OSError:
            pass

    def _toggle_autoscroll(self) -> None:
        self._log_view.set_autoscroll(self._autoscroll_var.get())

    def _clear(self) -> None:
        self._log_view.clear()

    def _do_search(self) -> None:
        term = self._search_var.get()
        count = self._log_view.search_highlight(term)
        if term:
            self._match_var.set(f"{count} match{'es' if count != 1 else ''}")
        else:
            self._match_var.set("")

    def _open_folder(self) -> None:
        logs_dir = os.path.join(self._app._manager_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        subprocess.Popen(["explorer", logs_dir])
