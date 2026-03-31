"""
GameUserSettings.ini — comprehensive visual editor.
Organized into inner notebook tabs with presets and tooltips.
"""
from __future__ import annotations
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

from core.ini_parser import ArkIniFile
from ui.widgets.collapsible_frame import CollapsibleFrame

BG   = "#1e1e2e"
BG2  = "#181825"
BG3  = "#313244"
FG   = "#cdd6f4"
FG2  = "#a6adc8"
ACCENT = "#89b4fa"
GREEN  = "#a6e3a1"
YELLOW = "#f9e2af"
RED    = "#f38ba8"

# ---------------------------------------------------------------------------
# Preset definitions  (key → value strings)
# ---------------------------------------------------------------------------
PRESETS = {
    "Official (Default)": {
        "HarvestAmountMultiplier": "1.0",
        "TamingSpeedMultiplier": "1.0",
        "XPMultiplier": "1.0",
        "MatingIntervalMultiplier": "1.0",
        "EggHatchSpeedMultiplier": "1.0",
        "BabyMatureSpeedMultiplier": "1.0",
        "BabyCuddleIntervalMultiplier": "1.0",
        "BabyImprintingStatScaleMultiplier": "1.0",
        "ResourcesRespawnPeriodMultiplier": "1.0",
        "PlayerCharacterWaterDrainMultiplier": "1.0",
        "PlayerCharacterFoodDrainMultiplier": "1.0",
        "PlayerCharacterStaminaDrainMultiplier": "1.0",
        "PlayerCharacterHealthRecoveryMultiplier": "1.0",
        "DinoCharacterHealthRecoveryMultiplier": "1.0",
        "DinoCharacterFoodDrainMultiplier": "1.0",
        "DinoCountMultiplier": "1.0",
        "StructureDamageMultiplier": "1.0",
        "PlayerDamageMultiplier": "1.0",
        "PlayerResistanceMultiplier": "1.0",
        "DinoResistanceMultiplier": "1.0",
        "DinoDamageMultiplier": "1.0",
        "bServerPVE": "False",
        "bServerHardcore": "False",
        "bDisableFriendlyFire": "False",
        "AutoSavePeriodMinutes": "15.0",
    },
    "Boosted x3": {
        "HarvestAmountMultiplier": "3.0",
        "TamingSpeedMultiplier": "3.0",
        "XPMultiplier": "3.0",
        "MatingIntervalMultiplier": "0.33",
        "EggHatchSpeedMultiplier": "3.0",
        "BabyMatureSpeedMultiplier": "3.0",
        "BabyCuddleIntervalMultiplier": "0.33",
        "BabyImprintingStatScaleMultiplier": "1.0",
        "ResourcesRespawnPeriodMultiplier": "0.5",
    },
    "Boosted x5": {
        "HarvestAmountMultiplier": "5.0",
        "TamingSpeedMultiplier": "5.0",
        "XPMultiplier": "5.0",
        "MatingIntervalMultiplier": "0.2",
        "EggHatchSpeedMultiplier": "5.0",
        "BabyMatureSpeedMultiplier": "5.0",
        "BabyCuddleIntervalMultiplier": "0.2",
        "BabyImprintingStatScaleMultiplier": "1.0",
        "ResourcesRespawnPeriodMultiplier": "0.25",
    },
    "Boosted x10": {
        "HarvestAmountMultiplier": "10.0",
        "TamingSpeedMultiplier": "10.0",
        "XPMultiplier": "10.0",
        "MatingIntervalMultiplier": "0.1",
        "EggHatchSpeedMultiplier": "10.0",
        "BabyMatureSpeedMultiplier": "10.0",
        "BabyCuddleIntervalMultiplier": "0.1",
        "BabyImprintingStatScaleMultiplier": "1.0",
        "ResourcesRespawnPeriodMultiplier": "0.1",
    },
    "Solo / Singleplayer": {
        "HarvestAmountMultiplier": "2.0",
        "TamingSpeedMultiplier": "4.0",
        "XPMultiplier": "2.0",
        "MatingIntervalMultiplier": "0.25",
        "EggHatchSpeedMultiplier": "4.0",
        "BabyMatureSpeedMultiplier": "4.0",
        "BabyCuddleIntervalMultiplier": "0.5",
        "BabyImprintingStatScaleMultiplier": "1.0",
        "ResourcesRespawnPeriodMultiplier": "0.5",
        "AutoSavePeriodMinutes": "5.0",
    },
}

# ---------------------------------------------------------------------------
# Field descriptors
# (section, key, label, kind, default, hint, choices)
# kind: "entry" | "check" | "combo" | "spin"
# ---------------------------------------------------------------------------
_F = dict  # shorthand

SECTIONS_FIELDS = {
    "Identity": [
        _F(s="SessionSettings",              k="SessionName",                  l="Server Name",               t="entry", d="My ARK Server",      h="Displayed in the server browser"),
        _F(s="ServerSettings",               k="ServerPassword",               l="Join Password",             t="entry", d="",                   h="Leave empty for a public server"),
        _F(s="ServerSettings",               k="ServerAdminPassword",          l="Admin Password",            t="entry", d="adminpass",          h="Required for admin commands and RCON"),
        _F(s="/Script/Engine.GameSession",   k="MaxPlayers",                   l="Max Players",               t="entry", d="70",                 h="Maximum simultaneous players (default 70)"),
        _F(s="ServerSettings",               k="AutoSavePeriodMinutes",        l="Auto-Save Interval (min)",  t="entry", d="15.0",               h="How often the world saves automatically"),
        _F(s="ServerSettings",               k="RCONEnabled",                  l="Enable RCON",               t="check", d="True",               h="Enable Remote Console access"),
        _F(s="ServerSettings",               k="RCONPort",                     l="RCON Port",                 t="entry", d="27020",              h="TCP port for RCON connections"),
        _F(s="ServerSettings",               k="AdminLogging",                 l="Log Admin Commands",        t="check", d="False",              h="Broadcast admin commands in tribe chat"),
        _F(s="ServerSettings",               k="AllowHitMarkers",              l="Show Hit Markers",          t="check", d="True",               h="Display hit confirmation markers"),
        _F(s="ServerSettings",               k="BanListURL",                   l="Ban List URL",              t="entry", d="http://playark.com/banlist.txt", h="URL to global ban list (checked every 10 min)"),
    ],
    "Rates": [
        _F(s="ServerSettings", k="HarvestAmountMultiplier",        l="Harvest Amount",           t="entry", d="1.0",  h="Multiplier for all harvested resources (wood, stone, fiber…)"),
        _F(s="ServerSettings", k="HarvestHealthMultiplier",        l="Harvest Health",           t="entry", d="1.0",  h="How many hits a resource node takes before it depletes"),
        _F(s="ServerSettings", k="ResourcesRespawnPeriodMultiplier",l="Resource Respawn Speed",  t="entry", d="1.0",  h="< 1.0 = faster respawn, > 1.0 = slower"),
        _F(s="ServerSettings", k="TamingSpeedMultiplier",          l="Taming Speed",             t="entry", d="1.0",  h="Higher = faster taming (e.g. 3.0 = 3× speed)"),
        _F(s="ServerSettings", k="XPMultiplier",                   l="XP Multiplier",            t="entry", d="1.0",  h="Experience gained by players"),
        _F(s="ServerSettings", k="KillXPMultiplier",               l="Kill XP Multiplier",       t="entry", d="1.0",  h="XP gained from killing creatures"),
        _F(s="ServerSettings", k="HarvestXPMultiplier",            l="Harvest XP Multiplier",    t="entry", d="1.0",  h="XP gained from harvesting"),
        _F(s="ServerSettings", k="CraftXPMultiplier",              l="Craft XP Multiplier",      t="entry", d="1.0",  h="XP gained from crafting"),
        _F(s="ServerSettings", k="GenericXPMultiplier",            l="Generic XP Multiplier",    t="entry", d="1.0",  h="XP from miscellaneous sources"),
        _F(s="ServerSettings", k="SpecialXPMultiplier",            l="Special XP Multiplier",    t="entry", d="1.0",  h="XP from special events"),
    ],
    "Breeding": [
        _F(s="ServerSettings", k="MatingIntervalMultiplier",       l="Mating Interval",          t="entry", d="1.0",  h="< 1.0 = shorter wait between mates (e.g. 0.1 = 10× faster)"),
        _F(s="ServerSettings", k="MatingSpeedMultiplier",          l="Mating Speed",             t="entry", d="1.0",  h="How fast the mating progress bar fills"),
        _F(s="ServerSettings", k="EggHatchSpeedMultiplier",        l="Egg Hatch Speed",          t="entry", d="1.0",  h="Higher = eggs hatch faster"),
        _F(s="ServerSettings", k="BabyMatureSpeedMultiplier",      l="Baby Mature Speed",        t="entry", d="1.0",  h="Higher = babies grow up faster"),
        _F(s="ServerSettings", k="BabyCuddleIntervalMultiplier",   l="Cuddle Interval",          t="entry", d="1.0",  h="< 1.0 = imprint cuddles needed more frequently (easier 100%)"),
        _F(s="ServerSettings", k="BabyImprintingStatScaleMultiplier", l="Imprint Stat Bonus",    t="entry", d="1.0",  h="How much imprinting boosts baby stats (1.0 = normal)"),
        _F(s="ServerSettings", k="BabyCuddleGracePeriodMultiplier",l="Cuddle Grace Period",      t="entry", d="1.0",  h="Window of time before imprint is missed"),
        _F(s="ServerSettings", k="BabyCuddleLoseImprintQualitySpeedMultiplier", l="Imprint Loss Speed", t="entry", d="1.0", h="How fast imprint quality decays if cuddle is missed"),
        _F(s="ServerSettings", k="LayEggIntervalMultiplier",       l="Lay Egg Interval",         t="entry", d="1.0",  h="How often tamed creatures lay unfertilized eggs"),
        _F(s="ServerSettings", k="PoopIntervalMultiplier",         l="Poop Interval",            t="entry", d="1.0",  h="How often creatures defecate (affects fertilizer farms)"),
    ],
    "Survival": [
        _F(s="ServerSettings", k="PlayerCharacterFoodDrainMultiplier",     l="Player Food Drain",        t="entry", d="1.0", h="Higher = get hungry faster"),
        _F(s="ServerSettings", k="PlayerCharacterWaterDrainMultiplier",    l="Player Water Drain",       t="entry", d="1.0", h="Higher = get thirsty faster"),
        _F(s="ServerSettings", k="PlayerCharacterStaminaDrainMultiplier",  l="Player Stamina Drain",     t="entry", d="1.0", h="Higher = stamina depletes faster"),
        _F(s="ServerSettings", k="PlayerCharacterHealthRecoveryMultiplier",l="Player Health Recovery",   t="entry", d="1.0", h="Higher = player heals faster"),
        _F(s="ServerSettings", k="DinoCharacterFoodDrainMultiplier",       l="Dino Food Drain",          t="entry", d="1.0", h="How fast tamed dinos consume food"),
        _F(s="ServerSettings", k="DinoCharacterHealthRecoveryMultiplier",  l="Dino Health Recovery",     t="entry", d="1.0", h="How fast dinos regenerate health"),
        _F(s="ServerSettings", k="PassiveTameIntervalMultiplier",          l="Passive Tame Interval",    t="entry", d="1.0", h="< 1.0 = passive tames go faster"),
    ],
    "Combat": [
        _F(s="ServerSettings", k="PlayerDamageMultiplier",          l="Player Damage",            t="entry", d="1.0", h="Damage dealt by players"),
        _F(s="ServerSettings", k="PlayerResistanceMultiplier",      l="Player Resistance",        t="entry", d="1.0", h="< 1.0 = players take less damage"),
        _F(s="ServerSettings", k="DinoDamageMultiplier",            l="Wild Dino Damage",         t="entry", d="1.0", h="Damage dealt by wild creatures"),
        _F(s="ServerSettings", k="DinoResistanceMultiplier",        l="Wild Dino Resistance",     t="entry", d="1.0", h="< 1.0 = wild dinos take less damage (tougher)"),
        _F(s="ServerSettings", k="TamedDinoDamageMultiplier",       l="Tamed Dino Damage",        t="entry", d="1.0", h="Damage dealt by tamed creatures"),
        _F(s="ServerSettings", k="TamedDinoResistanceMultiplier",   l="Tamed Dino Resistance",    t="entry", d="1.0", h="< 1.0 = tamed dinos take less damage"),
        _F(s="ServerSettings", k="StructureDamageMultiplier",       l="Structure Damage",         t="entry", d="1.0", h="Damage dealt to structures"),
        _F(s="ServerSettings", k="StructureResistanceMultiplier",   l="Structure Resistance",     t="entry", d="1.0", h="< 1.0 = structures take less damage"),
        _F(s="ServerSettings", k="DinoCountMultiplier",             l="Wild Dino Count",          t="entry", d="1.0", h="Scales the number of wild creatures on the map"),
    ],
    "PvP / PvE": [
        _F(s="ServerSettings", k="bServerPVE",                      l="PvE Mode",                 t="check", d="False",   h="Disable player vs player damage"),
        _F(s="ServerSettings", k="bServerHardcore",                 l="Hardcore (Permadeath)",    t="check", d="False",   h="Players lose their character on death"),
        _F(s="ServerSettings", k="bDisableFriendlyFire",            l="Disable Friendly Fire",    t="check", d="False",   h="Tribe members cannot damage each other"),
        _F(s="ServerSettings", k="bPvEDisableFriendlyFire",         l="PvE: Disable Friendly Fire",t="check",d="False",   h="Prevents all player-to-player damage in PvE"),
        _F(s="ServerSettings", k="AllowCaveBuildingPvE",            l="PvE: Allow Cave Building", t="check", d="False",   h="Allow building inside caves in PvE mode"),
        _F(s="ServerSettings", k="AllowFlyerCarryPvE",              l="PvE: Flyer Carry Players", t="check", d="False",   h="Allow flyers to pick up players in PvE"),
        _F(s="ServerSettings", k="AllowThirdPersonPlayer",          l="Allow 3rd Person Camera",  t="check", d="True",    h="Players can switch to third-person view"),
        _F(s="ServerSettings", k="AlwaysNotifyPlayerJoined",        l="Announce Player Join",     t="check", d="True",    h="Broadcast a message when a player connects"),
        _F(s="ServerSettings", k="AlwaysNotifyPlayerLeft",          l="Announce Player Leave",    t="check", d="True",    h="Broadcast a message when a player disconnects"),
        _F(s="ServerSettings", k="bAllowUnlimitedRespecs",          l="Unlimited Respecs",        t="check", d="False",   h="Players can re-spec stats and engrams for free"),
        _F(s="ServerSettings", k="AllowRaidDinoFeeding",            l="Allow Titanosaur Feeding", t="check", d="False",   h="Enable Titanosaur taming via feeding"),
        _F(s="ServerSettings", k="EnablePvPGamma",                  l="PvP Gamma Adjustment",     t="check", d="False",   h="Allow gamma changes on PvP servers"),
    ],
    "Structures": [
        _F(s="ServerSettings", k="StructurePickupTimeAfterPlacement",l="Pickup Window (sec)",     t="entry", d="30.0",    h="Seconds after placement when structures can be freely picked up"),
        _F(s="ServerSettings", k="StructurePickupHoldDuration",     l="Pickup Hold Duration",     t="entry", d="0.5",     h="Seconds to hold E to pick up a structure"),
        _F(s="ServerSettings", k="PlatformSaddleBuildAreaBoundsMultiplier",l="Platform Saddle Area",t="entry",d="1.0",    h="Increases the build area on platform saddles"),
        _F(s="ServerSettings", k="MaxStructuresInRange",            l="Max Structures in Range",  t="entry", d="10500",   h="Maximum structures within the anti-structure range"),
        _F(s="ServerSettings", k="OverrideStructurePlatformPrevention",l="Override Platform Restrictions",t="check",d="False",h="Allow normally-restricted structures on platforms"),
        _F(s="ServerSettings", k="FlyerPlatformMaxStructureBuildDistance",l="Flyer Platform Build Distance",t="entry",d="10000",h="Max distance you can build from center of flyer platform"),
        _F(s="ServerSettings", k="bDisableStructureDecayPvE",       l="PvE: Disable Decay",       t="check", d="False",   h="Turn off structure auto-decay in PvE mode"),
        _F(s="ServerSettings", k="PvPStructureDecay",               l="PvP Structure Decay",      t="check", d="False",   h="Enable structure decay on PvP servers"),
    ],
    "Transfers": [
        _F(s="ServerSettings", k="PreventDownloadSurvivors",        l="Block: Download Survivors",t="check", d="False",   h="Prevent transferring characters from other servers"),
        _F(s="ServerSettings", k="PreventDownloadItems",            l="Block: Download Items",    t="check", d="False",   h="Prevent transferring items from other servers"),
        _F(s="ServerSettings", k="PreventDownloadDinos",            l="Block: Download Dinos",    t="check", d="False",   h="Prevent transferring tamed creatures from other servers"),
        _F(s="ServerSettings", k="PreventUploadSurvivors",          l="Block: Upload Survivors",  t="check", d="False",   h="Prevent uploading characters to other servers"),
        _F(s="ServerSettings", k="PreventUploadItems",              l="Block: Upload Items",      t="check", d="False",   h="Prevent uploading items to other servers"),
        _F(s="ServerSettings", k="PreventUploadDinos",              l="Block: Upload Dinos",      t="check", d="False",   h="Prevent uploading tamed creatures to other servers"),
        _F(s="ServerSettings", k="noTributeDownloads",              l="Disable All Tribute Transfers",t="check",d="False",h="Completely disable the obelisk upload/download system"),
        _F(s="ServerSettings", k="CrossARKAllowForeignDinoDownloads",l="Allow Foreign Dino Downloads",t="check",d="False",h="Allow dinos from other ARK games/mods"),
    ],
}


class SettingsGUSTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self._app = app
        # {key: tk.Variable}
        self._vars: dict[str, tk.Variable] = {}
        # {key: field dict}
        self._field_map: dict[str, dict] = {
            f["k"]: f
            for fields in SECTIONS_FIELDS.values()
            for f in fields
        }
        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    # Profile paths
    # ------------------------------------------------------------------

    def _gus_path(self) -> str:
        name = self._app.config.get("active_profile", "default")
        return os.path.join(self._app._manager_dir, "profiles", name,
                             "GameUserSettings.ini")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=BG2)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="💾  Save to Profile",
                   style="Accent.TButton",
                   command=self._save).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(toolbar, text="⟳  Sync to Server",
                   command=self._sync_to_server).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        ttk.Button(toolbar, text="↓  Load from Server",
                   command=self._load_from_server).pack(side=tk.LEFT, pady=6)

        # Presets
        tk.Label(toolbar, text="  Preset:", bg=BG2, fg=FG2,
                  font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(24, 4))
        self._preset_var = tk.StringVar(value="— choose —")
        preset_combo = ttk.Combobox(
            toolbar, textvariable=self._preset_var,
            values=["— choose —"] + list(PRESETS.keys()),
            state="readonly", width=20,
        )
        preset_combo.pack(side=tk.LEFT, pady=6)
        preset_combo.bind("<<ComboboxSelected>>", self._apply_preset)

        tk.Frame(self, bg=BG3, height=1).pack(fill=tk.X)

        # ── Inner notebook ───────────────────────────────────────────
        inner_nb = ttk.Notebook(self)
        inner_nb.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        for tab_title, fields in SECTIONS_FIELDS.items():
            frame = tk.Frame(inner_nb, bg=BG)
            inner_nb.add(frame, text=f"  {tab_title}  ")
            self._build_section(frame, fields)

    def _build_section(self, parent: tk.Frame, fields: list[dict]) -> None:
        """Build a scrollable grid of labelled fields for one section."""
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                     lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"),
                         add=True)

        # Column headers
        tk.Label(inner, text="Setting", bg=BG3, fg=ACCENT,
                  font=("Segoe UI", 9, "bold"),
                  width=32, anchor="w", padx=8).grid(
            row=0, column=0, sticky="ew", padx=(8, 2), pady=(6, 2))
        tk.Label(inner, text="Value", bg=BG3, fg=ACCENT,
                  font=("Segoe UI", 9, "bold"),
                  width=18, anchor="w", padx=4).grid(
            row=0, column=1, sticky="ew", padx=2, pady=(6, 2))
        tk.Label(inner, text="Description", bg=BG3, fg=ACCENT,
                  font=("Segoe UI", 9, "bold"), anchor="w", padx=4).grid(
            row=0, column=2, sticky="ew", padx=(2, 8), pady=(6, 2))
        inner.columnconfigure(0, minsize=260)
        inner.columnconfigure(1, minsize=180)
        inner.columnconfigure(2, weight=1)

        for row_i, f in enumerate(fields, start=1):
            bg_row = BG if row_i % 2 == 0 else BG2
            key   = f["k"]
            label = f["l"]
            kind  = f["t"]
            default = f["d"]
            hint  = f.get("h", "")

            # Label cell
            lbl = tk.Label(inner, text=label, bg=bg_row, fg=FG,
                            font=("Segoe UI", 10), anchor="w", padx=12)
            lbl.grid(row=row_i, column=0, sticky="ew", padx=(8, 2), pady=1)

            # Value cell
            cell = tk.Frame(inner, bg=bg_row)
            cell.grid(row=row_i, column=1, sticky="ew", padx=2, pady=1)

            if kind == "check":
                var = tk.BooleanVar(value=default.lower() == "true")
                cb = ttk.Checkbutton(cell, variable=var,
                                      text="Enabled")
                cb.pack(anchor="w", padx=4)
            elif kind == "combo":
                var = tk.StringVar(value=default)
                choices = f.get("c", [])
                ttk.Combobox(cell, textvariable=var, values=choices,
                              state="readonly", width=16).pack(anchor="w", padx=4)
            else:  # entry
                var = tk.StringVar(value=default)
                entry = ttk.Entry(cell, textvariable=var, width=18)
                entry.pack(anchor="w", padx=4)

            self._vars[key] = var

            # Hint cell
            tk.Label(inner, text=hint, bg=bg_row, fg=FG2,
                      font=("Segoe UI", 9), anchor="w", wraplength=380,
                      padx=4).grid(row=row_i, column=2, sticky="ew",
                                    padx=(2, 8), pady=1)

    # ------------------------------------------------------------------
    # Data load / save
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Load values from the profile's GameUserSettings.ini."""
        path = self._gus_path()
        if not os.path.isfile(path):
            return
        ini = ArkIniFile(path)
        ini.load()
        for key, var in self._vars.items():
            field = self._field_map[key]
            raw = ini.get_value(field["s"], key, field["d"])
            if isinstance(var, tk.BooleanVar):
                var.set(raw.lower() in ("true", "1", "yes"))
            else:
                var.set(raw)

    def _save(self) -> None:
        path = self._gus_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ini = ArkIniFile(path)
        if os.path.isfile(path):
            ini.load()
        for key, var in self._vars.items():
            field = self._field_map[key]
            if isinstance(var, tk.BooleanVar):
                value = "True" if var.get() else "False"
            else:
                value = var.get()
            ini.set_value(field["s"], key, value)
        ini.save()
        messagebox.showinfo("Saved", "GameUserSettings.ini saved to profile.\n"
                             "Use 'Sync to Server' to apply it.")

    def _sync_to_server(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        if not server_dir:
            messagebox.showwarning("No Server Dir",
                                    "Set the server install directory in the Install tab first.")
            return
        if self._app.server.status in ("running", "starting"):
            if not messagebox.askyesno(
                    "Server Running",
                    "The server is running.\nChanges take effect after a restart. Continue?"):
                return
        self._save()
        src = self._gus_path()
        dst_dir = os.path.join(server_dir, "ShooterGame", "Saved",
                                "Config", "WindowsServer")
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, "GameUserSettings.ini")
        shutil.copy2(src, dst)
        messagebox.showinfo("Synced", f"GameUserSettings.ini copied to server:\n{dst}")

    def _load_from_server(self) -> None:
        profile = self._app.get_active_profile()
        server_dir = profile.get("server_install_dir", "")
        src = os.path.join(server_dir, "ShooterGame", "Saved",
                            "Config", "WindowsServer", "GameUserSettings.ini")
        if not os.path.isfile(src):
            messagebox.showwarning("Not Found",
                                    f"GameUserSettings.ini not found at:\n{src}")
            return
        dst = self._gus_path()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        self.refresh()
        messagebox.showinfo("Loaded", "Loaded GameUserSettings.ini from server directory.")

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    def _apply_preset(self, event=None) -> None:
        name = self._preset_var.get()
        if name not in PRESETS:
            return
        preset = PRESETS[name]
        for key, value in preset.items():
            if key in self._vars:
                var = self._vars[key]
                if isinstance(var, tk.BooleanVar):
                    var.set(value.lower() in ("true", "1"))
                else:
                    var.set(value)
        self._preset_var.set("— choose —")
        messagebox.showinfo("Preset Applied",
                             f"'{name}' preset applied.\n"
                             "Click 'Save to Profile' to keep it.")
