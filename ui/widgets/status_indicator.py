"""Colored circle + label status indicator widget."""
import tkinter as tk
from tkinter import ttk

_COLORS = {
    "running":  "#a6e3a1",
    "starting": "#f9e2af",
    "stopped":  "#f38ba8",
    "crashed":  "#fab387",
    "connected":    "#a6e3a1",
    "disconnected": "#f38ba8",
}


class StatusIndicator(tk.Frame):
    def __init__(self, parent, status: str = "stopped", **kwargs):
        bg = kwargs.pop("bg", None) or kwargs.pop("background", "#1e1e2e")
        super().__init__(parent, bg=bg, **kwargs)
        self._canvas = tk.Canvas(self, width=14, height=14, bg=bg,
                                  highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, padx=(0, 4))
        self._dot = self._canvas.create_oval(2, 2, 12, 12, fill="#888", outline="")
        self._label = tk.Label(self, text=status.capitalize(),
                                bg=bg, fg="#cdd6f4",
                                font=("Segoe UI", 10, "bold"))
        self._label.pack(side=tk.LEFT)
        self.set_status(status)

    def set_status(self, status: str) -> None:
        color = _COLORS.get(status.lower(), "#888888")
        self._canvas.itemconfig(self._dot, fill=color)
        self._label.config(text=status.capitalize())
