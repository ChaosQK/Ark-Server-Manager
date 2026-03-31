"""Collapsible (accordion) frame widget."""
import tkinter as tk
from tkinter import ttk


class CollapsibleFrame(tk.Frame):
    def __init__(self, parent, title: str = "", collapsed: bool = False, **kwargs):
        bg = kwargs.pop("bg", "#1e1e2e")
        super().__init__(parent, bg=bg, **kwargs)

        self._collapsed = collapsed
        self._title = title

        # Header button
        self._toggle_btn = tk.Button(
            self, text=self._header_text(),
            anchor="w", relief=tk.FLAT,
            bg="#313244", fg="#cdd6f4",
            activebackground="#45475a", activeforeground="#cdd6f4",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            command=self.toggle,
        )
        self._toggle_btn.pack(fill=tk.X, pady=(2, 0))

        # Inner content frame
        self.content = tk.Frame(self, bg=bg)
        if not collapsed:
            self.content.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

    def _header_text(self) -> str:
        arrow = "▶" if self._collapsed else "▼"
        return f"  {arrow}  {self._title}"

    def toggle(self) -> None:
        self._collapsed = not self._collapsed
        self._toggle_btn.config(text=self._header_text())
        if self._collapsed:
            self.content.pack_forget()
        else:
            self.content.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

    def collapse(self) -> None:
        if not self._collapsed:
            self.toggle()

    def expand(self) -> None:
        if self._collapsed:
            self.toggle()
