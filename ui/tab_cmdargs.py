"""
Launch arguments builder - based on the ARK server configuration wiki.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, scrolledtext

BG    = "#1e1e2e"
BG2   = "#181825"
BG3   = "#313244"
FG    = "#cdd6f4"
FG2   = "#a6adc8"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"

# (flag, label, description, category, default_on)
_FLAGS = [
    # Core
    ("-log",                        "Enable Logging",               "Write server output to log files",                          "Core",       True),
    ("-NoBattlEye",                 "Disable BattlEye",             "Turn off BattlEye anti-cheat (common for private servers)",  "Core",       True),
    ("-forcerespawndinos",          "Respawn Dinos on Start",       "Destroy and re-spawn all wild dinos when the server starts", "Core",       False),
    ("-preventhibernation",         "Prevent Dino Hibernation",     "Keep all dinos active even far from players",               "Core",       False),
    ("-ForceAllowCaveFlyers",       "Allow Cave Flyers",            "Allow flyers inside cave areas",                            "Core",       False),
    ("-NoDinos",                    "No Wild Dinos",                "Disable all wild creature spawning",                        "Core",       False),
    ("-NoWildBabies",               "No Wild Babies",               "Prevent wild baby creatures from spawning",                 "Core",       False),
    ("-AllowFlyerSpeedLeveling",    "Flyer Speed Leveling",         "Allow players to level up flyer movement speed",            "Core",       False),
    # Network
    ("-crossplay",                  "Enable Crossplay (EOS)",       "Allow Steam and Epic Games players to join together",        "Network",    False),
    ("-epicgames",                  "Force Epic Games Login",       "Force EOS/Epic login for connections",                      "Network",    False),
    # Performance
    ("-UseStructureStasisGrid",     "Structure Stasis Grid",        "Improves performance on servers with large bases",          "Performance",False),
    ("-StasisKeepControllers",      "Keep NPC Controllers",         "Keeps creature AI controllers loaded (reduces lag spikes)", "Performance",False),
    ("-structurememopts",           "Structure Memory Opts",        "Enable structure memory optimizations",                     "Performance",False),
    ("-NoHangDetection",            "Disable Hang Detection",       "Disable the 45-min startup hang detection timeout",         "Performance",False),
    ("-usecache",                   "Use Cache",                    "Cache commonly used data to improve load times",            "Performance",False),
    # Security
    ("-exclusivejoin",              "Whitelist Only",               "Only allow players on the whitelist to join",               "Security",   False),
    ("-insecure",                   "Disable VAC",                  "Disable Valve Anti-Cheat (not recommended)",                "Security",   False),
    ("-noundermeshchecking",        "Disable Anti-Mesh Check",      "Turn off the anti-meshing system",                         "Security",   False),
    ("-noundermeshkilling",         "No Anti-Mesh Kills",           "Allow teleporting but disable anti-mesh kills",             "Security",   False),
    ("-UseSecureSpawnRules",        "Secure Spawn Rules",           "Extra spawn-point validation",                              "Security",   False),
    ("-UseItemDupeCheck",           "Item Dupe Check",              "Additional item duplication protection",                    "Security",   False),
    # Logging
    ("-servergamelog",              "Server Game Log",              "Enable admin command logging to file",                      "Logging",    False),
    ("-servergamelogincludetribelogs","Include Tribe Logs",         "Include tribe events in the game log",                      "Logging",    False),
    ("-ServerRCONOutputTribeLogs",  "RCON Tribe Logs",              "Send tribe logs to RCON output",                            "Logging",    False),
    ("-NotifyAdminCommandsInChat",  "Admin Cmd Chat Notify",        "Show admin commands in admin chat",                         "Logging",    False),
    # Save format
    ("-newsaveformat",              "New Save Format",              "Use the v11 save format (faster, smaller files)",           "Save",       False),
    ("-automanagedmods",            "Auto-Manage Mods",             "Auto-download mods listed in Game.ini [ModInstaller]",      "Save",       False),
    # Misc
    ("-UseDynamicConfig",           "Dynamic Config",               "Enable dynamic server config updates without restart",      "Misc",       False),
    ("-noantispeedhack",            "Disable Speed Hack Detect",    "Turn off the speed-hack detection system",                  "Misc",       False),
    ("-forceuseperfthreads",        "Force Perf Threads",           "Force the server to use performance threads",               "Misc",       False),
    ("-BackupTransferPlayerDatas",  "Backup Player Data",           "Create separate backups for character profiles on transfer","Misc",       False),
]

_MAPS_ASE = [
    "TheIsland", "TheCenter", "ScorchedEarth_P", "Ragnarok",
    "Aberration_P", "Extinction", "Genesis", "Genesis2",
    "CrystalIsles", "LostIsland", "Fjordur",
]
_MAPS_ASA = [
    "TheIsland_WP", "TheCenter_WP", "ScorchedEarth_WP",
    "Ragnarok_WP", "Aberration_WP",
]
_EVENTS = ["None", "WinterWonderland", "Easter", "Summer", "Arkaeology",
           "FearEvolved", "TurkeyTrial", "Birthday", "NewYear"]


def build_launch_args(profile: dict) -> list[str]:
    la = profile.get("launch_args", {})
    map_name = profile.get("map", "TheIsland")

    parts = [map_name, "?listen"]

    for key in ("MaxPlayers", "Port", "QueryPort"):
        val = la.get(key)
        if val is not None:
            parts.append(f"?{key}={val}")

    if la.get("ServerName"):
        parts.append(f"?SessionName={la['ServerName']}")
    if la.get("ServerPassword"):
        parts.append(f"?ServerPassword={la['ServerPassword']}")
    if la.get("ServerAdminPassword"):
        parts.append(f"?ServerAdminPassword={la['ServerAdminPassword']}")
    if la.get("RCONEnabled", True):
        parts.append("?RCONEnabled=True")
        rcon_port = la.get("RCONPort", profile.get("rcon", {}).get("port", 27020))
        parts.append(f"?RCONPort={rcon_port}")
    if la.get("ClusterId"):
        parts.append(f"?AltSaveDirectoryName={la['ClusterId']}")

    combined = "".join(parts)  # parts already carry their own leading "?"
    args = [combined]

    # Extra ?-style args
    extra_q = la.get("extra_query", "").strip()
    if extra_q:
        args[0] = args[0] + "?" + extra_q.lstrip("?")

    for flag in la.get("flags", []):
        if flag:
            args.append(flag if flag.startswith("-") else f"-{flag}")

    if la.get("ClusterDirOverride"):
        args.append(f"-ClusterDirOverride={la['ClusterDirOverride']}")
    if la.get("MultihomeIP"):
        args.append(f"-MULTIHOME={la['MultihomeIP']}")
    if la.get("GBUsageToForceRestart"):
        args.append(f"-GBUsageToForceRestart={la['GBUsageToForceRestart']}")
    if la.get("ActiveEvent") and la.get("ActiveEvent") != "None":
        args.append(f"-ActiveEvent={la['ActiveEvent']}")

    return args


class CmdArgsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        self._flag_vars: dict[str, tk.BooleanVar] = {}
        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Toolbar
        toolbar = tk.Frame(self, bg=BG2)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="💾  Save", style="Accent.TButton",
                   command=self._save).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(toolbar, text="Reset to Defaults",
                   command=self._reset).pack(side=tk.LEFT, pady=6)
        tk.Frame(self, bg=BG3, height=1).pack(fill=tk.X)

        # Inner notebook
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True)

        self._build_tab_basic()
        self._build_tab_flags()
        self._build_tab_cluster()
        self._build_tab_preview()

    # ------------------------------------------------------------------
    # Tab: Basic
    # ------------------------------------------------------------------

    def _build_tab_basic(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Basic  ")

        canvas, inner = self._scrollable(frame)

        # Map
        map_grp = ttk.LabelFrame(inner, text="Map", padding=10)
        map_grp.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        map_grp.columnconfigure(1, weight=1)

        tk.Label(map_grp, text="Game:", bg=BG, fg=FG).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._game_var = tk.StringVar(value="ase")
        game_combo = ttk.Combobox(map_grp, textvariable=self._game_var,
                                   values=["ase", "asa"], state="readonly", width=8)
        game_combo.grid(row=0, column=1, sticky="w")
        game_combo.bind("<<ComboboxSelected>>", self._on_game_change)
        tk.Label(map_grp, text="  ase = Survival Evolved  |  asa = Survival Ascended",
                  bg=BG, fg=FG2, font=("Segoe UI", 9)).grid(
            row=0, column=2, sticky="w")

        tk.Label(map_grp, text="Map:", bg=BG, fg=FG).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        self._map_var = tk.StringVar(value="TheIsland")
        self._map_combo = ttk.Combobox(map_grp, textvariable=self._map_var,
                                        values=_MAPS_ASE, width=22)
        self._map_combo.grid(row=1, column=1, sticky="w", pady=(8, 0))

        tk.Label(map_grp, text="Custom map name:", bg=BG, fg=FG2,
                  font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=(16, 0))
        self._custom_map_var = tk.StringVar()
        ttk.Entry(map_grp, textvariable=self._custom_map_var, width=20).grid(
            row=1, column=3, sticky="w", padx=(4, 0), pady=(8, 0))
        tk.Label(map_grp, text="(overrides dropdown if filled)",
                  bg=BG, fg=FG2, font=("Segoe UI", 8)).grid(
            row=2, column=2, columnspan=2, sticky="w")

        # Connection
        conn_grp = ttk.LabelFrame(inner, text="Connection", padding=10)
        conn_grp.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
        conn_grp.columnconfigure(1, weight=1)

        self._arg_vars: dict[str, tk.StringVar] = {}
        conn_fields = [
            ("Port",             "Game Port",          "7777",   "UDP port players connect to (default 7777)"),
            ("QueryPort",        "Steam Query Port",   "27015",  "UDP port for Steam server browser (default 27015)"),
            ("MaxPlayers",       "Max Players",        "70",     "Maximum simultaneous players"),
        ]
        for i, (key, label, default, hint) in enumerate(conn_fields):
            tk.Label(conn_grp, text=f"{label}:", bg=BG, fg=FG, width=20, anchor="w").grid(
                row=i, column=0, sticky="w", pady=3)
            v = tk.StringVar(value=default)
            ttk.Entry(conn_grp, textvariable=v, width=10).grid(
                row=i, column=1, sticky="w")
            tk.Label(conn_grp, text=hint, bg=BG, fg=FG2, font=("Segoe UI", 9)).grid(
                row=i, column=2, sticky="w", padx=(12, 0))
            self._arg_vars[key] = v

        # Multihome
        tk.Label(conn_grp, text="Bind to IP (MULTIHOME):", bg=BG, fg=FG,
                  width=20, anchor="w").grid(row=3, column=0, sticky="w", pady=(8, 3))
        self._multihome_var = tk.StringVar()
        ttk.Entry(conn_grp, textvariable=self._multihome_var, width=18).grid(
            row=3, column=1, sticky="w", pady=(8, 3))
        tk.Label(conn_grp, text="Leave blank to bind to all interfaces",
                  bg=BG, fg=FG2, font=("Segoe UI", 9)).grid(
            row=3, column=2, sticky="w", padx=(12, 0))

        # RCON
        rcon_grp = ttk.LabelFrame(inner, text="RCON", padding=10)
        rcon_grp.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
        rcon_grp.columnconfigure(1, weight=1)

        self._rcon_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(rcon_grp, text="Enable RCON",
                         variable=self._rcon_enabled_var).grid(
            row=0, column=0, sticky="w")

        tk.Label(rcon_grp, text="RCON Port:", bg=BG, fg=FG).grid(
            row=0, column=1, sticky="e", padx=(40, 8))
        self._arg_vars["RCONPort"] = tk.StringVar(value="27020")
        ttk.Entry(rcon_grp, textvariable=self._arg_vars["RCONPort"], width=8).grid(
            row=0, column=2, sticky="w")

        # Event
        event_grp = ttk.LabelFrame(inner, text="Active Event (optional)", padding=10)
        event_grp.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
        self._event_var = tk.StringVar(value="None")
        ttk.Combobox(event_grp, textvariable=self._event_var,
                      values=_EVENTS, state="readonly", width=20).pack(
            side=tk.LEFT)
        tk.Label(event_grp, text="  Activates the selected seasonal event",
                  bg=BG, fg=FG2, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Memory restart
        mem_grp = ttk.LabelFrame(inner, text="Auto-Restart on Memory Use (optional)", padding=10)
        mem_grp.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 12))
        tk.Label(mem_grp, text="Restart when RAM usage exceeds (GB):",
                  bg=BG, fg=FG).pack(side=tk.LEFT)
        self._gb_restart_var = tk.StringVar()
        ttk.Entry(mem_grp, textvariable=self._gb_restart_var, width=6).pack(
            side=tk.LEFT, padx=8)
        tk.Label(mem_grp, text="Leave blank to disable",
                  bg=BG, fg=FG2, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        inner.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Tab: Flags
    # ------------------------------------------------------------------

    def _build_tab_flags(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Launch Flags  ")

        canvas, inner = self._scrollable(frame)

        # Group by category
        categories: dict[str, list] = {}
        for flag, label, desc, cat, default_on in _FLAGS:
            categories.setdefault(cat, []).append((flag, label, desc, default_on))

        row = 0
        for cat, items in categories.items():
            # Category header
            tk.Label(inner, text=cat, bg=BG3, fg=ACCENT,
                      font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                      anchor="w").grid(row=row, column=0, columnspan=3,
                                        sticky="ew", padx=8, pady=(8, 2))
            row += 1

            for flag, label, desc, default_on in items:
                bg_r = BG if row % 2 == 0 else BG2
                var = tk.BooleanVar(value=default_on)
                self._flag_vars[flag] = var
                var.trace_add("write", lambda *_: self._update_preview())

                ttk.Checkbutton(inner, text="", variable=var).grid(
                    row=row, column=0, sticky="w", padx=(16, 0), pady=1)
                tk.Label(inner, text=label, bg=bg_r, fg=FG,
                          font=("Segoe UI", 10), width=30, anchor="w").grid(
                    row=row, column=1, sticky="ew", pady=1)
                tk.Label(inner, text=desc, bg=bg_r, fg=FG2,
                          font=("Segoe UI", 9), anchor="w").grid(
                    row=row, column=2, sticky="ew", padx=(8, 12), pady=1)
                row += 1

        inner.columnconfigure(1, minsize=240)
        inner.columnconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # Tab: Cluster
    # ------------------------------------------------------------------

    def _build_tab_cluster(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Cluster  ")

        info = tk.Label(frame,
            text="Cluster settings allow players to transfer characters, items, and dinos\n"
                 "between servers. All servers in a cluster must share the same Cluster ID.",
            bg=BG3, fg=FG2, font=("Segoe UI", 10), padx=12, pady=8,
            justify="left")
        info.pack(fill=tk.X, padx=8, pady=(8, 0))

        grp = ttk.LabelFrame(frame, text="Cluster Configuration", padding=12)
        grp.pack(fill=tk.X, padx=12, pady=12)
        grp.columnconfigure(1, weight=1)

        fields = [
            ("ClusterId",         "Cluster ID",              "",   "Unique name shared by all servers in the cluster"),
            ("ClusterDirOverride","Cluster Save Directory",  "",   "Full path to the shared cluster save folder"),
        ]
        self._cluster_vars: dict[str, tk.StringVar] = {}
        for i, (key, label, default, hint) in enumerate(fields):
            tk.Label(grp, text=f"{label}:", bg=BG, fg=FG, width=26,
                      anchor="w").grid(row=i, column=0, sticky="w", pady=4)
            v = tk.StringVar(value=default)
            ttk.Entry(grp, textvariable=v, width=40).grid(
                row=i, column=1, sticky="ew", padx=(0, 8))
            tk.Label(grp, text=hint, bg=BG, fg=FG2,
                      font=("Segoe UI", 9)).grid(row=i, column=2, sticky="w")
            self._cluster_vars[key] = v
            v.trace_add("write", lambda *_: self._update_preview())

        tk.Label(grp,
                  text="ℹ  Leave Cluster ID blank if this is a standalone server.",
                  bg=BG, fg=FG2, font=("Segoe UI", 9)).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(12, 0))

    # ------------------------------------------------------------------
    # Tab: Preview
    # ------------------------------------------------------------------

    def _build_tab_preview(self) -> None:
        frame = tk.Frame(self._nb, bg=BG)
        self._nb.add(frame, text="  Preview  ")

        tk.Label(frame,
                  text="Full launch command - copy this to run your server manually.",
                  bg=BG3, fg=FG2, font=("Segoe UI", 9), padx=12, pady=6,
                  justify="left").pack(fill=tk.X)

        self._preview = scrolledtext.ScrolledText(
            frame, bg=BG2, fg=ACCENT,
            font=("Consolas", 10), wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._preview.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Button(frame, text="Copy to Clipboard",
                   command=self._copy_preview).pack(anchor="e", padx=8, pady=(0, 8))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _scrollable(self, parent):
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

    def _on_game_change(self, event=None) -> None:
        maps = _MAPS_ASA if self._game_var.get() == "asa" else _MAPS_ASE
        self._map_combo["values"] = maps
        if self._map_var.get() not in maps:
            self._map_var.set(maps[0])
        self._update_preview()

    def _build_profile_la(self) -> dict:
        la = {k: v.get() for k, v in self._arg_vars.items()}
        la["RCONEnabled"] = self._rcon_enabled_var.get()
        la["flags"] = [f for f, v in self._flag_vars.items() if v.get()]
        la["MultihomeIP"] = self._multihome_var.get()
        la["GBUsageToForceRestart"] = self._gb_restart_var.get()
        la["ActiveEvent"] = self._event_var.get()
        for k, v in self._cluster_vars.items():
            la[k] = v.get()
        return la

    def _update_preview(self) -> None:
        try:
            profile = dict(self._app.get_active_profile())
            profile["game"] = self._game_var.get()
            profile["map"] = (self._custom_map_var.get().strip()
                               if self._custom_map_var.get().strip()
                               else self._map_var.get())
            profile["launch_args"] = self._build_profile_la()

            game = profile["game"]
            exe = ("ShooterGameServer.exe" if game == "ase" else "ArkAscendedServer.exe")
            args = build_launch_args(profile)
            full_cmd = exe + " " + " ".join(args)

            self._preview.config(state=tk.NORMAL)
            self._preview.delete("1.0", tk.END)
            self._preview.insert("1.0", full_cmd)
            self._preview.config(state=tk.DISABLED)
        except Exception:
            pass

    def _copy_preview(self) -> None:
        text = self._preview.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(text)

    # ------------------------------------------------------------------
    # Refresh / Save
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        profile = self._app.get_active_profile()
        la = profile.get("launch_args", {})

        self._game_var.set(profile.get("game", "ase"))
        self._on_game_change()  # refresh map list
        self._map_var.set(profile.get("map", "TheIsland"))
        self._custom_map_var.set("")

        defaults = {"Port": "7777", "QueryPort": "27015",
                    "MaxPlayers": "70", "RCONPort": "27020",
                    "ServerName": "", "ServerPassword": "", "ServerAdminPassword": ""}
        for key, var in self._arg_vars.items():
            var.set(str(la.get(key, defaults.get(key, ""))))

        self._rcon_enabled_var.set(bool(la.get("RCONEnabled", True)))
        self._multihome_var.set(la.get("MultihomeIP", ""))
        self._gb_restart_var.set(la.get("GBUsageToForceRestart", ""))
        self._event_var.set(la.get("ActiveEvent", "None"))

        active_flags = set(la.get("flags", ["-log", "-NoBattlEye"]))
        for flag, var in self._flag_vars.items():
            var.set(flag in active_flags)

        for k, v in self._cluster_vars.items():
            v.set(la.get(k, ""))

        self._update_preview()

    def _save(self) -> None:
        profile = self._app.get_active_profile()
        profile["game"] = self._game_var.get()
        profile["map"] = (self._custom_map_var.get().strip()
                           if self._custom_map_var.get().strip()
                           else self._map_var.get())
        profile["launch_args"] = self._build_profile_la()
        self._app.save_config()
        self._update_preview()

    def _reset(self) -> None:
        profile = self._app.get_active_profile()
        profile["launch_args"] = self._app._default_profile()["launch_args"]
        profile["map"] = "TheIsland"
        self._app.save_config()
        self.refresh()
