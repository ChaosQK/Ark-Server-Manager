"""
Game.ini editor — easy structured forms + raw editor.
Covers difficulty, day/night, per-level stats, engram points, and raw editing.
"""
from __future__ import annotations
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from core.ini_parser import ArkIniFile
from ui.widgets.collapsible_frame import CollapsibleFrame

BG    = "#1e1e2e"
BG2   = "#181825"
BG3   = "#313244"
FG    = "#cdd6f4"
FG2   = "#a6adc8"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"

# The main section in Game.ini
_SECTION = "/script/shootergame.shootergamemode"

# Stat attribute indices (for PerLevelStatsMultiplier_Player / _DinoTamed / _DinoWild)
_STAT_NAMES = [
    (0, "Health"),
    (1, "Stamina"),
    (2, "Oxygen"),
    (3, "Food"),
    (4, "Weight"),
    (5, "Melee Damage"),
    (6, "Movement Speed"),
    (7, "Fortitude"),
    (8, "Crafting Speed"),
]


class SettingsGameTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._build()
        self.refresh()

    def _game_ini_path(self) -> str:
        name = self._app.config.get("active_profile", "default")
        return os.path.join(self._app._manager_dir, "profiles", name, "Game.ini")

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # ── Top toolbar ─────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=BG2)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="💾  Save to Profile",
                   style="Accent.TButton", command=self._save).pack(
            side=tk.LEFT, padx=8, pady=6)
        ttk.Button(toolbar, text="⟳  Sync to Server",
                   command=self._sync_to_server).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        ttk.Button(toolbar, text="↓  Load from Server",
                   command=self._load_from_server).pack(side=tk.LEFT, pady=6)

        tk.Frame(self, bg=BG3, height=1).pack(fill=tk.X)

        # ── Inner notebook ───────────────────────────────────────────
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True)

        self._build_tab_difficulty()
        self._build_tab_day_night()
        self._build_tab_player_stats()
        self._build_tab_dino_stats()
        self._build_tab_engrams()
        self._build_tab_raw()

    # ------------------------------------------------------------------
    # Tab: Difficulty
    # ------------------------------------------------------------------

    def _build_tab_difficulty(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Difficulty  ")

        canvas, inner = self._scrollable(frame)

        self._diff_offset  = self._row(inner, 0,
            "Difficulty Offset", "0.2",
            "Controls max wild dino level: 0.2 = up to L60, 1.0 = up to L30\n"
            "Use OverrideOfficialDifficulty instead for precise control")

        self._override_diff = self._row(inner, 1,
            "Override Official Difficulty", "5.0",
            "Max wild dino level = this value × 30\n"
            "5.0 → max L150  |  6.0 → max L180  |  8.0 → max L240",
            highlight=True)

        self._max_tamed_dinos = self._row(inner, 2,
            "Max Tamed Dinos (server-wide)", "5000",
            "Total tamed creatures allowed on the entire server at once")

        self._max_personal_tamed = self._row(inner, 3,
            "Max Personal Tamed Dinos", "500",
            "Maximum tamed creatures per tribe")

        self._dino_count_multi = self._row(inner, 4,
            "Wild Dino Count Multiplier", "1.0",
            "Scales the number of wild creatures spawned on the map\n"
            "2.0 = twice as many wild dinos, 0.5 = half")

        # Note box
        note = tk.Label(inner,
            text="ℹ  After changing difficulty, use 'destroywilddinos' via RCON\n"
                 "   to respawn dinos at the new level cap.",
            bg=BG3, fg=YELLOW,
            font=("Segoe UI", 9), justify="left",
            padx=12, pady=6)
        note.grid(row=5, column=0, columnspan=3, sticky="ew", padx=12, pady=(12, 4))
        inner.columnconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # Tab: Day / Night
    # ------------------------------------------------------------------

    def _build_tab_day_night(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Day / Night  ")

        canvas, inner = self._scrollable(frame)

        self._day_cycle  = self._row(inner, 0,
            "Day Cycle Speed", "1.0",
            "Overall speed of the entire day/night cycle\n"
            "2.0 = days pass twice as fast")
        self._daytime    = self._row(inner, 1,
            "Daytime Speed", "1.0",
            "Relative speed of the daytime portion only\n"
            "Higher = shorter days")
        self._nighttime  = self._row(inner, 2,
            "Nighttime Speed", "1.0",
            "Relative speed of the nighttime portion only\n"
            "Higher = shorter nights")

        # Visual guide
        guide = tk.Label(inner,
            text="Example — Long days, short nights:\n"
                 "  Day Cycle Speed = 1.0\n"
                 "  Daytime Speed   = 0.5  ← days are twice as long\n"
                 "  Nighttime Speed = 2.0  ← nights are twice as short",
            bg=BG3, fg=FG2,
            font=("Consolas", 9), justify="left",
            padx=12, pady=8)
        guide.grid(row=3, column=0, columnspan=3, sticky="ew",
                    padx=12, pady=(16, 4))
        inner.columnconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # Tab: Player Per-Level Stats
    # ------------------------------------------------------------------

    def _build_tab_player_stats(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Player Stats  ")

        canvas, inner = self._scrollable(frame)

        tk.Label(inner,
                  text="Multiplier applied to each stat point when a player levels up.\n"
                       "1.0 = default  |  2.0 = double per level-up gain",
                  bg=BG3, fg=FG2, font=("Segoe UI", 9), padx=12, pady=6,
                  justify="left").grid(row=0, column=0, columnspan=3,
                                        sticky="ew", padx=12, pady=(8, 4))

        # Headers
        for col, text in enumerate(("Stat", "Per Level Multiplier", "Base Stat Multiplier")):
            tk.Label(inner, text=text, bg=BG3, fg=ACCENT,
                      font=("Segoe UI", 9, "bold"), padx=8, anchor="w").grid(
                row=1, column=col, sticky="ew", padx=(12 if col == 0 else 4, 4),
                pady=(4, 2))

        self._player_per_level: dict[int, tk.StringVar] = {}
        self._player_base:      dict[int, tk.StringVar] = {}

        for row_i, (idx, name) in enumerate(_STAT_NAMES, start=2):
            bg_r = BG if row_i % 2 == 0 else BG2
            tk.Label(inner, text=name, bg=bg_r, fg=FG,
                      font=("Segoe UI", 10), padx=12, anchor="w").grid(
                row=row_i, column=0, sticky="ew", padx=12, pady=2)

            v_level = tk.StringVar(value="1.0")
            ttk.Entry(inner, textvariable=v_level, width=12).grid(
                row=row_i, column=1, sticky="w", padx=8, pady=2)
            self._player_per_level[idx] = v_level

            v_base = tk.StringVar(value="1.0")
            ttk.Entry(inner, textvariable=v_base, width=12).grid(
                row=row_i, column=2, sticky="w", padx=8, pady=2)
            self._player_base[idx] = v_base

        inner.columnconfigure(0, minsize=180)
        inner.columnconfigure(1, minsize=160)
        inner.columnconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # Tab: Dino Per-Level Stats
    # ------------------------------------------------------------------

    def _build_tab_dino_stats(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Dino Stats  ")

        canvas, inner = self._scrollable(frame)

        tk.Label(inner,
                  text="Per-level stat multipliers for tamed dinos.\n"
                       "Add = the raw stat gained per level-up point.\n"
                       "Affinity = the imprint bonus multiplier (usually 1.0).",
                  bg=BG3, fg=FG2, font=("Segoe UI", 9), padx=12, pady=6,
                  justify="left").grid(row=0, column=0, columnspan=3,
                                        sticky="ew", padx=12, pady=(8, 4))

        for col, text in enumerate(("Stat", "Tamed Add Per Level", "Tamed Affinity")):
            tk.Label(inner, text=text, bg=BG3, fg=ACCENT,
                      font=("Segoe UI", 9, "bold"), padx=8, anchor="w").grid(
                row=1, column=col, sticky="ew",
                padx=(12 if col == 0 else 4, 4), pady=(4, 2))

        self._dino_add:      dict[int, tk.StringVar] = {}
        self._dino_affinity: dict[int, tk.StringVar] = {}

        for row_i, (idx, name) in enumerate(_STAT_NAMES, start=2):
            bg_r = BG if row_i % 2 == 0 else BG2
            tk.Label(inner, text=name, bg=bg_r, fg=FG,
                      font=("Segoe UI", 10), padx=12, anchor="w").grid(
                row=row_i, column=0, sticky="ew", padx=12, pady=2)

            v_add = tk.StringVar(value="1.0")
            ttk.Entry(inner, textvariable=v_add, width=12).grid(
                row=row_i, column=1, sticky="w", padx=8, pady=2)
            self._dino_add[idx] = v_add

            v_aff = tk.StringVar(value="1.0")
            ttk.Entry(inner, textvariable=v_aff, width=12).grid(
                row=row_i, column=2, sticky="w", padx=8, pady=2)
            self._dino_affinity[idx] = v_aff

        inner.columnconfigure(0, minsize=180)
        inner.columnconfigure(1, minsize=160)
        inner.columnconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # Tab: Engram Points
    # ------------------------------------------------------------------

    def _build_tab_engrams(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Engram Points  ")

        tk.Label(frame,
                  text="Engram points earned per level-up (one value per level).\n"
                       "The number of rows = the number of levels your server supports.\n"
                       "Leave blank to use ARK defaults.",
                  bg=BG3, fg=FG2, font=("Segoe UI", 9), padx=12, pady=6,
                  justify="left").pack(fill=tk.X, padx=8, pady=(8, 0))

        # Quick fill bar
        qf = tk.Frame(frame, bg=BG)
        qf.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(qf, text="Quick fill — all levels:", bg=BG, fg=FG,
                  font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._engram_quick_var = tk.StringVar(value="30")
        ttk.Entry(qf, textvariable=self._engram_quick_var, width=8).pack(
            side=tk.LEFT, padx=6)
        tk.Label(qf, text="pts/level", bg=BG, fg=FG2,
                  font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Button(qf, text="Apply",
                   command=self._fill_engrams).pack(side=tk.LEFT, padx=8)
        ttk.Button(qf, text="Clear (use defaults)",
                   command=self._clear_engrams).pack(side=tk.LEFT)

        # Scrollable per-level grid
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                     lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"),
                         add=True)

        # 6 columns of (Level, Points)
        COLS = 6
        self._engram_vars: list[tk.StringVar] = []
        MAX_LEVELS = 180

        for i in range(MAX_LEVELS):
            col_group = i % COLS
            row_group = i // COLS
            base_col = col_group * 3  # label | entry | spacer

            bg_r = BG if (i // COLS) % 2 == 0 else BG2
            tk.Label(inner, text=f"L{i+1}", bg=bg_r, fg=FG2,
                      font=("Segoe UI", 9), width=4, anchor="e").grid(
                row=row_group, column=base_col, sticky="e", padx=(8, 2), pady=1)
            v = tk.StringVar(value="")
            ttk.Entry(inner, textvariable=v, width=6).grid(
                row=row_group, column=base_col+1, sticky="w", padx=(0, 8), pady=1)
            self._engram_vars.append(v)

    # ------------------------------------------------------------------
    # Tab: Raw Editor
    # ------------------------------------------------------------------

    def _build_tab_raw(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Raw Editor  ")

        info = tk.Label(frame,
            text="Direct text editing of Game.ini.\n"
                 "Click 'Pull from Forms' to copy all structured settings here, "
                 "or edit freely and use Save/Sync.",
            bg=BG3, fg=FG2, font=("Segoe UI", 9), padx=12, pady=6,
            justify="left")
        info.pack(fill=tk.X)

        btn_row = tk.Frame(frame, bg=BG)
        btn_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(btn_row, text="Pull from Forms → Raw",
                   command=self._forms_to_raw).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Push Raw → Forms",
                   command=self._raw_to_forms).pack(side=tk.LEFT)

        self._raw = scrolledtext.ScrolledText(
            frame, bg=BG2, fg=FG,
            insertbackground=FG,
            font=("Consolas", 9),
            wrap=tk.NONE,
        )
        self._raw.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _scrollable(self, parent: tk.Frame):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                     lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"),
                         add=True)
        return canvas, inner

    def _row(self, parent, row: int, label: str, default: str,
              hint: str, highlight: bool = False) -> tk.StringVar:
        bg_r = BG if row % 2 == 0 else BG2
        fg_l = ACCENT if highlight else FG
        font_l = ("Segoe UI", 10, "bold") if highlight else ("Segoe UI", 10)

        tk.Label(parent, text=label, bg=bg_r, fg=fg_l,
                  font=font_l, anchor="w", padx=12, width=35).grid(
            row=row, column=0, sticky="ew", padx=(8, 4), pady=3)

        var = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=var, width=16).grid(
            row=row, column=1, sticky="w", padx=4, pady=3)

        tk.Label(parent, text=hint, bg=bg_r, fg=FG2,
                  font=("Segoe UI", 9), anchor="w", padx=4,
                  wraplength=420, justify="left").grid(
            row=row, column=2, sticky="ew", padx=(4, 12), pady=3)

        parent.columnconfigure(0, minsize=280)
        parent.columnconfigure(1, minsize=160)
        parent.columnconfigure(2, weight=1)
        return var

    # ------------------------------------------------------------------
    # Engram helpers
    # ------------------------------------------------------------------

    def _fill_engrams(self) -> None:
        try:
            pts = int(self._engram_quick_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Enter an integer for points per level.")
            return
        for v in self._engram_vars:
            v.set(str(pts))

    def _clear_engrams(self) -> None:
        for v in self._engram_vars:
            v.set("")

    # ------------------------------------------------------------------
    # INI serialization
    # ------------------------------------------------------------------

    def _build_ini(self) -> ArkIniFile:
        """Build an ArkIniFile from the current form state."""
        ini = ArkIniFile(self._game_ini_path())
        if os.path.isfile(ini.path):
            ini.load()

        ini.ensure_section(_SECTION)
        ini.set_value(_SECTION, "DifficultyOffset",             self._diff_offset.get())
        ini.set_value(_SECTION, "OverrideOfficialDifficulty",   self._override_diff.get())
        ini.set_value(_SECTION, "MaxTamedDinos",                self._max_tamed_dinos.get())
        ini.set_value(_SECTION, "MaxPersonalTamedDinos",        self._max_personal_tamed.get())

        ini.set_value(_SECTION, "DayCycleSpeedScale",           self._day_cycle.get())
        ini.set_value(_SECTION, "DayTimeSpeedScale",            self._daytime.get())
        ini.set_value(_SECTION, "NightTimeSpeedScale",          self._nighttime.get())

        # Player per-level stats
        for idx, v in self._player_per_level.items():
            ini.set_value(_SECTION, f"PerLevelStatsMultiplier_Player[{idx}]", v.get())
        for idx, v in self._player_base.items():
            ini.set_value(_SECTION, f"PlayerBaseStatMultipliers[{idx}]", v.get())

        # Dino stats
        for idx, v in self._dino_add.items():
            ini.set_value(_SECTION, f"PerLevelStatsMultiplier_DinoTamed_Add[{idx}]", v.get())
        for idx, v in self._dino_affinity.items():
            ini.set_value(_SECTION, f"PerLevelStatsMultiplier_DinoTamed_Affinity[{idx}]", v.get())

        # Engram points
        pts = [v.get() for v in self._engram_vars if v.get().strip()]
        ini.set_all_values(_SECTION, "OverridePlayerLevelEngramPoints", pts)

        return ini

    def _load_ini_to_forms(self, ini: ArkIniFile) -> None:
        """Populate all form fields from a loaded ArkIniFile."""
        g = lambda k, d="1.0": ini.get_value(_SECTION, k, d)

        self._diff_offset.set(g("DifficultyOffset", "0.2"))
        self._override_diff.set(g("OverrideOfficialDifficulty", "5.0"))
        self._max_tamed_dinos.set(g("MaxTamedDinos", "5000"))
        self._max_personal_tamed.set(g("MaxPersonalTamedDinos", "500"))

        self._day_cycle.set(g("DayCycleSpeedScale", "1.0"))
        self._daytime.set(g("DayTimeSpeedScale", "1.0"))
        self._nighttime.set(g("NightTimeSpeedScale", "1.0"))

        for idx, v in self._player_per_level.items():
            v.set(g(f"PerLevelStatsMultiplier_Player[{idx}]", "1.0"))
        for idx, v in self._player_base.items():
            v.set(g(f"PlayerBaseStatMultipliers[{idx}]", "1.0"))
        for idx, v in self._dino_add.items():
            v.set(g(f"PerLevelStatsMultiplier_DinoTamed_Add[{idx}]", "1.0"))
        for idx, v in self._dino_affinity.items():
            v.set(g(f"PerLevelStatsMultiplier_DinoTamed_Affinity[{idx}]", "1.0"))

        engrams = ini.get_all_values(_SECTION, "OverridePlayerLevelEngramPoints")
        for i, v in enumerate(self._engram_vars):
            v.set(engrams[i] if i < len(engrams) else "")

    def _forms_to_raw(self) -> None:
        ini = self._build_ini()
        self._raw.delete("1.0", tk.END)
        self._raw.insert("1.0", ini.to_string())

    def _raw_to_forms(self) -> None:
        text = self._raw.get("1.0", tk.END)
        ini = ArkIniFile("")
        ini.load_from_string(text)
        self._load_ini_to_forms(ini)

    # ------------------------------------------------------------------
    # Public: refresh / save / sync
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        path = self._game_ini_path()
        if not os.path.isfile(path):
            return
        ini = ArkIniFile(path)
        ini.load()
        self._load_ini_to_forms(ini)
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        self._raw.delete("1.0", tk.END)
        self._raw.insert("1.0", content)

    def _save(self) -> None:
        path = self._game_ini_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ini = self._build_ini()
        ini.path = path
        ini.save()
        # Also reflect in raw editor
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        self._raw.delete("1.0", tk.END)
        self._raw.insert("1.0", content)
        messagebox.showinfo("Saved", "Game.ini saved to profile.")

    def _sync_to_server(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            messagebox.showwarning("No Server Dir",
                                    "Set the server install directory in the Install tab first.")
            return
        if self._app.server.status in ("running", "starting"):
            if not messagebox.askyesno("Server Running",
                                        "Server is running. Changes take effect after a restart."):
                return
        self._save()
        src = self._game_ini_path()
        dst_dir = os.path.join(server_dir, "ShooterGame", "Saved",
                                "Config", "WindowsServer")
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, "Game.ini")
        shutil.copy2(src, dst)
        messagebox.showinfo("Synced", f"Game.ini copied to server:\n{dst}")

    def _load_from_server(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        src = os.path.join(server_dir, "ShooterGame", "Saved",
                            "Config", "WindowsServer", "Game.ini")
        if not os.path.isfile(src):
            messagebox.showwarning("Not Found", f"Game.ini not found at:\n{src}")
            return
        dst = self._game_ini_path()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        self.refresh()
        messagebox.showinfo("Loaded", "Loaded Game.ini from server directory.")
