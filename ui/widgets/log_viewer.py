"""Scrollable log viewer with color-coded lines."""
import tkinter as tk
from tkinter import scrolledtext


class LogViewer(scrolledtext.ScrolledText):
    TAGS = {
        "error":   {"foreground": "#f38ba8"},
        "warning": {"foreground": "#f9e2af"},
        "success": {"foreground": "#a6e3a1"},
        "info":    {"foreground": "#89dceb"},
        "manager": {"foreground": "#cba6f7"},
        "default": {"foreground": "#cdd6f4"},
    }

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", "#181825")
        kwargs.setdefault("fg", "#cdd6f4")
        kwargs.setdefault("font", ("Consolas", 9))
        kwargs.setdefault("wrap", tk.WORD)
        kwargs.setdefault("state", tk.DISABLED)
        super().__init__(parent, **kwargs)
        for tag, cfg in self.TAGS.items():
            self.tag_config(tag, **cfg)
        self._autoscroll = True

    def append(self, line: str, autoscroll: bool = True) -> None:
        tag = self._classify(line)
        self.config(state=tk.NORMAL)
        self.insert(tk.END, line, tag)
        if self._autoscroll and autoscroll:
            self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clear(self) -> None:
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)

    def set_autoscroll(self, value: bool) -> None:
        self._autoscroll = value

    def search_highlight(self, term: str) -> int:
        self.tag_remove("search", "1.0", tk.END)
        if not term:
            return 0
        count = 0
        start = "1.0"
        while True:
            pos = self.search(term, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(term)}c"
            self.tag_add("search", pos, end)
            start = end
            count += 1
        self.tag_config("search", background="#f9e2af", foreground="#1e1e2e")
        return count

    @staticmethod
    def _classify(line: str) -> str:
        u = line.upper()
        if "[MANAGER]" in u:
            return "manager"
        if "[STEAMCMD]" in u or "[MODS]" in u:
            return "manager"
        if any(w in u for w in ("ERROR", "FATAL", "EXCEPTION", "CRASH")):
            return "error"
        if any(w in u for w in ("WARNING", "WARN")):
            return "warning"
        if any(w in u for w in ("JOIN", "JOINED", "CONNECTED", "LOGIN")):
            return "success"
        if any(w in u for w in ("INFO", "SERVER IS LISTENING")):
            return "info"
        return "default"
