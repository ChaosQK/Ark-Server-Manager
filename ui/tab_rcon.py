"""RCON console tab."""
from __future__ import annotations
import collections
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

from core.rcon_client import RconClient, RconError
from ui.widgets.status_indicator import StatusIndicator

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"

_QUICK_CMDS = [
    ("SaveWorld",         "saveworld"),
    ("List Players",      "listplayers"),
    ("Broadcast",         "broadcast Hello!"),
    ("Destroy Wild Dinos","destroywilddinos"),
    ("Do Exit",           "doexit"),
    ("Whitelist",         "AllowPlayerToJoinNoCheck <steamid>"),
    ("Kick Player",       "KickPlayer <steamid>"),
    ("Ban Player",        "BanPlayer <steamid>"),
    ("Set Time of Day",   "SetTimeOfDay 12:00"),
    ("Give Item",         "GiveItemNum <itemid> <qty> <quality> <bp>"),
]


class RconTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._client = RconClient()
        self._history: collections.deque = collections.deque(maxlen=100)
        self._history_idx = -1
        self._build()
        self._load_connection_settings()

    def _build(self) -> None:
        # Connection bar
        conn_frame = ttk.LabelFrame(self, text="Connection", padding=8)
        conn_frame.pack(fill=tk.X, padx=16, pady=(12, 0))

        tk.Label(conn_frame, text="Host:", bg=BG, fg=FG).grid(row=0, column=0, sticky="w", padx=(0,4))
        self._host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self._host_var, width=16).grid(row=0, column=1, padx=(0,8))

        tk.Label(conn_frame, text="Port:", bg=BG, fg=FG).grid(row=0, column=2, sticky="w", padx=(0,4))
        self._port_var = tk.StringVar(value="27020")
        ttk.Entry(conn_frame, textvariable=self._port_var, width=7).grid(row=0, column=3, padx=(0,8))

        tk.Label(conn_frame, text="Password:", bg=BG, fg=FG).grid(row=0, column=4, sticky="w", padx=(0,4))
        self._pass_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self._pass_var, show="*", width=16).grid(
            row=0, column=5, padx=(0,8))

        self._conn_btn = ttk.Button(conn_frame, text="Connect",
                                     style="Accent.TButton", command=self._toggle_connect)
        self._conn_btn.grid(row=0, column=6, padx=(0,8))

        self._indicator = StatusIndicator(conn_frame, "disconnected", bg=BG)
        self._indicator.grid(row=0, column=7)

        ttk.Button(conn_frame, text="Save",
                   command=self._save_settings).grid(row=0, column=8, padx=(8, 0))

        tk.Frame(self, bg="#313244", height=1).pack(fill=tk.X, pady=(8, 0))

        # Main area: console + quick commands
        main = tk.Frame(self, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Console output
        self._console = scrolledtext.ScrolledText(
            main, height=22,
            bg="#181825", fg=FG,
            insertbackground=FG,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._console.pack(fill=tk.BOTH, expand=True)
        self._console.tag_config("cmd", foreground=ACCENT)
        self._console.tag_config("resp", foreground="#cdd6f4")
        self._console.tag_config("err", foreground="#f38ba8")
        self._console.tag_config("info", foreground="#a6e3a1")

        # Quick commands
        quick_frame = ttk.LabelFrame(main, text="Quick Commands", padding=6)
        quick_frame.pack(fill=tk.X, pady=(8, 0))

        for i, (label, cmd) in enumerate(_QUICK_CMDS):
            btn = ttk.Button(quick_frame, text=label,
                              command=lambda c=cmd: self._set_input(c))
            btn.grid(row=i // 5, column=i % 5, padx=3, pady=2, sticky="ew")
        for c in range(5):
            quick_frame.columnconfigure(c, weight=1)

        # Input row
        input_row = tk.Frame(self, bg=BG)
        input_row.pack(fill=tk.X, padx=16, pady=(0, 12))

        tk.Label(input_row, text=">", bg=BG, fg=ACCENT,
                  font=("Consolas", 11, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self._input_var = tk.StringVar()
        self._input_entry = ttk.Entry(input_row, textvariable=self._input_var, font=("Consolas", 10))
        self._input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._input_entry.bind("<Return>", lambda _: self._send())
        self._input_entry.bind("<Up>", self._history_up)
        self._input_entry.bind("<Down>", self._history_down)

        ttk.Button(input_row, text="Send",
                   style="Accent.TButton", command=self._send).pack(side=tk.LEFT, padx=(8, 0))

    def _load_connection_settings(self) -> None:
        profile = self._app.get_active_profile()
        rcon = profile.get("rcon", {})
        self._host_var.set(rcon.get("host", "localhost"))
        self._port_var.set(str(rcon.get("port", 27020)))
        self._pass_var.set(rcon.get("password", ""))

    def refresh(self) -> None:
        self._load_connection_settings()

    def _toggle_connect(self) -> None:
        if self._client.connected:
            self._client.disconnect()
            self._indicator.set_status("disconnected")
            self._conn_btn.config(text="Connect")
            self._write_console("Disconnected.\n", "info")
        else:
            self._connect()

    def _connect(self) -> None:
        host = self._host_var.get()
        port = self._port_var.get()
        password = self._pass_var.get()
        self._write_console(f"Connecting to {host}:{port}...\n", "info")

        def _run():
            try:
                self._client.connect(host, int(port), password)
                self.after(0, self._on_connected)
            except RconError as e:
                self.after(0, self._write_console, f"Connection failed: {e}\n", "err")
                self.after(0, self._indicator.set_status, "disconnected")

        threading.Thread(target=_run, daemon=True).start()

    def _on_connected(self) -> None:
        self._indicator.set_status("connected")
        self._conn_btn.config(text="Disconnect")
        self._write_console("Connected!\n", "info")

    def _send(self) -> None:
        cmd = self._input_var.get().strip()
        if not cmd:
            return
        if not self._client.connected:
            self._write_console("Not connected. Click Connect first.\n", "err")
            return
        self._history.append(cmd)
        self._history_idx = -1
        self._input_var.set("")
        self._write_console(f"> {cmd}\n", "cmd")

        def _run():
            try:
                resp = self._client.send_command(cmd)
                self.after(0, self._write_console, (resp or "(no response)") + "\n", "resp")
            except RconError as e:
                self.after(0, self._write_console, f"Error: {e}\n", "err")
                self.after(0, self._indicator.set_status, "disconnected")
                self._client.connected = False

        threading.Thread(target=_run, daemon=True).start()

    def _set_input(self, cmd: str) -> None:
        self._input_var.set(cmd)
        self._input_entry.focus_set()
        self._input_entry.icursor(tk.END)

    def _write_console(self, text: str, tag: str = "resp") -> None:
        self._console.config(state=tk.NORMAL)
        self._console.insert(tk.END, text, tag)
        self._console.see(tk.END)
        self._console.config(state=tk.DISABLED)

    def _history_up(self, event=None) -> str:
        if not self._history:
            return "break"
        if self._history_idx < len(self._history) - 1:
            self._history_idx += 1
        idx = len(self._history) - 1 - self._history_idx
        self._input_var.set(self._history[idx])
        self._input_entry.icursor(tk.END)
        return "break"

    def _history_down(self, event=None) -> str:
        if self._history_idx <= 0:
            self._history_idx = -1
            self._input_var.set("")
            return "break"
        self._history_idx -= 1
        idx = len(self._history) - 1 - self._history_idx
        self._input_var.set(self._history[idx])
        self._input_entry.icursor(tk.END)
        return "break"

    def _save_settings(self) -> None:
        profile = self._app.get_active_profile()
        profile.setdefault("rcon", {}).update({
            "host": self._host_var.get(),
            "port": int(self._port_var.get() or 27020),
            "password": self._pass_var.get(),
        })
        self._app.save_config()
        self._write_console("RCON settings saved.\n", "info")
