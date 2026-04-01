'use strict';

// ═══════════════════════════════════════════════════════════════════════════
//  SETTINGS DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════

const GUS_SETTINGS = [
  { category: 'Identity', fields: [
    { k:'SessionName',      s:'SessionSettings',            l:'Server Name',              t:'text',   d:'My ARK Server',   h:'Displayed in the server browser' },
    { k:'ServerPassword',   s:'ServerSettings',             l:'Join Password',            t:'text',   d:'',                h:'Leave blank for a public server' },
    { k:'ServerAdminPassword', s:'ServerSettings',          l:'Admin Password',           t:'text',   d:'adminpass',       h:'Required for admin commands and RCON' },
    { k:'MaxPlayers',       s:'/Script/Engine.GameSession', l:'Max Players',              t:'text',   d:'70',              h:'Maximum simultaneous players (default 70)' },
    { k:'AutoSavePeriodMinutes', s:'ServerSettings',        l:'Auto-Save Interval (min)', t:'text',   d:'15.0',            h:'How often the world saves automatically' },
    { k:'RCONEnabled',      s:'ServerSettings',             l:'Enable RCON',              t:'check',  d:'True',            h:'Enable Remote Console access' },
    { k:'RCONPort',         s:'ServerSettings',             l:'RCON Port',                t:'text',   d:'27020',           h:'TCP port for RCON connections' },
    { k:'AdminLogging',     s:'ServerSettings',             l:'Log Admin Commands',       t:'check',  d:'False',           h:'Broadcast admin commands in tribe chat' },
    { k:'AllowHitMarkers',  s:'ServerSettings',             l:'Show Hit Markers',         t:'check',  d:'True',            h:'Display hit confirmation markers' },
    { k:'BanListURL',       s:'ServerSettings',             l:'Ban List URL',             t:'text',   d:'',                h:'Global ban list URL, fetched every 10 min' },
  ]},
  { category: 'Rates', fields: [
    { k:'HarvestAmountMultiplier',          s:'ServerSettings', l:'Harvest Amount',           t:'text', d:'1.0', h:'Multiplier for all harvested resources (wood, stone, fiber…)' },
    { k:'HarvestHealthMultiplier',          s:'ServerSettings', l:'Harvest Health (Node HP)', t:'text', d:'1.0', h:'How many hits a resource node takes before it depletes' },
    { k:'ResourcesRespawnPeriodMultiplier', s:'ServerSettings', l:'Resource Respawn Speed',   t:'text', d:'1.0', h:'< 1.0 = faster respawn, > 1.0 = slower' },
    { k:'TamingSpeedMultiplier',            s:'ServerSettings', l:'Taming Speed',             t:'text', d:'1.0', h:'Higher = faster taming (e.g. 3.0 = 3× speed)' },
    { k:'XPMultiplier',                     s:'ServerSettings', l:'XP Multiplier',            t:'text', d:'1.0', h:'Experience gained by players and dinos' },
    { k:'KillXPMultiplier',                 s:'ServerSettings', l:'Kill XP',                  t:'text', d:'1.0', h:'XP from killing creatures' },
    { k:'HarvestXPMultiplier',              s:'ServerSettings', l:'Harvest XP',               t:'text', d:'1.0', h:'XP from harvesting resources' },
    { k:'CraftXPMultiplier',                s:'ServerSettings', l:'Craft XP',                 t:'text', d:'1.0', h:'XP from crafting items' },
    { k:'GenericXPMultiplier',              s:'ServerSettings', l:'Generic XP',               t:'text', d:'1.0', h:'XP from miscellaneous sources' },
  ]},
  { category: 'Breeding', fields: [
    { k:'MatingIntervalMultiplier',          s:'ServerSettings', l:'Mating Interval',      t:'text', d:'1.0', h:'< 1.0 = shorter wait between mates (e.g. 0.1 = 10× faster)' },
    { k:'MatingSpeedMultiplier',             s:'ServerSettings', l:'Mating Speed',          t:'text', d:'1.0', h:'How fast the mating progress bar fills' },
    { k:'EggHatchSpeedMultiplier',           s:'ServerSettings', l:'Egg Hatch Speed',       t:'text', d:'1.0', h:'Higher = eggs hatch faster' },
    { k:'BabyMatureSpeedMultiplier',         s:'ServerSettings', l:'Baby Mature Speed',     t:'text', d:'1.0', h:'Higher = babies grow up faster' },
    { k:'BabyCuddleIntervalMultiplier',      s:'ServerSettings', l:'Cuddle Interval',       t:'text', d:'1.0', h:'< 1.0 = imprint cuddles available more often (easier 100%)' },
    { k:'BabyImprintingStatScaleMultiplier', s:'ServerSettings', l:'Imprint Stat Bonus',    t:'text', d:'1.0', h:'How much imprinting boosts baby stats' },
    { k:'BabyCuddleGracePeriodMultiplier',   s:'ServerSettings', l:'Cuddle Grace Period',   t:'text', d:'1.0', h:'Window of time before an imprint is missed' },
    { k:'LayEggIntervalMultiplier',          s:'ServerSettings', l:'Lay Egg Interval',      t:'text', d:'1.0', h:'How often tamed creatures lay unfertilized eggs' },
  ]},
  { category: 'Survival', fields: [
    { k:'PlayerCharacterFoodDrainMultiplier',      s:'ServerSettings', l:'Player Food Drain',      t:'text', d:'1.0', h:'Higher = get hungry faster' },
    { k:'PlayerCharacterWaterDrainMultiplier',     s:'ServerSettings', l:'Player Water Drain',     t:'text', d:'1.0', h:'Higher = get thirsty faster' },
    { k:'PlayerCharacterStaminaDrainMultiplier',   s:'ServerSettings', l:'Player Stamina Drain',   t:'text', d:'1.0', h:'Higher = stamina depletes faster' },
    { k:'PlayerCharacterHealthRecoveryMultiplier', s:'ServerSettings', l:'Player Health Recovery', t:'text', d:'1.0', h:'Higher = player heals faster' },
    { k:'DinoCharacterFoodDrainMultiplier',        s:'ServerSettings', l:'Dino Food Drain',        t:'text', d:'1.0', h:'How fast tamed dinos consume food' },
    { k:'DinoCharacterHealthRecoveryMultiplier',   s:'ServerSettings', l:'Dino Health Recovery',   t:'text', d:'1.0', h:'How fast dinos regenerate health' },
    { k:'PassiveTameIntervalMultiplier',           s:'ServerSettings', l:'Passive Tame Interval',  t:'text', d:'1.0', h:'< 1.0 = passive tames go faster' },
  ]},
  { category: 'Combat', fields: [
    { k:'PlayerDamageMultiplier',       s:'ServerSettings', l:'Player Damage',       t:'text', d:'1.0', h:'Damage dealt by players' },
    { k:'PlayerResistanceMultiplier',   s:'ServerSettings', l:'Player Resistance',   t:'text', d:'1.0', h:'< 1.0 = players take less damage' },
    { k:'DinoDamageMultiplier',         s:'ServerSettings', l:'Wild Dino Damage',    t:'text', d:'1.0', h:'Damage dealt by wild creatures' },
    { k:'DinoResistanceMultiplier',     s:'ServerSettings', l:'Wild Dino Resistance',t:'text', d:'1.0', h:'< 1.0 = wild dinos are tougher' },
    { k:'TamedDinoDamageMultiplier',    s:'ServerSettings', l:'Tamed Dino Damage',   t:'text', d:'1.0', h:'Damage dealt by tamed creatures' },
    { k:'TamedDinoResistanceMultiplier',s:'ServerSettings', l:'Tamed Dino Resistance',t:'text',d:'1.0', h:'< 1.0 = tamed dinos take less damage' },
    { k:'StructureDamageMultiplier',    s:'ServerSettings', l:'Structure Damage',    t:'text', d:'1.0', h:'Damage dealt to structures' },
    { k:'StructureResistanceMultiplier',s:'ServerSettings', l:'Structure Resistance',t:'text', d:'1.0', h:'< 1.0 = structures are tougher' },
    { k:'DinoCountMultiplier',          s:'ServerSettings', l:'Wild Dino Count',     t:'text', d:'1.0', h:'Scales the number of wild creatures on the map' },
  ]},
  { category: 'PvP / PvE', fields: [
    { k:'bServerPVE',                   s:'ServerSettings', l:'PvE Mode',                    t:'check', d:'False', h:'Disable player vs player damage' },
    { k:'bServerHardcore',              s:'ServerSettings', l:'Hardcore (Permadeath)',        t:'check', d:'False', h:'Players lose their character on death' },
    { k:'bDisableFriendlyFire',         s:'ServerSettings', l:'Disable Friendly Fire',        t:'check', d:'False', h:'Tribe members cannot damage each other' },
    { k:'bPvEDisableFriendlyFire',      s:'ServerSettings', l:'PvE: Disable All Player Dmg',  t:'check', d:'False', h:'Prevents all player-to-player damage in PvE' },
    { k:'AllowCaveBuildingPvE',         s:'ServerSettings', l:'PvE: Allow Cave Building',     t:'check', d:'False', h:'Allow building inside caves in PvE' },
    { k:'AllowFlyerCarryPvE',           s:'ServerSettings', l:'PvE: Flyer Carry Players',     t:'check', d:'False', h:'Allow flyers to pick up players in PvE' },
    { k:'AllowThirdPersonPlayer',       s:'ServerSettings', l:'Allow 3rd Person Camera',      t:'check', d:'True',  h:'Players can switch to third-person view' },
    { k:'AlwaysNotifyPlayerJoined',     s:'ServerSettings', l:'Announce Player Join',          t:'check', d:'True',  h:'Broadcast a message when a player connects' },
    { k:'AlwaysNotifyPlayerLeft',       s:'ServerSettings', l:'Announce Player Leave',         t:'check', d:'True',  h:'Broadcast a message when a player disconnects' },
    { k:'bAllowUnlimitedRespecs',       s:'ServerSettings', l:'Unlimited Respecs',             t:'check', d:'False', h:'Players can re-spec stats and engrams for free' },
    { k:'AllowRaidDinoFeeding',         s:'ServerSettings', l:'Allow Titanosaur Feeding',      t:'check', d:'False', h:'Enable Titanosaur taming' },
    { k:'EnablePvPGamma',               s:'ServerSettings', l:'PvP Gamma Adjustment',          t:'check', d:'False', h:'Allow gamma changes on PvP servers' },
  ]},
  { category: 'Structures', fields: [
    { k:'StructurePickupTimeAfterPlacement',      s:'ServerSettings', l:'Pickup Window (sec)',           t:'text', d:'30.0',  h:'Seconds after placement when structures can be freely picked up' },
    { k:'StructurePickupHoldDuration',            s:'ServerSettings', l:'Pickup Hold Duration',          t:'text', d:'0.5',   h:'Seconds to hold E to pick up a structure' },
    { k:'PlatformSaddleBuildAreaBoundsMultiplier',s:'ServerSettings', l:'Platform Saddle Build Area',    t:'text', d:'1.0',   h:'Increases the build area on platform saddles' },
    { k:'MaxStructuresInRange',                   s:'ServerSettings', l:'Max Structures in Range',        t:'text', d:'10500', h:'Maximum structures within the anti-structure range' },
    { k:'bDisableStructureDecayPvE',              s:'ServerSettings', l:'PvE: Disable Structure Decay',  t:'check',d:'False', h:'Turn off structure auto-decay in PvE mode' },
  ]},
  { category: 'Transfers', fields: [
    { k:'PreventDownloadSurvivors', s:'ServerSettings', l:'Block: Download Survivors', t:'check', d:'False', h:'Prevent transferring characters from other servers' },
    { k:'PreventDownloadItems',     s:'ServerSettings', l:'Block: Download Items',     t:'check', d:'False', h:'Prevent transferring items from other servers' },
    { k:'PreventDownloadDinos',     s:'ServerSettings', l:'Block: Download Dinos',     t:'check', d:'False', h:'Prevent transferring tamed creatures from other servers' },
    { k:'PreventUploadSurvivors',   s:'ServerSettings', l:'Block: Upload Survivors',   t:'check', d:'False', h:'Prevent uploading characters to other servers' },
    { k:'PreventUploadItems',       s:'ServerSettings', l:'Block: Upload Items',        t:'check', d:'False', h:'Prevent uploading items to other servers' },
    { k:'PreventUploadDinos',       s:'ServerSettings', l:'Block: Upload Dinos',        t:'check', d:'False', h:'Prevent uploading tamed creatures to other servers' },
    { k:'noTributeDownloads',       s:'ServerSettings', l:'Disable All Tribute',        t:'check', d:'False', h:'Completely disable the obelisk upload/download system' },
  ]},
];

const GUS_PRESETS = {
  'Official (Default)': { HarvestAmountMultiplier:'1.0', TamingSpeedMultiplier:'1.0', XPMultiplier:'1.0', MatingIntervalMultiplier:'1.0', EggHatchSpeedMultiplier:'1.0', BabyMatureSpeedMultiplier:'1.0', BabyCuddleIntervalMultiplier:'1.0' },
  'Boosted ×3':  { HarvestAmountMultiplier:'3.0', TamingSpeedMultiplier:'3.0', XPMultiplier:'3.0', MatingIntervalMultiplier:'0.33', EggHatchSpeedMultiplier:'3.0', BabyMatureSpeedMultiplier:'3.0', BabyCuddleIntervalMultiplier:'0.33', ResourcesRespawnPeriodMultiplier:'0.5' },
  'Boosted ×5':  { HarvestAmountMultiplier:'5.0', TamingSpeedMultiplier:'5.0', XPMultiplier:'5.0', MatingIntervalMultiplier:'0.2',  EggHatchSpeedMultiplier:'5.0', BabyMatureSpeedMultiplier:'5.0', BabyCuddleIntervalMultiplier:'0.2',  ResourcesRespawnPeriodMultiplier:'0.25' },
  'Boosted ×10': { HarvestAmountMultiplier:'10.0',TamingSpeedMultiplier:'10.0',XPMultiplier:'10.0',MatingIntervalMultiplier:'0.1',  EggHatchSpeedMultiplier:'10.0',BabyMatureSpeedMultiplier:'10.0',BabyCuddleIntervalMultiplier:'0.1',  ResourcesRespawnPeriodMultiplier:'0.1' },
  'Solo / SP':   { HarvestAmountMultiplier:'2.0', TamingSpeedMultiplier:'4.0', XPMultiplier:'2.0', MatingIntervalMultiplier:'0.25', EggHatchSpeedMultiplier:'4.0', BabyMatureSpeedMultiplier:'4.0', BabyCuddleIntervalMultiplier:'0.5', AutoSavePeriodMinutes:'5.0' },
};

const STAT_NAMES = ['Health','Stamina','Oxygen','Food','Weight','Melee Damage','Movement Speed','Fortitude','Crafting Speed'];

const LAUNCH_FLAGS = [
  { f:'-log',                       l:'Enable Logging',           d:'Write server output to log files',                         cat:'Core',        on:true  },
  { f:'-NoBattlEye',                l:'Disable BattlEye',         d:'Turn off BattlEye anti-cheat',                             cat:'Core',        on:true  },
  { f:'-forcerespawndinos',         l:'Respawn Dinos on Start',   d:'Destroy and re-spawn all wild dinos when server starts',    cat:'Core',        on:false },
  { f:'-preventhibernation',        l:'Prevent Hibernation',      d:'Keep all dinos active even far from players',              cat:'Core',        on:false },
  { f:'-ForceAllowCaveFlyers',      l:'Allow Cave Flyers',        d:'Allow flyers inside cave areas',                           cat:'Core',        on:false },
  { f:'-NoDinos',                   l:'No Wild Dinos',            d:'Disable all wild creature spawning',                       cat:'Core',        on:false },
  { f:'-AllowFlyerSpeedLeveling',   l:'Flyer Speed Leveling',     d:'Allow players to level up flyer movement speed',           cat:'Core',        on:false },
  { f:'-crossplay',                 l:'Enable Crossplay',         d:'Allow Steam and Epic Games players together',               cat:'Network',     on:false },
  { f:'-epicgames',                 l:'Force Epic Login',         d:'Force EOS/Epic login for connections',                     cat:'Network',     on:false },
  { f:'-UseStructureStasisGrid',    l:'Structure Stasis Grid',    d:'Improves performance on servers with large bases',         cat:'Performance', on:false },
  { f:'-StasisKeepControllers',     l:'Keep NPC Controllers',     d:'Keeps creature AI controllers loaded (reduces lag spikes)',cat:'Performance', on:false },
  { f:'-NoHangDetection',           l:'Disable Hang Detection',   d:'Disable the 45-min startup hang detection timeout',        cat:'Performance', on:false },
  { f:'-exclusivejoin',             l:'Whitelist Only',           d:'Only allow players on the whitelist to join',              cat:'Security',    on:false },
  { f:'-noundermeshchecking',       l:'Disable Anti-Mesh Check',  d:'Turn off the anti-meshing system',                        cat:'Security',    on:false },
  { f:'-UseItemDupeCheck',          l:'Item Dupe Check',          d:'Additional item duplication protection',                   cat:'Security',    on:false },
  { f:'-servergamelog',             l:'Server Game Log',          d:'Enable admin command logging to file',                     cat:'Logging',     on:false },
  { f:'-servergamelogincludetribelogs',l:'Include Tribe Logs',    d:'Include tribe events in the game log',                     cat:'Logging',     on:false },
  { f:'-ServerRCONOutputTribeLogs', l:'RCON Tribe Logs',          d:'Send tribe logs to RCON output',                           cat:'Logging',     on:false },
  { f:'-newsaveformat',             l:'New Save Format',          d:'Use v11 save format (faster, smaller files)',               cat:'Save',        on:false },
  { f:'-automanagedmods',           l:'Auto-Manage Mods',         d:'Auto-download mods listed in Game.ini [ModInstaller]',     cat:'Save',        on:false },
  { f:'-UseDynamicConfig',          l:'Dynamic Config',           d:'Enable dynamic server config updates without restart',     cat:'Misc',        on:false },
  { f:'-BackupTransferPlayerDatas', l:'Backup Player Data',       d:'Create separate backups for character profiles on transfer',cat:'Misc',       on:false },
];

const MAPS_ASE = ['TheIsland','TheCenter','ScorchedEarth_P','Ragnarok','Aberration_P','Extinction','Genesis','Genesis2','CrystalIsles','LostIsland','Fjordur'];
const MAPS_ASA = ['TheIsland_WP','TheCenter_WP','ScorchedEarth_WP','Ragnarok_WP','Aberration_WP'];
const EVENTS   = ['None','WinterWonderland','Easter','Summer','Arkaeology','FearEvolved','TurkeyTrial','Birthday'];

// ═══════════════════════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════════════════════

const State = {
  page: 'dashboard',
  config: {},
  profile: {},
  serverStatus: 'stopped',
  uptime: '',
  gusValues: {},
  rconConnected: false,
  _pollTimer: null,
};

// ═══════════════════════════════════════════════════════════════════════════
//  API WRAPPER
// ═══════════════════════════════════════════════════════════════════════════

const API = {
  async call(method, ...args) {
    try {
      const result = await window.pywebview.api[method](...args);
      return result;
    } catch(e) {
      console.error('API error:', method, e);
      return { ok: false, error: String(e) };
    }
  },
  async getConfig()         { return (await this.call('get_config')).data; },
  async getProfile()        { return (await this.call('get_profile')).data; },
  async getProfileNames()   { return (await this.call('get_profile_names')).data; },
  async switchProfile(n)    { return this.call('switch_profile', n); },
  async addProfile(n)       { return this.call('add_profile', n); },
  async saveProfileBasic(d) { return this.call('save_profile_basic', d); },
  async saveLaunchArgs(d)   { return this.call('save_launch_args', d); },
  async saveRconSettings(d) { return this.call('save_rcon_settings', d); },
  async getGusValues()      { return (await this.call('get_gus_values')).data || {}; },
  async saveGusValues(d, custom)    { return this.call('save_gus_values', d, custom || []); },
  async syncGusToServer()   { return this.call('sync_gus_to_server'); },
  async loadGusFromServer() { return this.call('load_gus_from_server'); },
  async getGameIniValues()  { return (await this.call('get_game_ini_values')).data || {}; },
  async getGameIniText()    { return (await this.call('get_game_ini_text')).data || ''; },
  async saveGameIniText(t)  { return this.call('save_game_ini_text', t); },
  async saveGameIniValues(v){ return this.call('save_game_ini_values', v); },
  async syncGameIniToServer(){ return this.call('sync_game_ini_to_server'); },
  async loadGameIniFromServer(){ return this.call('load_game_ini_from_server'); },
  async startServer()       { return this.call('start_server'); },
  async stopServer()        { return this.call('stop_server'); },
  async restartServer()     { return this.call('restart_server'); },
  async getServerStatus()   { return (await this.call('get_server_status')).data; },
  async getSteamcmdInfo()   { return (await this.call('get_steamcmd_info')).data; },
  async setSteamcmdPath(p)  { return this.call('set_steamcmd_path', p); },
  async downloadSteamcmd(d) { return this.call('download_steamcmd', d); },
  async importServer(d)     { return this.call('import_server', d); },
  async installServer()     { return this.call('install_server'); },
  async cancelInstall()     { return this.call('cancel_install'); },
  async checkUpdate()       { return this.call('check_update'); },
  async getLogLines(n)      { return (await this.call('get_log_lines', n)).data || []; },
  async getLogFiles()       { return (await this.call('get_log_files')).data || []; },
  async getLogFileContent(f){ return (await this.call('get_log_file_content', f)).data || ''; },
  async getMods()           { return (await this.call('get_mods')).data || []; },
  async fetchModInfo(id)    { return (await this.call('fetch_mod_info', id)).data; },
  async installMod(id)      { return this.call('install_mod', id); },
  async removeMod(id)       { return this.call('remove_mod', id); },
  async toggleMod(id)       { return this.call('toggle_mod', id); },
  async getBackups()        { return (await this.call('get_backups')).data || []; },
  async createBackup()      { return this.call('create_backup'); },
  async restoreBackup(p)    { return this.call('restore_backup', p); },
  async deleteBackup(p)     { return this.call('delete_backup', p); },
  async applyBackupSchedule(d){ return this.call('apply_backup_schedule', d); },
  async rconConnect(h,p,pw) { return this.call('rcon_connect', h, p, pw); },
  async rconCommand(c)      { return this.call('rcon_command', c); },
  async rconDisconnect()    { return this.call('rcon_disconnect'); },
  async browseFolder()      { return (await this.call('browse_folder')).data; },
  async browseFile(e)       { return (await this.call('browse_file', e)).data; },
  async openFolder(p)       { return this.call('open_folder_in_explorer', p); },
  async getEvents()         { return (await this.call('get_events')) || []; },
};

// ═══════════════════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function qs(sel, root=document)  { return root.querySelector(sel); }
function qsa(sel, root=document) { return [...root.querySelectorAll(sel)]; }
function el(tag, cls='', html='') {
  const e = document.createElement(tag);
  if (cls)  e.className = cls;
  if (html) e.innerHTML = html;
  return e;
}
function svgIcon(path) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px">${path}</svg>`;
}

// Toast
function toast(msg, type='info', duration=3000) {
  const wrap = qs('#toast-container');
  const t = el('div', `toast ${type}`, msg);
  wrap.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

// Modal confirm
function confirm(title, body) {
  return new Promise(resolve => {
    qs('#modal-title').textContent = title;
    qs('#modal-body').textContent  = body;
    qs('#modal-overlay').classList.remove('hidden');
    const ok  = qs('#modal-ok');
    const can = qs('#modal-cancel');
    const cleanup = () => qs('#modal-overlay').classList.add('hidden');
    ok.onclick  = () => { cleanup(); resolve(true); };
    can.onclick = () => { cleanup(); resolve(false); };
  });
}

// Escape HTML
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Toggle button helper
function makeToggle(value, onChange) {
  const btn = document.createElement('button');
  btn.className = `toggle ${value ? 'on' : ''}`;
  btn.onclick = () => {
    const newVal = !btn.classList.contains('on');
    btn.classList.toggle('on', newVal);
    onChange(newVal);
  };
  return btn;
}

// Inner tab helper
function makeInnerTabs(pairs) {
  // pairs: [{label, render}]
  const wrap = el('div');
  const tabRow = el('div', 'inner-tabs');
  const panels = [];
  pairs.forEach(({label, render}, i) => {
    const tab   = el('div', `inner-tab${i===0?' active':''}`, label);
    const panel = el('div', `inner-tab-panel${i===0?' active':''}`);
    render(panel);
    tabRow.appendChild(tab);
    panels.push(panel);
    tab.onclick = () => {
      qsa('.inner-tab', tabRow).forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      panel.classList.add('active');
    };
  });
  wrap.appendChild(tabRow);
  panels.forEach(p => wrap.appendChild(p));
  return wrap;
}

// ═══════════════════════════════════════════════════════════════════════════
//  SEARCH
// ═══════════════════════════════════════════════════════════════════════════

const Search = {
  index: [],

  build() {
    this.index = [];
    GUS_SETTINGS.forEach(cat => {
      cat.fields.forEach(f => {
        this.index.push({ page:'settings', category:cat.category, key:f.k, label:f.l, hint:f.h, id:`gus-${f.k}`, badge:'GameUserSettings' });
      });
    });
    LAUNCH_FLAGS.forEach(f => {
      this.index.push({ page:'launch', category:f.cat, key:f.f, label:f.l, hint:f.d, id:`flag-${f.f.replace(/\W/g,'_')}`, badge:'Launch Args' });
    });
    STAT_NAMES.forEach((n,i) => {
      this.index.push({ page:'gameini', category:'Player Stats', key:`PerLevelStatsMultiplier_Player[${i}]`, label:`Player: ${n}`, hint:'Per-level stat multiplier for player characters', id:`ps-${i}`, badge:'Game.ini' });
      this.index.push({ page:'gameini', category:'Dino Stats',   key:`PerLevelStatsMultiplier_DinoTamed_Add[${i}]`, label:`Dino: ${n}`, hint:'Per-level stat multiplier for tamed dinos', id:`ds-${i}`, badge:'Game.ini' });
    });
    ['DifficultyOffset','OverrideOfficialDifficulty','MaxTamedDinos','DayCycleSpeedScale','DayTimeSpeedScale','NightTimeSpeedScale'].forEach(k => {
      this.index.push({ page:'gameini', category:'Difficulty/Time', key:k, label:k.replace(/([A-Z])/g,' $1').trim(), hint:'Game.ini setting', id:`gi-${k}`, badge:'Game.ini' });
    });
  },

  query(q) {
    if (!q || q.length < 2) return [];
    const lower = q.toLowerCase();
    return this.index.filter(item =>
      item.label.toLowerCase().includes(lower) ||
      item.key.toLowerCase().includes(lower) ||
      item.hint.toLowerCase().includes(lower)
    ).slice(0, 40);
  },

  highlight(text, q) {
    if (!q) return esc(text);
    const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
    return esc(text).replace(re, '<mark>$1</mark>');
  },

  open() {
    qs('#search-overlay').classList.remove('hidden');
    qs('#search-modal-input').value = '';
    qs('#search-modal-input').focus();
    qs('#search-results').innerHTML = '';
    qs('#search-empty').classList.add('hidden');
  },

  close() {
    qs('#search-overlay').classList.add('hidden');
  },

  render(q) {
    const results = this.query(q);
    const container = qs('#search-results');
    const empty = qs('#search-empty');
    container.innerHTML = '';
    if (!q || q.length < 2) { empty.classList.add('hidden'); return; }
    if (!results.length) { empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');

    // Group by badge
    const groups = {};
    results.forEach(r => (groups[r.badge] = groups[r.badge] || []).push(r));
    Object.entries(groups).forEach(([g, items]) => {
      const grp = el('div', 'search-result-group');
      grp.innerHTML = `<div class="search-result-group-title">${esc(g)}</div>`;
      items.forEach(item => {
        const row = el('div', 'search-result-item');
        row.innerHTML = `
          <div>
            <div class="sr-name">${this.highlight(item.label, q)}</div>
            <div class="sr-hint mono">${esc(item.key)}</div>
          </div>
          <span class="sr-badge">${esc(item.category)}</span>`;
        row.onclick = () => {
          this.close();
          Router.navigate(item.page, item.id);
        };
        grp.appendChild(row);
      });
      container.appendChild(grp);
    });
  },

  initEvents() {
    // Topbar search → open overlay
    qs('#search-input').addEventListener('focus', () => { this.open(); qs('#search-modal-input').value = qs('#search-input').value; this.render(qs('#search-input').value); });
    qs('#search-input').addEventListener('input', () => { this.open(); qs('#search-modal-input').value = qs('#search-input').value; this.render(qs('#search-input').value); });
    qs('#search-modal-input').addEventListener('input', e => this.render(e.target.value));
    qs('#search-overlay').addEventListener('click', e => { if (e.target === qs('#search-overlay')) this.close(); });
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') { e.preventDefault(); this.open(); }
      if (e.key === 'Escape') this.close();
    });
  }
};

// ═══════════════════════════════════════════════════════════════════════════
//  ROUTER / NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

const Router = {
  navigate(page, scrollToId) {
    State.page = page;
    qsa('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
    // Reset any inline styles set by previous pages (e.g. logs sets display:flex)
    const content = qs('#content');
    content.style.display = '';
    content.style.flexDirection = '';
    Pages[page].render();
    if (scrollToId) {
      setTimeout(() => {
        const el = document.getElementById(scrollToId);
        if (el) { el.scrollIntoView({behavior:'smooth', block:'center'}); el.classList.add('highlight'); setTimeout(() => el.classList.remove('highlight'), 2000); }
      }, 200);
    }
  },

  init() {
    qsa('.nav-item').forEach(item => {
      item.addEventListener('click', () => this.navigate(item.dataset.page));
    });
  }
};

// ═══════════════════════════════════════════════════════════════════════════
//  POLLING
// ═══════════════════════════════════════════════════════════════════════════

const EventBus = {
  handlers: {},
  on(type, fn) { (this.handlers[type] = this.handlers[type]||[]).push(fn); },
  emit(type, data) { (this.handlers[type]||[]).forEach(fn => fn(data)); },

  async poll() {
    try {
      const events = await API.getEvents();
      events.forEach(e => this.emit(e.type, e.data));
    } catch(_) {}

    // Always refresh status
    try {
      const s = await API.getServerStatus();
      if (s) {
        State.serverStatus = s.status;
        State.uptime = s.uptime;
        updateStatusBar();
      }
    } catch(_) {}

    setTimeout(() => this.poll(), 1000);
  }
};

function updateStatusBar() {
  const dot  = qs('#status-dot');
  const txt  = qs('#status-text');
  const upt  = qs('#uptime-display');
  dot.className = `dot ${State.serverStatus}`;
  txt.textContent = State.serverStatus.charAt(0).toUpperCase() + State.serverStatus.slice(1);
  upt.textContent = State.uptime ? `  ${State.uptime}` : '';

  // Update dashboard buttons if visible
  if (State.page === 'dashboard') refreshDashboardButtons();
}

// ═══════════════════════════════════════════════════════════════════════════
//  PAGES
// ═══════════════════════════════════════════════════════════════════════════

const Pages = {

  // ──────────────────────────────────────────────── DASHBOARD ───
  dashboard: {
    render() {
      const c = qs('#content');
      c.innerHTML = '';
      c.appendChild(Pages.dashboard._build());
    },
    _build() {
      const frag = document.createDocumentFragment();

      // Header
      const hdr = el('div','page-header');
      hdr.innerHTML = '<div class="page-title">Dashboard</div><div class="page-subtitle">Server status and quick controls</div>';
      frag.appendChild(hdr);

      // Status card
      const statusCard = el('div','card');
      statusCard.innerHTML = `
        <div class="card-title">Server Status</div>
        <div class="big-status">
          <div class="big-dot ${State.serverStatus}" id="dash-big-dot"></div>
          <div class="big-status-text" id="dash-status-text">${State.serverStatus.charAt(0).toUpperCase()+State.serverStatus.slice(1)}</div>
          <div class="muted" id="dash-uptime" style="font-size:13px">${State.uptime ? `Uptime: ${State.uptime}` : ''}</div>
        </div>
        <div class="btn-row" style="margin-top:16px" id="dash-btn-row"></div>
        <div style="margin-top:12px;display:flex;align-items:center;gap:8px" id="dash-autoreset-row">
          <button class="toggle ${State.profile.auto_restart?'on':''}" id="dash-autorestart"></button>
          <span class="toggle-label">Auto-restart on crash</span>
        </div>`;
      frag.appendChild(statusCard);
      refreshDashboardButtons(statusCard);

      const tog = statusCard.querySelector('#dash-autorestart');
      tog.onclick = async () => {
        const nv = !tog.classList.contains('on');
        tog.classList.toggle('on', nv);
        State.profile.auto_restart = nv;
        await API.saveProfileBasic({ auto_restart: nv });
      };

      // Stats grid
      const statsCard = el('div','card');
      const p = State.profile;
      const la = p.launch_args || {};
      statsCard.innerHTML = `
        <div class="card-title">Server Info</div>
        <div class="stat-grid">
          <div class="stat-card"><div class="stat-value">${esc(p.map||'-')}</div><div class="stat-label">Map</div></div>
          <div class="stat-card"><div class="stat-value">${esc(String(la.MaxPlayers||70))}</div><div class="stat-label">Max Players</div></div>
          <div class="stat-card"><div class="stat-value">${esc(String(la.Port||7777))}</div><div class="stat-label">Game Port</div></div>
          <div class="stat-card"><div class="stat-value">${esc(String(la.QueryPort||27015))}</div><div class="stat-label">Query Port</div></div>
          <div class="stat-card"><div class="stat-value">${esc(p.game||'ase').toUpperCase()}</div><div class="stat-label">Game</div></div>
          <div class="stat-card"><div class="stat-value" id="dash-update-val">-</div><div class="stat-label">Local Build</div></div>
        </div>`;
      frag.appendChild(statsCard);

      // Update card
      const updCard = el('div','card');
      updCard.innerHTML = `
        <div class="card-title">Server Update</div>
        <div class="gap-row">
          <button class="btn btn-ghost" id="check-update-btn">Check for Updates</button>
          <span id="update-status" class="muted" style="font-size:13px"></span>
        </div>`;
      frag.appendChild(updCard);
      updCard.querySelector('#check-update-btn').onclick = async () => {
        qs('#update-status').textContent = 'Checking…';
        await API.checkUpdate();
      };

      return frag;
    }
  },

  // ──────────────────────────────────────────────── INSTALL ───
  install: {
    _logEl: null,
    render() {
      const c = qs('#content');
      c.innerHTML = '';
      c.style.display = 'flex';
      c.style.flexDirection = 'column';
      c.style.gap = '16px';

      const hdr = el('div','page-header');
      hdr.innerHTML = '<div class="page-title">Install / Update</div><div class="page-subtitle">Download and install the ARK dedicated server via SteamCMD</div>';
      c.appendChild(hdr);

      Pages.install._buildCards(c);
    },

    async _buildCards(c) {
      const info = await API.getSteamcmdInfo();
      const profile = State.profile;

      // SteamCMD card
      const sc = el('div','card');
      const hasScmd = !!(info.detected);
      sc.innerHTML = `
        <div class="card-title">SteamCMD</div>
        <div class="gap-row" style="margin-bottom:10px">
          <div style="flex:1;min-width:0">
            <input type="text" id="scmd-path" value="${esc(info.detected||info.configured||'')}" placeholder="Path to steamcmd.exe">
          </div>
          <button class="btn btn-ghost" id="scmd-browse">Browse…</button>
          <button class="btn btn-ghost" id="scmd-detect">Auto-detect</button>
        </div>
        <div id="scmd-status" class="field-hint" style="margin-bottom:10px">${hasScmd ? `<span class="text-green">✓ Found: ${esc(info.detected)}</span>` : '<span class="text-red">✗ SteamCMD not found - download it below</span>'}</div>
        <button class="btn btn-ghost" id="scmd-download">Download SteamCMD…</button>`;
      c.appendChild(sc);

      sc.querySelector('#scmd-browse').onclick = async () => {
        const p = await API.browseFile('Executable (steamcmd.exe)');
        if (p) { sc.querySelector('#scmd-path').value = p; await API.setSteamcmdPath(p); sc.querySelector('#scmd-status').innerHTML = `<span class="text-green">✓ Set: ${esc(p)}</span>`; }
      };
      sc.querySelector('#scmd-detect').onclick = async () => {
        const inf2 = await API.getSteamcmdInfo();
        if (inf2.detected) { sc.querySelector('#scmd-path').value = inf2.detected; sc.querySelector('#scmd-status').innerHTML = `<span class="text-green">✓ Found: ${esc(inf2.detected)}</span>`; await API.setSteamcmdPath(inf2.detected); }
        else toast('SteamCMD not found in common locations', 'error');
      };
      sc.querySelector('#scmd-download').onclick = async () => {
        const dir = await API.browseFolder();
        if (!dir) return;
        Pages.install._appendLog(`[Manager] Downloading SteamCMD to ${dir}…\n`);
        await API.downloadSteamcmd(dir);
      };

      // Server install card
      const si = el('div','card');
      si.innerHTML = `
        <div class="card-title">Server Installation Directory</div>
        <div class="gap-row" style="margin-bottom:10px">
          <div style="flex:1">
            <input type="text" id="install-dir" value="${esc(profile.server_install_dir||'')}" placeholder="e.g. C:\\ARKServer">
          </div>
          <button class="btn btn-ghost" id="dir-browse">Browse…</button>
        </div>
        <div class="gap-row" style="margin-bottom:10px;flex-wrap:wrap">
          <label class="field-label" style="white-space:nowrap">Game:</label>
          <select id="game-select" style="width:auto">
            <option value="ase" ${profile.game==='ase'?'selected':''}>ARK: Survival Evolved (ASE)</option>
            <option value="asa" ${profile.game==='asa'?'selected':''}>ARK: Survival Ascended (ASA)</option>
          </select>
          <label class="field-label" style="white-space:nowrap;margin-left:12px">Branch:</label>
          <select id="branch-select" style="width:auto">
            <option value="" ${!profile.branch?'selected':''}>Live (default)</option>
            <option value="experimental" ${profile.branch==='experimental'?'selected':''}>Experimental</option>
            <option value="arkpublic" ${profile.branch==='arkpublic'?'selected':''}>Public Beta</option>
            <option value="__custom__" ${profile.branch&&!['','experimental','arkpublic'].includes(profile.branch)?'selected':''}>Custom…</option>
          </select>
          <input type="text" id="branch-custom" placeholder="Branch name"
                 value="${esc(profile.branch&&!['','experimental','arkpublic'].includes(profile.branch)?profile.branch:'')}"
                 style="width:140px;${profile.branch&&!['','experimental','arkpublic'].includes(profile.branch)?'':'display:none'}">
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" id="install-btn">Install / Update Server</button>
          <button class="btn btn-ghost" id="cancel-btn" disabled>Cancel</button>
        </div>
        <div class="progress-bar-wrap" style="margin-top:12px">
          <div class="progress-bar-fill" id="install-progress" style="width:0%"></div>
        </div>`;
      c.appendChild(si);

      si.querySelector('#dir-browse').onclick = async () => {
        const d = await API.browseFolder();
        if (d) { si.querySelector('#install-dir').value = d; await API.saveProfileBasic({server_install_dir:d}); State.profile.server_install_dir=d; }
      };
      si.querySelector('#game-select').onchange = async e => { await API.saveProfileBasic({game:e.target.value}); State.profile.game=e.target.value; };
      si.querySelector('#install-dir').onchange = async e => { await API.saveProfileBasic({server_install_dir:e.target.value}); State.profile.server_install_dir=e.target.value; };
      si.querySelector('#branch-select').onchange = async e => {
        const custom = si.querySelector('#branch-custom');
        custom.style.display = e.target.value === '__custom__' ? '' : 'none';
        if (e.target.value !== '__custom__') {
          await API.saveProfileBasic({branch: e.target.value});
          State.profile.branch = e.target.value;
        }
      };
      si.querySelector('#branch-custom').onchange = async e => {
        await API.saveProfileBasic({branch: e.target.value.trim()});
        State.profile.branch = e.target.value.trim();
      };

      si.querySelector('#install-btn').onclick = async () => {
        const dir = si.querySelector('#install-dir').value;
        if (!dir) { toast('Set install directory first', 'error'); return; }
        const branchSel = si.querySelector('#branch-select');
        const branch = branchSel.value === '__custom__'
          ? si.querySelector('#branch-custom').value.trim()
          : branchSel.value;
        await API.saveProfileBasic({server_install_dir:dir, game:si.querySelector('#game-select').value, branch});
        State.profile.server_install_dir = dir;
        const r = await API.installServer();
        if (!r.ok) { toast(r.error, 'error'); return; }
        si.querySelector('#install-btn').disabled = true;
        si.querySelector('#cancel-btn').disabled = false;
        const bar = si.querySelector('#install-progress');
        bar.classList.add('indeterminate');
      };
      si.querySelector('#cancel-btn').onclick = async () => {
        await API.cancelInstall();
        si.querySelector('#install-btn').disabled = false;
        si.querySelector('#cancel-btn').disabled = true;
        si.querySelector('#install-progress').classList.remove('indeterminate');
      };

      // Import existing server card
      const ic = el('div','card');
      ic.innerHTML = `
        <div class="card-title">Import Existing Server</div>
        <div class="field-hint" style="margin-bottom:10px">Already have an ARK server installed? Select its root directory to import it into this profile. The game type will be auto-detected and GameUserSettings.ini / Game.ini will be read and written directly from its <code>Saved\\Config\\WindowsServer\\</code> folder.</div>
        <div class="gap-row">
          <div style="flex:1">
            <input type="text" id="import-dir" placeholder="e.g. C:\\ARKServer">
          </div>
          <button class="btn btn-ghost" id="import-browse">Browse…</button>
          <button class="btn btn-primary" id="import-btn">Import</button>
        </div>
        <div id="import-result" style="margin-top:8px"></div>`;
      c.appendChild(ic);

      ic.querySelector('#import-browse').onclick = async () => {
        const d = await API.browseFolder();
        if (d) ic.querySelector('#import-dir').value = d;
      };
      ic.querySelector('#import-btn').onclick = async () => {
        const dir = ic.querySelector('#import-dir').value.trim();
        if (!dir) { toast('Select a server directory first', 'error'); return; }
        const r = await API.importServer(dir);
        const res = ic.querySelector('#import-result');
        if (!r.ok) {
          res.innerHTML = `<span class="text-red">✗ ${esc(r.error)}</span>`;
          toast(r.error, 'error');
          return;
        }
        const d2 = r.data;
        const gameLabel = d2.game === 'asa' ? 'ARK: Survival Ascended' : 'ARK: Survival Evolved';
        const detectedNote = d2.game_detected ? '' : ' <span style="color:var(--yellow)">(could not detect — set manually)</span>';
        res.innerHTML = `<span class="text-green">✓ Imported</span> &nbsp;
          Game: <strong>${esc(gameLabel)}</strong>${detectedNote} &nbsp;
          GUS: ${d2.has_gus ? '<span class="text-green">found</span>' : '<span style="color:var(--yellow)">not found (will be created on first save)</span>'} &nbsp;
          Game.ini: ${d2.has_game_ini ? '<span class="text-green">found</span>' : '<span style="color:var(--yellow)">not found</span>'}`;
        State.profile.server_install_dir = d2.server_dir;
        State.profile.game = d2.game;
        // Sync the install-dir input on this page too
        const installDirInput = si.querySelector('#install-dir');
        if (installDirInput) installDirInput.value = d2.server_dir;
        const gameSelect = si.querySelector('#game-select');
        if (gameSelect) gameSelect.value = d2.game;
        toast('Server imported', 'success');
      };

      // Log card
      const lc = el('div','card');
      lc.style.flex = '1';
      lc.style.display = 'flex';
      lc.style.flexDirection = 'column';
      lc.innerHTML = `
        <div style="display:flex;align-items:center;margin-bottom:8px">
          <span class="card-title" style="margin-bottom:0">Output</span>
          <div class="btn-row ml-auto" style="gap:6px">
            <button class="btn btn-ghost" id="copy-log-btn" style="padding:4px 10px;font-size:12px">Copy</button>
            <button class="btn btn-ghost" id="clear-log-btn" style="padding:4px 10px;font-size:12px">Clear</button>
          </div>
        </div>
        <div id="install-log" style="flex:1;background:var(--bg);border:1px solid var(--bg3);border-radius:4px;padding:10px;font-family:Consolas,monospace;font-size:12px;color:var(--fg2);overflow-y:auto;min-height:200px;max-height:320px;white-space:pre-wrap;word-break:break-all;user-select:text;cursor:text"></div>`;
      c.appendChild(lc);
      Pages.install._logEl = lc.querySelector('#install-log');
      lc.querySelector('#clear-log-btn').onclick = () => { if (Pages.install._logEl) Pages.install._logEl.innerHTML = ''; };
      lc.querySelector('#copy-log-btn').onclick = () => {
        const text = Pages.install._logEl ? Pages.install._logEl.innerText : '';
        navigator.clipboard.writeText(text).then(() => toast('Log copied', 'success'), () => toast('Copy failed', 'error'));
      };
    },

    _appendLog(line) {
      if (!Pages.install._logEl) return;
      const span = document.createElement('span');
      const l = line.toLowerCase();
      if (l.includes('error') || l.includes('failed')) span.style.color = 'var(--red)';
      else if (l.includes('success') || l.includes('complete')) span.style.color = 'var(--green)';
      else if (l.includes('[manager]')) span.style.color = 'var(--purple)';
      else span.style.color = 'var(--fg3)';
      span.textContent = line;
      Pages.install._logEl.appendChild(span);
      Pages.install._logEl.scrollTop = Pages.install._logEl.scrollHeight;
    }
  },

  // ──────────────────────────────────────────────── GUS SETTINGS ───
  settings: {
    values: {},
    render() {
      const c = qs('#content');
      c.innerHTML = `
        <div class="page-header">
          <div class="page-title">GameUserSettings.ini</div>
          <div class="page-subtitle">Server configuration - all settings in one place</div>
        </div>`;

      // Toolbar
      const tb = el('div','btn-row');
      tb.style.flexWrap = 'wrap';
      tb.style.gap = '8px';
      tb.innerHTML = `
        <button class="btn btn-primary" id="gus-save">💾 Save</button>
        <button class="btn btn-ghost" id="gus-load">↓ Reload from Disk</button>
        <select id="gus-preset" style="background:var(--bg3);border:1px solid var(--bg4);color:var(--fg);padding:6px 10px;border-radius:4px;font-size:13px">
          <option value="">- Apply Preset -</option>
          ${Object.keys(GUS_PRESETS).map(k=>`<option value="${esc(k)}">${esc(k)}</option>`).join('')}
        </select>`;
      c.appendChild(tb);

      // Search bar
      const sb = el('div','settings-search-bar');
      sb.innerHTML = `<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="gus-search" placeholder="Filter settings…">`;
      c.appendChild(sb);

      // Category chips
      const chips = el('div','category-chips');
      GUS_SETTINGS.forEach(cat => {
        const ch = el('div','chip',cat.category);
        ch.onclick = () => {
          const content = document.getElementById('content');
          const target = document.getElementById(`cat-${cat.category}`);
          if (!target || !content) return;
          // offsetTop traversal up to #content (position:relative makes it an
          // offsetParent boundary). Reads natural DOM position, not visual
          // sticky position, so scrolling back up to pinned headers works.
          let top = 0, node = target;
          while (node && node !== content) { top += node.offsetTop; node = node.offsetParent; }
          content.scrollTo({ top, behavior: 'smooth' });
        };
        chips.appendChild(ch);
      });
      c.appendChild(chips);

      // Settings list
      const list = el('div','settings-list');
      list.style.background = 'var(--bg2)';
      list.style.border = '1px solid var(--bg3)';
      list.style.borderRadius = '8px';
      list.style.overflow = 'hidden';
      GUS_SETTINGS.forEach(cat => {
        const header = el('div','setting-category-header', cat.category);
        header.id = `cat-${cat.category}`;
        list.appendChild(header);
        cat.fields.forEach(f => {
          const row = this._makeRow(f);
          row.id = `gus-${f.k}`;
          row.dataset.search = `${f.l} ${f.k} ${f.h} ${cat.category}`.toLowerCase();
          list.appendChild(row);
        });
      });
      c.appendChild(list);

      // Custom settings card
      const customCard = el('div','card');
      customCard.id = 'gus-custom-card';
      customCard.innerHTML = `
        <div class="card-title">CUSTOM SETTINGS</div>
        <div class="field-hint" style="margin-bottom:10px;color:var(--fg3)">
          Add any GameUserSettings.ini key not listed above. Changes are saved with the profile.
        </div>
        <div id="custom-rows"></div>
        <button class="btn btn-ghost" id="add-custom-row" style="margin-top:8px">+ Add Custom Setting</button>`;
      c.appendChild(customCard);
      qs('#add-custom-row').onclick = () => this._addCustomRow();

      // Wire up buttons
      tb.querySelector('#gus-save').onclick = () => this.save();
      tb.querySelector('#gus-load').onclick = () => this.loadFromServer();
      tb.querySelector('#gus-preset').onchange = e => { if (e.target.value) this.applyPreset(e.target.value); e.target.value=''; };

      // Live search filter
      sb.querySelector('#gus-search').addEventListener('input', e => {
        const q = e.target.value.toLowerCase();
        qsa('.setting-row', list).forEach(row => {
          row.classList.toggle('hidden', !!q && !row.dataset.search.includes(q));
        });
        // Hide category headers if all children hidden
        qsa('.setting-category-header', list).forEach(hdr => {
          let next = hdr.nextElementSibling;
          let allHidden = true;
          while (next && !next.classList.contains('setting-category-header')) {
            if (!next.classList.contains('hidden')) allHidden = false;
            next = next.nextElementSibling;
          }
          hdr.classList.toggle('hidden', allHidden && !!q);
        });
      });

      // Load values
      API.getGusValues().then(vals => {
        this.values = vals;
        this._fillValues();
      });
    },

    _makeRow(f) {
      const row = el('div','setting-row');
      const nameCell = el('div');
      nameCell.innerHTML = `<div class="setting-name">${esc(f.l)}</div><div class="setting-key">${esc(f.k)}</div>`;

      let inputEl;
      if (f.t === 'check') {
        inputEl = makeToggle(f.d.toLowerCase() === 'true', () => {});
        inputEl.dataset.key = f.k;
        inputEl.dataset.type = 'check';
      } else {
        inputEl = document.createElement('input');
        inputEl.type = 'text';
        inputEl.value = f.d;
        inputEl.dataset.key = f.k;
        inputEl.dataset.type = 'text';
      }

      const hint = el('div','setting-hint', esc(f.h));
      row.appendChild(nameCell);
      row.appendChild(inputEl);
      row.appendChild(hint);
      return row;
    },

    _addCustomRow(section='ServerSettings', key='', value='') {
      const container = qs('#custom-rows');
      if (!container) return;
      const KNOWN_SECTIONS = ['ServerSettings', '/Script/ShooterGame.ShooterGameMode',
        '/Script/Engine.GameSession', 'SessionSettings'];
      const isKnown = KNOWN_SECTIONS.includes(section);
      const row = document.createElement('div');
      row.className = 'custom-setting-row';
      row.innerHTML = `
        <select class="custom-section">
          ${KNOWN_SECTIONS.map(s => `<option value="${esc(s)}" ${s===section&&isKnown?'selected':''}>${esc(s)}</option>`).join('')}
          <option value="__other__" ${!isKnown?'selected':''}>Other…</option>
        </select>
        <input type="text" class="custom-section-other" placeholder="Section name"
               value="${!isKnown?esc(section):''}" style="${isKnown?'display:none':''}">
        <input type="text" class="custom-key" placeholder="Key" value="${esc(key)}">
        <input type="text" class="custom-value" placeholder="Value" value="${esc(value)}">
        <button class="btn btn-ghost custom-del" title="Remove">×</button>`;
      row.querySelector('.custom-section').onchange = function() {
        const other = row.querySelector('.custom-section-other');
        other.style.display = this.value === '__other__' ? '' : 'none';
      };
      row.querySelector('.custom-del').onclick = () => row.remove();
      container.appendChild(row);
    },

    _fillValues() {
      const list = qs('.settings-list');
      if (!list) return;
      const vs = this.values;
      const sections = vs.__sections__ || {};
      // Fill known fields
      qsa('[data-key]', list).forEach(el => {
        const k = el.dataset.key;
        if (!(k in vs)) return;
        if (el.dataset.type === 'check') {
          el.classList.toggle('on', String(vs[k]).toLowerCase() === 'true');
        } else {
          el.value = vs[k];
        }
      });
      // Populate custom rows with keys not in the known GUS_SETTINGS list
      const knownKeys = new Set(GUS_SETTINGS.flatMap(cat => cat.fields.map(f => f.k)));
      const customContainer = qs('#custom-rows');
      if (customContainer) {
        customContainer.innerHTML = '';
        Object.entries(vs).forEach(([k, v]) => {
          if (k === '__sections__') return;
          if (!knownKeys.has(k)) this._addCustomRow(sections[k] || 'ServerSettings', k, v);
        });
      }
    },

    _collectValues() {
      const list = qs('.settings-list');
      const out = {};
      qsa('[data-key]', list).forEach(el => {
        if (el.dataset.type === 'check') {
          out[el.dataset.key] = el.classList.contains('on') ? 'True' : 'False';
        } else {
          out[el.dataset.key] = el.value;
        }
      });
      return out;
    },

    _collectCustom() {
      return qsa('.custom-setting-row', qs('#gus-custom-card') || document).map(row => {
        const sel = row.querySelector('.custom-section');
        const s = sel.value === '__other__'
          ? (row.querySelector('.custom-section-other').value.trim() || 'ServerSettings')
          : sel.value;
        return { s, k: row.querySelector('.custom-key').value.trim(),
                    v: row.querySelector('.custom-value').value };
      }).filter(e => e.k);
    },

    async save() {
      const vals = this._collectValues();
      const custom = this._collectCustom();
      const r = await API.saveGusValues(vals, custom);
      r.ok ? toast('GameUserSettings.ini saved to profile', 'success') : toast(r.error, 'error');
    },

    async sync() {
      await this.save();
      const r = await API.syncGusToServer();
      r.ok ? toast('Synced to server ✓', 'success') : toast(r.error, 'error');
    },

    async loadFromServer() {
      const r = await API.loadGusFromServer();
      if (!r.ok) { toast(r.error, 'error'); return; }
      const vals = await API.getGusValues();
      this.values = vals;
      this._fillValues();
      toast('Loaded from server', 'success');
    },

    applyPreset(name) {
      const preset = GUS_PRESETS[name];
      if (!preset) return;
      const list = qs('.settings-list');
      Object.entries(preset).forEach(([k,v]) => {
        const el = list.querySelector(`[data-key="${k}"]`);
        if (!el) return;
        if (el.dataset.type === 'check') el.classList.toggle('on', v.toLowerCase()==='true');
        else el.value = v;
      });
      toast(`Preset "${name}" applied - click Save to keep`, 'info');
    }
  },

  // ──────────────────────────────────────────────── GAME.INI ───
  gameini: {
    render() {
      const c = qs('#content');
      c.innerHTML = '';
      const hdr = el('div','page-header');
      hdr.innerHTML = '<div class="page-title">Game.ini</div><div class="page-subtitle">Difficulty, day/night, per-level stats, engram points</div>';
      c.appendChild(hdr);

      // Toolbar
      const tb = el('div','btn-row');
      tb.innerHTML = `
        <button class="btn btn-primary" id="gi-save">💾 Save</button>
        <button class="btn btn-ghost" id="gi-load">↓ Reload from Disk</button>`;
      c.appendChild(tb);

      const tabs = makeInnerTabs([
        { label: 'Difficulty',    render: p => this._renderDifficulty(p) },
        { label: 'Day / Night',   render: p => this._renderDayNight(p) },
        { label: 'Player Stats',  render: p => this._renderPlayerStats(p) },
        { label: 'Dino Stats',    render: p => this._renderDinoStats(p) },
        { label: 'Engram Points', render: p => this._renderEngrams(p) },
        { label: 'Raw Editor',    render: p => this._renderRaw(p) },
      ]);
      c.appendChild(tabs);

      tb.querySelector('#gi-save').onclick  = () => this.save();
      tb.querySelector('#gi-load').onclick  = () => this.loadFromServer();

      API.getGameIniValues().then(v => this._fillValues(v));
      API.getGameIniText().then(t => { const ta = document.getElementById('gi-raw'); if (ta) ta.value = t; });
    },

    _renderDifficulty(p) {
      p.innerHTML = `
        <div class="settings-list" style="background:var(--bg2);border:1px solid var(--bg3);border-radius:8px;overflow:hidden">
          ${this._infoRow('Use <b>Override Official Difficulty</b> for precise control. After changing, send <code>destroywilddinos</code> via RCON.')}
          ${this._sRow('gi-OverrideOfficialDifficulty','Override Official Difficulty','5.0','Max dino level = value × 30 &nbsp;(5.0 → L150 &nbsp;|&nbsp; 6.0 → L180 &nbsp;|&nbsp; 8.0 → L240)',true)}
          ${this._sRow('gi-DifficultyOffset','Difficulty Offset','0.2','0.2 = up to L60, 1.0 = up to L30 - usually leave this alone when using Override above')}
          ${this._sRow('gi-MaxTamedDinos','Max Tamed Dinos (server-wide)','5000','Total tamed creatures allowed on the entire server at once')}
          ${this._sRow('gi-MaxPersonalTamedDinos','Max Personal Tamed Dinos','500','Maximum tamed creatures per tribe')}
          ${this._sRow('gi-DinoCountMultiplier','Wild Dino Count Multiplier','1.0','Scales the number of wild creatures spawned on the map')}
        </div>`;
    },

    _renderDayNight(p) {
      p.innerHTML = `
        <div class="settings-list" style="background:var(--bg2);border:1px solid var(--bg3);border-radius:8px;overflow:hidden">
          ${this._infoRow('Example - Long days, short nights: Day Cycle=1.0 &nbsp;|&nbsp; Daytime=0.5 &nbsp;|&nbsp; Nighttime=2.0')}
          ${this._sRow('gi-DayCycleSpeedScale','Day Cycle Speed','1.0','Overall speed of the entire day/night cycle (2.0 = days pass twice as fast overall)')}
          ${this._sRow('gi-DayTimeSpeedScale','Daytime Speed','1.0','Relative speed of daytime only - higher = shorter days')}
          ${this._sRow('gi-NightTimeSpeedScale','Nighttime Speed','1.0','Relative speed of nighttime only - higher = shorter nights')}
        </div>`;
    },

    _renderPlayerStats(p) {
      const rows = STAT_NAMES.map((name,i) => `
        <tr>
          <td>${esc(name)}</td>
          <td><input type="text" id="ps-${i}" value="1.0" style="width:90px"></td>
          <td><input type="text" id="pb-${i}" value="1.0" style="width:90px"></td>
        </tr>`).join('');
      p.innerHTML = `
        <div style="color:var(--fg3);font-size:12.5px;margin-bottom:10px">
          Per-level multiplier applied when a player spends a stat point. 1.0 = default. Base = the stat at level 1.
        </div>
        <div style="overflow-x:auto">
          <table class="stat-input-table">
            <thead><tr><th>Stat</th><th>Per Level Mult.</th><th>Base Stat Mult.</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>`;
    },

    _renderDinoStats(p) {
      const rows = STAT_NAMES.map((name,i) => `
        <tr>
          <td>${esc(name)}</td>
          <td><input type="text" id="ds-${i}" value="1.0" style="width:90px"></td>
          <td><input type="text" id="da-${i}" value="1.0" style="width:90px"></td>
        </tr>`).join('');
      p.innerHTML = `
        <div style="color:var(--fg3);font-size:12.5px;margin-bottom:10px">
          Per-level stat multipliers for tamed dinos. Add = raw stat gained per level-up. Affinity = imprint bonus (usually 1.0).
        </div>
        <div style="overflow-x:auto">
          <table class="stat-input-table">
            <thead><tr><th>Stat</th><th>Tamed Add / Level</th><th>Tamed Affinity</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>`;
    },

    _renderEngrams(p) {
      const cells = Array.from({length:180},(_,i) => `
        <div class="engram-cell">
          <span class="engram-lbl">L${i+1}</span>
          <input type="text" id="ep-${i}" placeholder="-" style="width:52px">
        </div>`).join('');
      p.innerHTML = `
        <div class="gap-row" style="margin-bottom:12px;flex-wrap:wrap">
          <span style="color:var(--fg2);font-size:13px">Quick fill - all levels:</span>
          <input type="text" id="ep-quick" value="30" style="width:70px">
          <span style="color:var(--fg3);font-size:13px">pts/level</span>
          <button class="btn btn-ghost" id="ep-fill" style="padding:5px 10px;font-size:12px">Apply</button>
          <button class="btn btn-ghost" id="ep-clear" style="padding:5px 10px;font-size:12px">Clear (use defaults)</button>
        </div>
        <div class="engram-grid">${cells}</div>`;
      p.querySelector('#ep-fill').onclick = () => {
        const v = p.querySelector('#ep-quick').value;
        Array.from({length:180},(_,i) => { const el=document.getElementById(`ep-${i}`); if(el) el.value=v; });
      };
      p.querySelector('#ep-clear').onclick = () => {
        Array.from({length:180},(_,i) => { const el=document.getElementById(`ep-${i}`); if(el) el.value=''; });
      };
    },

    _renderRaw(p) {
      p.innerHTML = `
        <div class="gap-row" style="margin-bottom:8px">
          <button class="btn btn-ghost" id="gi-pull-raw" style="font-size:12px">Pull from Forms → Raw</button>
          <span style="color:var(--fg3);font-size:12px">Or edit the raw text directly and save.</span>
        </div>
        <textarea id="gi-raw" class="raw-editor" style="min-height:400px;max-height:500px"></textarea>`;
      p.querySelector('#gi-pull-raw').onclick = () => {
        const vals = this._collectValues();
        const lines = ['/script/shootergame.shootergamemode\n'];
        Object.entries(vals).forEach(([k,v]) => {
          if (k !== '_engram_points') lines.push(`${k}=${v}`);
        });
        if (vals._engram_points) vals._engram_points.forEach(pt => lines.push(`OverridePlayerLevelEngramPoints=${pt}`));
        document.getElementById('gi-raw').value = `[/script/shootergame.shootergamemode]\n` + lines.slice(1).join('\n');
      };
    },

    _sRow(id, label, def, hint, highlight=false) {
      return `<div class="setting-row" id="${id}">
        <div><div class="setting-name${highlight?' text-accent':''}"><b>${esc(label)}</b></div></div>
        <input type="text" data-gi="${id}" value="${esc(def)}" style="width:120px">
        <div class="setting-hint">${hint}</div>
      </div>`;
    },

    _infoRow(html) {
      return `<div style="padding:10px 16px;font-size:12.5px;color:var(--yellow);background:rgba(249,226,175,.06);border-bottom:1px solid var(--bg3)">ℹ ${html}</div>`;
    },

    _fillValues(v) {
      const map = {
        'gi-OverrideOfficialDifficulty': 'OverrideOfficialDifficulty',
        'gi-DifficultyOffset': 'DifficultyOffset',
        'gi-MaxTamedDinos': 'MaxTamedDinos',
        'gi-MaxPersonalTamedDinos': 'MaxPersonalTamedDinos',
        'gi-DinoCountMultiplier': 'DinoCountMultiplier',
        'gi-DayCycleSpeedScale': 'DayCycleSpeedScale',
        'gi-DayTimeSpeedScale': 'DayTimeSpeedScale',
        'gi-NightTimeSpeedScale': 'NightTimeSpeedScale',
      };
      Object.entries(map).forEach(([id,k]) => {
        const el = document.querySelector(`[data-gi="${id}"]`);
        if (el && k in v) el.value = v[k];
      });
      STAT_NAMES.forEach((_,i) => {
        const ps = document.getElementById(`ps-${i}`); if(ps && `PerLevelStatsMultiplier_Player[${i}]` in v) ps.value=v[`PerLevelStatsMultiplier_Player[${i}]`];
        const pb = document.getElementById(`pb-${i}`);  if(pb && `PlayerBaseStatMultipliers[${i}]` in v) pb.value=v[`PlayerBaseStatMultipliers[${i}]`];
        const ds = document.getElementById(`ds-${i}`); if(ds && `PerLevelStatsMultiplier_DinoTamed_Add[${i}]` in v) ds.value=v[`PerLevelStatsMultiplier_DinoTamed_Add[${i}]`];
        const da = document.getElementById(`da-${i}`); if(da && `PerLevelStatsMultiplier_DinoTamed_Affinity[${i}]` in v) da.value=v[`PerLevelStatsMultiplier_DinoTamed_Affinity[${i}]`];
      });
      if (v._engram_points) v._engram_points.forEach((pt,i) => { const el=document.getElementById(`ep-${i}`); if(el) el.value=pt; });
    },

    _collectValues() {
      const out = {};
      const map = { 'gi-OverrideOfficialDifficulty':'OverrideOfficialDifficulty','gi-DifficultyOffset':'DifficultyOffset','gi-MaxTamedDinos':'MaxTamedDinos','gi-MaxPersonalTamedDinos':'MaxPersonalTamedDinos','gi-DinoCountMultiplier':'DinoCountMultiplier','gi-DayCycleSpeedScale':'DayCycleSpeedScale','gi-DayTimeSpeedScale':'DayTimeSpeedScale','gi-NightTimeSpeedScale':'NightTimeSpeedScale' };
      qsa('[data-gi]').forEach(el => { const k=map[el.dataset.gi]; if(k) out[k]=el.value; });
      STAT_NAMES.forEach((_,i) => {
        const ps=document.getElementById(`ps-${i}`); if(ps) out[`PerLevelStatsMultiplier_Player[${i}]`]=ps.value;
        const pb=document.getElementById(`pb-${i}`);  if(pb) out[`PlayerBaseStatMultipliers[${i}]`]=pb.value;
        const ds=document.getElementById(`ds-${i}`); if(ds) out[`PerLevelStatsMultiplier_DinoTamed_Add[${i}]`]=ds.value;
        const da=document.getElementById(`da-${i}`); if(da) out[`PerLevelStatsMultiplier_DinoTamed_Affinity[${i}]`]=da.value;
      });
      out._engram_points = Array.from({length:180},(_,i)=>{ const e=document.getElementById(`ep-${i}`); return e?e.value:''; }).filter(v=>v.trim());
      return out;
    },

    async save() {
      const raw = document.getElementById('gi-raw');
      if (raw && raw.value.trim()) { const r=await API.saveGameIniText(raw.value); if(!r.ok){toast(r.error,'error');return;} }
      else { const r=await API.saveGameIniValues(this._collectValues()); if(!r.ok){toast(r.error,'error');return;} }
      toast('Game.ini saved to profile', 'success');
    },

    async sync() {
      await this.save();
      const r = await API.syncGameIniToServer();
      r.ok ? toast('Game.ini synced to server ✓', 'success') : toast(r.error, 'error');
    },

    async loadFromServer() {
      const r = await API.loadGameIniFromServer();
      if (!r.ok) { toast(r.error,'error'); return; }
      const [vals, txt] = await Promise.all([API.getGameIniValues(), API.getGameIniText()]);
      this._fillValues(vals);
      const ta=document.getElementById('gi-raw'); if(ta) ta.value=txt;
      toast('Loaded from server', 'success');
    }
  },

  // ──────────────────────────────────────────────── LAUNCH ARGS ───
  launch: {
    flagStates: {},
    render() {
      const c = qs('#content');
      c.innerHTML = '';
      const hdr = el('div','page-header');
      hdr.innerHTML = '<div class="page-title">Launch Arguments</div><div class="page-subtitle">Command-line options for the server executable</div>';
      c.appendChild(hdr);

      const tb = el('div','btn-row');
      tb.innerHTML = `<button class="btn btn-primary" id="la-save">💾 Save</button><button class="btn btn-ghost" id="la-reset">Reset Defaults</button>`;
      c.appendChild(tb);

      const tabs = makeInnerTabs([
        { label: 'Basic',        render: p => this._renderBasic(p) },
        { label: 'Launch Flags', render: p => this._renderFlags(p) },
        { label: 'Cluster',      render: p => this._renderCluster(p) },
        { label: 'Preview',      render: p => this._renderPreview(p) },
      ]);
      c.appendChild(tabs);

      tb.querySelector('#la-save').onclick  = () => this.save();
      tb.querySelector('#la-reset').onclick = () => this.reset();

      this._loadValues();
    },

    _renderBasic(p) {
      const la = State.profile.launch_args || {};
      const game = State.profile.game || 'ase';
      const maps = game === 'asa' ? MAPS_ASA : MAPS_ASE;
      p.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:4px 0">
          <div class="card">
            <div class="card-title">Map</div>
            <div class="field" style="margin-bottom:10px">
              <label class="field-label">Game</label>
              <select id="la-game">
                <option value="ase" ${game==='ase'?'selected':''}>ARK: Survival Evolved (ASE)</option>
                <option value="asa" ${game==='asa'?'selected':''}>ARK: Survival Ascended (ASA)</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Map</label>
              <select id="la-map">${maps.map(m=>`<option value="${m}" ${(State.profile.map||'TheIsland')===m?'selected':''}>${m}</option>`).join('')}</select>
            </div>
            <div class="field" style="margin-top:8px">
              <label class="field-label">Custom Map Name (overrides above)</label>
              <input type="text" id="la-custommap" placeholder="Leave blank to use dropdown">
            </div>
          </div>
          <div class="card">
            <div class="card-title">Connection</div>
            ${['Port:Game Port (UDP):7777','QueryPort:Steam Query Port (UDP):27015','MaxPlayers:Max Players:70','RCONPort:RCON Port (TCP):27020'].map(s=>{
              const [k,l,d]=s.split(':');
              return `<div class="field" style="margin-bottom:8px"><label class="field-label">${l}</label><input type="text" id="la-${k}" value="${esc(String(la[k]||d))}"></div>`;
            }).join('')}
            <div style="display:flex;align-items:center;gap:8px;margin-top:4px">
              <button class="toggle ${la.RCONEnabled!==false?'on':''}" id="la-rcon-toggle"></button>
              <span class="toggle-label">Enable RCON</span>
            </div>
          </div>
          <div class="card">
            <div class="card-title">Optional</div>
            <div class="field" style="margin-bottom:8px">
              <label class="field-label">Bind IP (MULTIHOME)</label>
              <input type="text" id="la-multihome" value="${esc(la.MultihomeIP||'')}" placeholder="Leave blank for all interfaces">
            </div>
            <div class="field" style="margin-bottom:8px">
              <label class="field-label">Active Event</label>
              <select id="la-event">${EVENTS.map(e=>`<option value="${e}" ${(la.ActiveEvent||'None')===e?'selected':''}>${e}</option>`).join('')}</select>
            </div>
            <div class="field">
              <label class="field-label">Auto-Restart RAM Limit (GB)</label>
              <input type="text" id="la-gbram" value="${esc(la.GBUsageToForceRestart||'')}" placeholder="Leave blank to disable">
            </div>
          </div>
          <div class="card">
            <div class="card-title">Server Passwords</div>
            <div class="field" style="margin-bottom:8px">
              <label class="field-label">Server Name (SessionName)</label>
              <input type="text" id="la-servername" value="${esc(la.ServerName||'')}">
            </div>
            <div class="field" style="margin-bottom:8px">
              <label class="field-label">Join Password</label>
              <input type="text" id="la-serverpw" value="${esc(la.ServerPassword||'')}">
            </div>
            <div class="field">
              <label class="field-label">Admin Password</label>
              <input type="text" id="la-adminpw" value="${esc(la.ServerAdminPassword||'')}">
            </div>
          </div>
        </div>`;

      p.querySelector('#la-game').onchange = () => {
        const g = p.querySelector('#la-game').value;
        const maps2 = g === 'asa' ? MAPS_ASA : MAPS_ASE;
        const sel = p.querySelector('#la-map');
        sel.innerHTML = maps2.map(m=>`<option value="${m}">${m}</option>`).join('');
        this._updatePreview();
      };
      p.querySelectorAll('input,select').forEach(el => el.addEventListener('input', () => this._updatePreview()));
      p.querySelector('#la-rcon-toggle').addEventListener('click', () => this._updatePreview());
    },

    _renderFlags(p) {
      const la = State.profile.launch_args || {};
      const activeFlags = new Set(la.flags || ['-log','-NoBattlEye']);
      this.flagStates = {};

      const cats = {};
      LAUNCH_FLAGS.forEach(f => (cats[f.cat] = cats[f.cat]||[]).push(f));

      p.innerHTML = '';
      const list = el('div','settings-list');
      list.style.cssText = 'background:var(--bg2);border:1px solid var(--bg3);border-radius:8px;overflow:hidden';

      // per-page search
      const sb = el('div','settings-search-bar');
      sb.style.borderRadius = '8px 8px 0 0';
      sb.innerHTML = `<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="flag-search" placeholder="Filter flags…">`;
      p.appendChild(sb);
      p.appendChild(list);

      Object.entries(cats).forEach(([cat, items]) => {
        const hdr = el('div','setting-category-header', cat);
        hdr.dataset.catHeader = cat;
        list.appendChild(hdr);
        items.forEach(f => {
          const on = activeFlags.has(f.f);
          this.flagStates[f.f] = on;
          const row = el('div','setting-row');
          row.id = `flag-${f.f.replace(/\W/g,'_')}`;
          row.dataset.search = `${f.l} ${f.f} ${f.d} ${cat}`.toLowerCase();
          const tog = makeToggle(on, nv => { this.flagStates[f.f]=nv; this._updatePreview(); });
          tog.dataset.flag = f.f;
          const left = el('div');
          left.innerHTML = `<div class="setting-name">${esc(f.l)}</div><div class="setting-key">${esc(f.f)}</div>`;
          row.appendChild(left);
          row.appendChild(tog);
          row.appendChild(el('div','setting-hint',esc(f.d)));
          list.appendChild(row);
        });
      });

      sb.querySelector('#flag-search').addEventListener('input', e => {
        const q = e.target.value.toLowerCase();
        qsa('.setting-row', list).forEach(r => r.classList.toggle('hidden', !!q && !r.dataset.search.includes(q)));
        qsa('.setting-category-header', list).forEach(hdr => {
          let next=hdr.nextElementSibling; let all=true;
          while(next && !next.classList.contains('setting-category-header')){ if(!next.classList.contains('hidden'))all=false; next=next.nextElementSibling; }
          hdr.classList.toggle('hidden', all && !!q);
        });
      });
    },

    _renderCluster(p) {
      const la = State.profile.launch_args || {};
      p.innerHTML = `
        <div class="card" style="max-width:580px">
          <div class="card-title">Cluster Configuration</div>
          <div style="color:var(--fg3);font-size:12.5px;margin-bottom:14px">
            Cluster settings allow players to transfer characters, items, and dinos between servers.<br>
            All servers in a cluster must share the same Cluster ID. Leave blank for standalone.
          </div>
          <div class="field" style="margin-bottom:12px">
            <label class="field-label">Cluster ID</label>
            <input type="text" id="la-clusterid" value="${esc(la.ClusterId||'')}" placeholder="Unique name shared by all cluster servers">
          </div>
          <div class="field">
            <label class="field-label">Cluster Save Directory Override</label>
            <div class="gap-row">
              <input type="text" id="la-clusterdir" value="${esc(la.ClusterDirOverride||'')}" placeholder="Full path to shared cluster save folder" style="flex:1">
              <button class="btn btn-ghost" id="la-clusterdir-browse">Browse…</button>
            </div>
          </div>
        </div>`;
      p.querySelector('#la-clusterdir-browse').onclick = async () => {
        const d = await API.browseFolder();
        if (d) p.querySelector('#la-clusterdir').value = d;
      };
      p.querySelectorAll('input').forEach(el => el.addEventListener('input', () => this._updatePreview()));
    },

    _renderPreview(p) {
      p.innerHTML = `
        <div class="card">
          <div style="display:flex;align-items:center;margin-bottom:8px">
            <span class="card-title" style="margin-bottom:0">Full Launch Command</span>
            <button class="btn btn-ghost ml-auto" id="la-copy" style="font-size:12px;padding:4px 10px">Copy</button>
          </div>
          <textarea id="la-preview" style="background:var(--bg);border:1px solid var(--bg3);border-radius:4px;font-family:Consolas,monospace;font-size:12.5px;color:var(--accent);padding:12px;width:100%;height:120px;resize:none" readonly></textarea>
        </div>`;
      p.querySelector('#la-copy').onclick = () => {
        const txt = document.getElementById('la-preview')?.value;
        if (txt) navigator.clipboard.writeText(txt).then(()=>toast('Copied!','success'));
      };
      this._updatePreview();
    },

    _collectData() {
      const la = {};
      ['Port','QueryPort','MaxPlayers','RCONPort','ServerName','ServerPassword','ServerAdminPassword'].forEach(k => {
        const el = document.getElementById(`la-${k}`);
        if (el) la[k] = el.value;
      });
      la.MultihomeIP         = document.getElementById('la-multihome')?.value || '';
      la.GBUsageToForceRestart = document.getElementById('la-gbram')?.value || '';
      la.ActiveEvent         = document.getElementById('la-event')?.value || 'None';
      la.ClusterId           = document.getElementById('la-clusterid')?.value || '';
      la.ClusterDirOverride  = document.getElementById('la-clusterdir')?.value || '';
      la.RCONEnabled         = document.getElementById('la-rcon-toggle')?.classList.contains('on') !== false;
      la.flags               = Object.entries(this.flagStates).filter(([,v])=>v).map(([k])=>k);
      la.game                = document.getElementById('la-game')?.value || 'ase';
      la.map                 = document.getElementById('la-custommap')?.value.trim() || document.getElementById('la-map')?.value || 'TheIsland';
      return la;
    },

    _buildArgs(la, game, map) {
      const parts = [map, '?listen'];
      if (la.MaxPlayers) parts.push(`?MaxPlayers=${la.MaxPlayers}`);
      if (la.Port)       parts.push(`?Port=${la.Port}`);
      if (la.QueryPort)  parts.push(`?QueryPort=${la.QueryPort}`);
      if (la.ServerName) parts.push(`?SessionName=${la.ServerName}`);
      if (la.ServerPassword) parts.push(`?ServerPassword=${la.ServerPassword}`);
      if (la.ServerAdminPassword) parts.push(`?ServerAdminPassword=${la.ServerAdminPassword}`);
      if (la.RCONEnabled !== false) { parts.push('?RCONEnabled=True'); if (la.RCONPort) parts.push(`?RCONPort=${la.RCONPort}`); }
      if (la.ClusterId) parts.push(`?AltSaveDirectoryName=${la.ClusterId}`);
      const args = [parts.join('?')];
      (la.flags||[]).forEach(f => args.push(f.startsWith('-')?f:`-${f}`));
      if (la.ClusterDirOverride) args.push(`-ClusterDirOverride=${la.ClusterDirOverride}`);
      if (la.MultihomeIP) args.push(`-MULTIHOME=${la.MultihomeIP}`);
      if (la.GBUsageToForceRestart) args.push(`-GBUsageToForceRestart=${la.GBUsageToForceRestart}`);
      if (la.ActiveEvent && la.ActiveEvent !== 'None') args.push(`-ActiveEvent=${la.ActiveEvent}`);
      const exe = game === 'asa' ? 'ArkAscendedServer.exe' : 'ShooterGameServer.exe';
      return `${exe} ${args.join(' ')}`;
    },

    _updatePreview() {
      const la = this._collectData();
      const game = la.game || 'ase';
      const map  = la.map  || 'TheIsland';
      const cmd  = this._buildArgs(la, game, map);
      const prev = document.getElementById('la-preview');
      if (prev) prev.value = cmd;
    },

    async _loadValues() {
      const la = State.profile.launch_args || {};
      // Flag states already set during _renderFlags
    },

    async save() {
      const la = this._collectData();
      const game = la.game; const map = la.map;
      delete la.game; delete la.map;
      await API.saveProfileBasic({ game, map });
      await API.saveLaunchArgs(la);
      State.profile.launch_args = la;
      State.profile.game = game;
      State.profile.map  = map;
      toast('Launch arguments saved', 'success');
    },

    reset() {
      const defaults = { MaxPlayers:70, Port:7777, QueryPort:27015, RCONPort:27020,
                          RCONEnabled:true, flags:['-log','-NoBattlEye'] };
      State.profile.launch_args = defaults;
      Pages.launch.render();
    }
  },

  // ──────────────────────────────────────────────── MODS ───
  mods: {
    render() {
      const c = qs('#content');
      c.innerHTML = `
        <div class="page-header">
          <div class="page-title">Mods</div>
          <div class="page-subtitle">Workshop mods installed on this server profile</div>
        </div>`;
      this._renderCards(c);
    },

    async _renderCards(c) {
      const mods = await API.getMods();

      const listCard = el('div','card');
      listCard.innerHTML = `
        <div style="display:flex;align-items:center;margin-bottom:12px">
          <span class="card-title" style="margin-bottom:0">Installed Mods (${mods.length})</span>
          <div class="btn-row ml-auto">
            <button class="btn btn-ghost" id="mods-refresh" style="font-size:12px;padding:5px 10px">Refresh</button>
            <button class="btn btn-warning" id="mods-update-all" style="font-size:12px;padding:5px 10px">Update All</button>
          </div>
        </div>
        <div style="overflow-x:auto">
          <table class="data-table" id="mods-table">
            <thead><tr><th>On</th><th>Mod ID</th><th>Name</th><th>Actions</th></tr></thead>
            <tbody>${mods.length ? mods.map(m => `
              <tr>
                <td><button class="toggle ${m.enabled?'on':''}" data-toggle-mod="${esc(m.id)}"></button></td>
                <td class="mono">${esc(m.id)}</td>
                <td>${esc(m.name||m.id)}</td>
                <td><button class="btn btn-ghost" data-remove-mod="${esc(m.id)}" style="font-size:12px;padding:4px 8px;color:var(--red)">Remove</button></td>
              </tr>`).join('') : '<tr><td colspan="4" class="muted" style="text-align:center;padding:20px">No mods installed</td></tr>'}
          </tbody></table>
        </div>`;
      c.appendChild(listCard);

      listCard.querySelector('#mods-refresh').onclick = () => Pages.mods.render();
      listCard.querySelector('#mods-update-all').onclick = () => Pages.mods._updateAll(mods);
      listCard.querySelectorAll('[data-toggle-mod]').forEach(b => b.onclick = async () => { await API.toggleMod(b.dataset.toggleMod); Pages.mods.render(); });
      listCard.querySelectorAll('[data-remove-mod]').forEach(b => b.onclick = async () => {
        const ok = await confirm('Remove Mod', `Remove mod ${b.dataset.removeMod} from profile? (Files on disk are NOT deleted.)`);
        if (ok) { await API.removeMod(b.dataset.removeMod); Pages.mods.render(); }
      });

      const addCard = el('div','card');
      addCard.innerHTML = `
        <div class="card-title">Add Mod from Workshop</div>
        <div class="gap-row" style="margin-bottom:8px">
          <input type="text" id="mod-id-input" placeholder="Workshop ID (e.g. 731604991)" style="width:220px">
          <button class="btn btn-ghost" id="mod-fetch">Fetch Info</button>
        </div>
        <div id="mod-info" style="font-size:13px;color:var(--fg3);margin-bottom:10px"></div>
        <button class="btn btn-primary" id="mod-install">Install Mod</button>`;
      c.appendChild(addCard);

      addCard.querySelector('#mod-fetch').onclick = async () => {
        const id = addCard.querySelector('#mod-id-input').value.trim();
        if (!id) return;
        addCard.querySelector('#mod-info').textContent = 'Fetching…';
        const info = await API.fetchModInfo(id);
        addCard.querySelector('#mod-info').textContent = info ? `${info.title}` : 'Could not fetch info';
      };

      addCard.querySelector('#mod-install').onclick = async () => {
        const id = addCard.querySelector('#mod-id-input').value.trim();
        if (!id) { toast('Enter a Workshop mod ID', 'error'); return; }
        const r = await API.installMod(id);
        r.ok ? toast(`Installing mod ${id}… (check Logs tab for progress)`, 'info') : toast(r.error, 'error');
      };

      const logCard = el('div','card');
      logCard.innerHTML = `<div class="card-title">Install Output</div><div id="mod-log" style="font-family:Consolas,monospace;font-size:12px;color:var(--fg3);background:var(--bg);border:1px solid var(--bg3);border-radius:4px;padding:10px;max-height:200px;overflow-y:auto;white-space:pre-wrap"></div>`;
      c.appendChild(logCard);
    },

    async _updateAll(mods) {
      const enabled = mods.filter(m=>m.enabled);
      if (!enabled.length) { toast('No enabled mods to update','info'); return; }
      for (const m of enabled) {
        toast(`Installing mod ${m.id}…`, 'info');
        await API.installMod(m.id);
      }
    }
  },

  // ──────────────────────────────────────────────── LOGS ───
  logs: {
    _autoscroll: true,
    render() {
      const c = qs('#content');
      c.style.display = 'flex';
      c.style.flexDirection = 'column';
      c.innerHTML = `
        <div class="page-header">
          <div class="page-title">Server Logs</div>
          <div class="page-subtitle">Live output and historical log files</div>
        </div>
        <div class="btn-row" style="flex-shrink:0">
          <button class="toggle on" id="log-autoscroll" title="Auto-scroll"></button>
          <span class="toggle-label">Auto-scroll</span>
          <input type="text" id="log-search" placeholder="Search log…" style="width:200px;margin-left:16px">
          <span id="log-search-count" class="muted" style="font-size:12px"></span>
          <button class="btn btn-ghost ml-auto" id="log-clear" style="font-size:12px;padding:5px 10px">Clear</button>
          <select id="log-file-select" style="background:var(--bg3);border:1px solid var(--bg4);color:var(--fg);padding:5px 10px;border-radius:4px;font-size:13px">
            <option value="">Live</option>
          </select>
          <button class="btn btn-ghost" id="log-open-folder" style="font-size:12px;padding:5px 10px">Open Folder</button>
        </div>
        <div id="log-output" style="flex:1;min-height:0"></div>`;

      const tog = qs('#log-autoscroll');
      tog.onclick = () => { Pages.logs._autoscroll = tog.classList.contains('on'); };

      qs('#log-clear').onclick = () => { qs('#log-output').innerHTML = ''; };
      qs('#log-open-folder').onclick = async () => {
        const d = (await API.call('get_manager_dir')).data;
        API.openFolder(d + '/logs');
      };

      qs('#log-search').addEventListener('input', e => Pages.logs._searchLog(e.target.value));

      qs('#log-file-select').onchange = async e => {
        const fn = e.target.value;
        if (!fn) { Pages.logs._startLive(); return; }
        const text = await API.getLogFileContent(fn);
        const out = qs('#log-output');
        out.innerHTML = '';
        text.split('\n').forEach(line => Pages.logs._appendLine(line));
      };

      API.getLogFiles().then(files => {
        const sel = qs('#log-file-select');
        files.forEach(f => { const o=document.createElement('option'); o.value=f; o.textContent=f; sel.appendChild(o); });
      });

      // Load existing buffer then start polling for new lines
      API.getLogLines(500).then(lines => {
        Pages.logs._lineCount = lines.length;
        lines.forEach(l => Pages.logs._appendLine(l));
      });
      Pages.logs._startLive();
    },

    _lineCount: 0,
    _liveTimer: null,
    _startLive() {
      clearTimeout(Pages.logs._liveTimer);
      Pages.logs._liveTimer = setTimeout(async function poll() {
        if (State.page !== 'logs') return;  // stop when navigated away
        const lines = await API.getLogLines(2000);
        const newLines = lines.slice(Pages.logs._lineCount);
        newLines.forEach(l => Pages.logs._appendLine(l));
        Pages.logs._lineCount = lines.length;
        Pages.logs._liveTimer = setTimeout(poll, 1000);
      }, 1000);
    },

    _appendLine(line) {
      if (!line) return;
      const out = qs('#log-output');
      if (!out) return;
      const span = document.createElement('span');
      const l = line.toLowerCase();
      if (l.startsWith('[ark]')) span.className='log-default';
      else if (l.includes('[manager]')||l.includes('[steamcmd]')||l.includes('[mods]')) span.className='log-manager';
      else if (l.includes('error')||l.includes('fatal')||l.includes('exception')) span.className='log-error';
      else if (l.includes('warning')||l.includes('warn')) span.className='log-warning';
      else if (l.includes('join')||l.includes('connected')) span.className='log-success';
      else if (l.includes('server is listening')) span.className='log-info';
      else span.className='log-default';
      span.textContent = line.endsWith('\n') ? line : line + '\n';
      out.appendChild(span);
      if (Pages.logs._autoscroll) out.scrollTop = out.scrollHeight;
    },

    _searchLog(q) {
      const out = qs('#log-output');
      if (!out) return;
      qsa('mark', out).forEach(m => { const t=document.createTextNode(m.textContent); m.parentNode.replaceChild(t,m); });
      out.normalize();
      if (!q) { qs('#log-search-count').textContent=''; return; }
      let count=0;
      const walker = document.createTreeWalker(out, NodeFilter.SHOW_TEXT);
      const toWrap = [];
      while(walker.nextNode()) {
        const node = walker.currentNode;
        if (node.textContent.toLowerCase().includes(q.toLowerCase())) toWrap.push(node);
      }
      toWrap.forEach(node => {
        const html = esc(node.textContent).replace(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi'), `<mark>$1</mark>`);
        const wrap = document.createElement('span');
        wrap.innerHTML = html;
        node.parentNode.replaceChild(wrap, node);
        count += wrap.querySelectorAll('mark').length;
      });
      qs('#log-search-count').textContent = `${count} match${count!==1?'es':''}`;
    }
  },

  // ──────────────────────────────────────────────── BACKUPS ───
  backups: {
    selected: null,
    render() {
      const c = qs('#content');
      c.innerHTML = `
        <div class="page-header">
          <div class="page-title">Backups</div>
          <div class="page-subtitle">Save and restore your server's world data</div>
        </div>`;
      this._renderCards(c);
    },

    async _renderCards(c) {
      const profile = State.profile;
      const bk = profile.backup || {};
      const backups = await API.getBackups();

      const schedCard = el('div','card');
      schedCard.innerHTML = `
        <div class="card-title">Scheduled Backups</div>
        <div class="gap-row" style="flex-wrap:wrap;margin-bottom:10px">
          <button class="toggle ${bk.enabled?'on':''}" id="bk-enabled"></button>
          <span class="toggle-label">Auto-backup every</span>
          <input type="text" id="bk-interval" value="${bk.interval_minutes||60}" style="width:60px">
          <span class="toggle-label">minutes &nbsp; - keep last</span>
          <input type="text" id="bk-keep" value="${bk.keep_count||10}" style="width:60px">
          <span class="toggle-label">backups</span>
          <button class="btn btn-primary" id="bk-apply" style="margin-left:8px">Apply Schedule</button>
        </div>`;
      c.appendChild(schedCard);
      schedCard.querySelector('#bk-apply').onclick = async () => {
        const r = await API.applyBackupSchedule({
          enabled: schedCard.querySelector('#bk-enabled').classList.contains('on'),
          interval_minutes: parseInt(schedCard.querySelector('#bk-interval').value)||60,
          keep_count: parseInt(schedCard.querySelector('#bk-keep').value)||10,
        });
        r.ok ? toast('Backup schedule applied','success') : toast(r.error,'error');
      };

      const listCard = el('div','card');
      listCard.innerHTML = `
        <div style="display:flex;align-items:center;margin-bottom:12px">
          <span class="card-title" style="margin-bottom:0">Backup List</span>
          <div class="btn-row ml-auto">
            <button class="btn btn-primary" id="bk-create">Create Backup Now</button>
            <button class="btn btn-ghost" id="bk-restore">Restore Selected</button>
            <button class="btn btn-danger" id="bk-delete">Delete Selected</button>
            <button class="btn btn-ghost" id="bk-folder">Open Folder</button>
          </div>
        </div>
        <table class="data-table" id="bk-table">
          <thead><tr><th>Date / Time</th><th>Label</th><th>Size</th></tr></thead>
          <tbody>${backups.length ? backups.map(b=>`<tr data-path="${esc(b.path)}"><td>${esc(b.timestamp)}</td><td><span class="badge badge-gray">${esc(b.label)}</span></td><td class="muted">${esc(b.size)}</td></tr>`).join('') : '<tr><td colspan="3" class="muted" style="text-align:center;padding:20px">No backups yet</td></tr>'}
          </tbody>
        </table>
        <div id="bk-status" style="margin-top:10px;font-size:13px;color:var(--fg3)"></div>`;
      c.appendChild(listCard);

      // Row selection
      listCard.querySelectorAll('#bk-table tbody tr').forEach(row => {
        row.onclick = () => { qsa('#bk-table tbody tr').forEach(r=>r.classList.remove('selected')); row.classList.add('selected'); Pages.backups.selected = row.dataset.path; };
      });

      listCard.querySelector('#bk-create').onclick = async () => {
        const r = await API.createBackup();
        r.ok ? toast('Creating backup…', 'info') : toast(r.error, 'error');
      };
      listCard.querySelector('#bk-restore').onclick = async () => {
        if (!Pages.backups.selected) { toast('Select a backup first','error'); return; }
        if (State.serverStatus === 'running') { toast('Stop the server before restoring a backup','error'); return; }
        const ok = await confirm('Restore Backup', 'This will overwrite the server\'s Saved directory. Continue?');
        if (ok) { await API.restoreBackup(Pages.backups.selected); toast('Restoring…','info'); }
      };
      listCard.querySelector('#bk-delete').onclick = async () => {
        if (!Pages.backups.selected) { toast('Select a backup first','error'); return; }
        const ok = await confirm('Delete Backup', 'Permanently delete this backup?');
        if (ok) { await API.deleteBackup(Pages.backups.selected); Pages.backups.render(); toast('Deleted','success'); }
      };
      listCard.querySelector('#bk-folder').onclick = async () => {
        const d = (await API.call('get_manager_dir')).data;
        API.openFolder(d + '/backups');
      };
    }
  },

  // ──────────────────────────────────────────────── RCON ───
  rcon: {
    history: [],
    histIdx: -1,
    render() {
      const c = qs('#content');
      c.style.display = 'flex';
      c.style.flexDirection = 'column';
      c.innerHTML = `
        <div class="page-header" style="flex-shrink:0">
          <div class="page-title">RCON Console</div>
          <div class="page-subtitle">Send commands directly to the running server</div>
        </div>
        <div class="card" style="flex-shrink:0">
          <div class="gap-row" style="flex-wrap:wrap">
            <div class="field" style="flex:0 0 auto"><label class="field-label">Host</label><input type="text" id="rcon-host" value="${esc((State.profile.rcon||{}).host||'localhost')}" style="width:140px"></div>
            <div class="field" style="flex:0 0 auto"><label class="field-label">Port</label><input type="text" id="rcon-port" value="${esc(String((State.profile.rcon||{}).port||27020))}" style="width:80px"></div>
            <div class="field" style="flex:0 0 auto"><label class="field-label">Password</label><input type="password" id="rcon-pw" value="${esc((State.profile.rcon||{}).password||'')}" style="width:160px"></div>
            <div style="display:flex;align-items:flex-end;gap:8px">
              <button class="btn btn-primary" id="rcon-connect">Connect</button>
              <button class="btn btn-ghost" id="rcon-disconnect">Disconnect</button>
              <button class="btn btn-ghost" id="rcon-save-cfg" style="font-size:12px">Save</button>
            </div>
            <div id="rcon-status" style="display:flex;align-items:flex-end;padding-bottom:2px">
              <span class="badge badge-red"><span class="dot stopped"></span>Disconnected</span>
            </div>
          </div>
        </div>
        <div class="card" style="flex-shrink:0">
          <div class="card-title">Quick Commands</div>
          <div class="quick-cmds">
            ${[['SaveWorld','saveworld'],['List Players','listplayers'],['Broadcast','broadcast '],['Destroy Wild Dinos','destroywilddinos'],['Do Exit','doexit'],['Set Time','SetTimeOfDay 12:00'],['Kick Player','KickPlayer '],['Ban Player','BanPlayer ']].map(([l,c])=>`<button class="quick-cmd-btn" data-cmd="${esc(c)}">${esc(l)}</button>`).join('')}
          </div>
        </div>
        <div id="rcon-output" style="flex:1;min-height:0;margin-bottom:8px"></div>
        <div class="card" style="flex-shrink:0;padding:10px 14px">
          <div class="gap-row">
            <span style="color:var(--accent);font-family:Consolas;font-size:13px;font-weight:700">></span>
            <input type="text" id="rcon-input" placeholder="Enter command…" style="flex:1">
            <button class="btn btn-primary" id="rcon-send">Send</button>
          </div>
        </div>`;

      qs('#rcon-connect').onclick    = () => Pages.rcon._connect();
      qs('#rcon-disconnect').onclick = () => Pages.rcon._disconnect();
      qs('#rcon-send').onclick       = () => Pages.rcon._send();
      qs('#rcon-save-cfg').onclick   = async () => {
        await API.saveRconSettings({ host:qs('#rcon-host').value, port:parseInt(qs('#rcon-port').value)||27020, password:qs('#rcon-pw').value });
        toast('RCON settings saved','success');
      };
      qs('#rcon-input').addEventListener('keydown', e => {
        if (e.key==='Enter') Pages.rcon._send();
        if (e.key==='ArrowUp')   { e.preventDefault(); Pages.rcon._historyUp(); }
        if (e.key==='ArrowDown') { e.preventDefault(); Pages.rcon._historyDown(); }
      });
      qsa('.quick-cmd-btn').forEach(b => b.onclick = () => { qs('#rcon-input').value = b.dataset.cmd; qs('#rcon-input').focus(); });
    },

    _write(text, cls='rcon-resp') {
      const out = qs('#rcon-output');
      if (!out) return;
      const span = el('span', cls, esc(text) + '\n');
      span.style.display = 'block';
      out.appendChild(span);
      out.scrollTop = out.scrollHeight;
    },

    async _connect() {
      const h=qs('#rcon-host').value, p=qs('#rcon-port').value, pw=qs('#rcon-pw').value;
      this._write(`Connecting to ${h}:${p}…`, 'rcon-info');
      const r = await API.rconConnect(h, p, pw);
      if (r.ok) {
        State.rconConnected = true;
        qs('#rcon-status').innerHTML = '<span class="badge badge-green"><span class="dot running"></span>Connected</span>';
        this._write('Connected!', 'rcon-info');
      } else {
        this._write('Connection failed: ' + r.error, 'rcon-err');
      }
    },

    async _disconnect() {
      await API.rconDisconnect();
      State.rconConnected = false;
      qs('#rcon-status').innerHTML = '<span class="badge badge-red"><span class="dot stopped"></span>Disconnected</span>';
      this._write('Disconnected.', 'rcon-info');
    },

    async _send() {
      const input = qs('#rcon-input');
      const cmd = input.value.trim();
      if (!cmd) return;
      this.history.unshift(cmd);
      this.histIdx = -1;
      input.value = '';
      this._write('> ' + cmd, 'rcon-cmd');
      const r = await API.rconCommand(cmd);
      r.ok ? this._write(r.data, 'rcon-resp') : this._write('Error: ' + r.error, 'rcon-err');
    },

    _historyUp() {
      if (this.histIdx < this.history.length-1) this.histIdx++;
      qs('#rcon-input').value = this.history[this.histIdx] || '';
    },

    _historyDown() {
      if (this.histIdx > 0) this.histIdx--;
      else { this.histIdx=-1; qs('#rcon-input').value=''; return; }
      qs('#rcon-input').value = this.history[this.histIdx]||'';
    }
  }
};

// ═══════════════════════════════════════════════════════════════════════════
//  DASHBOARD helpers
// ═══════════════════════════════════════════════════════════════════════════

function refreshDashboardButtons(card) {
  card = card || qs('#dash-btn-row')?.closest('.card');
  if (!card) return;
  const row = card.querySelector('#dash-btn-row');
  if (!row) return;

  const s = State.serverStatus;
  const running  = s === 'running';
  const starting = s === 'starting';

  row.innerHTML = `
    <button class="btn btn-success" id="dash-start" ${(running||starting)?'disabled':''}>▶ Start</button>
    <button class="btn btn-danger"  id="dash-stop"  ${(!running&&!starting)?'disabled':''}>■ Stop</button>
    <button class="btn btn-ghost"   id="dash-restart" ${!running?'disabled':''}>↺ Restart</button>`;

  row.querySelector('#dash-start').onclick = async () => {
    const r = await API.startServer();
    if (!r.ok) toast(r.error, 'error');
    else { toast('Starting server…','info'); Router.navigate('logs'); }
  };
  row.querySelector('#dash-stop').onclick = async () => {
    const ok = await confirm('Stop Server', 'Stop the server? Connected players will be disconnected.');
    if (ok) await API.stopServer();
  };
  row.querySelector('#dash-restart').onclick = async () => {
    const ok = await confirm('Restart Server', 'Restart the server? Players will be briefly disconnected.');
    if (ok) await API.restartServer();
  };

  // Update dot+text
  const bd = card.querySelector('#dash-big-dot');
  if (bd) { bd.className = `big-dot ${s}`; }
  const bt = card.querySelector('#dash-status-text');
  if (bt) { bt.textContent = s.charAt(0).toUpperCase()+s.slice(1); }
  const upt = card.querySelector('#dash-uptime');
  if (upt) upt.textContent = State.uptime ? `Uptime: ${State.uptime}` : '';
}

// ═══════════════════════════════════════════════════════════════════════════
//  PROFILE SELECTOR
// ═══════════════════════════════════════════════════════════════════════════

async function loadProfiles() {
  const names = await API.getProfileNames();
  const sel = qs('#profile-select');
  sel.innerHTML = names.map(n=>`<option value="${esc(n)}" ${n===State.config.active_profile?'selected':''}>${esc(n)}</option>`).join('');
}

qs('#profile-select').addEventListener('change', async e => {
  const r = await API.switchProfile(e.target.value);
  if (r.ok) {
    State.profile = await API.getProfile();
    Router.navigate(State.page);
    toast(`Switched to profile "${e.target.value}"`, 'info');
  }
});

qs('#new-profile-btn').addEventListener('click', async () => {
  const name = prompt('New profile name:');
  if (!name || !name.trim()) return;
  const r = await API.addProfile(name.trim());
  if (r.ok) { State.profile = await API.getProfile(); await loadProfiles(); Router.navigate(State.page); toast(`Profile "${name}" created`, 'success'); }
  else toast(r.error, 'error');
});

// ═══════════════════════════════════════════════════════════════════════════
//  EVENT BUS HANDLERS
// ═══════════════════════════════════════════════════════════════════════════

EventBus.on('install_log', line => {
  if (State.page === 'install') Pages.install._appendLog(line);
  if (State.page === 'logs')    Pages.logs._appendLine(line);
});

EventBus.on('install_done', async data => {
  const msg = data.msg || (data.ok ? 'Done!' : 'Failed');
  toast(msg, data.ok ? 'success' : 'error');
  const btn = document.getElementById('install-btn');
  if (btn) { btn.disabled=false; }
  const bar = document.getElementById('install-progress');
  if (bar) bar.classList.remove('indeterminate');
  // Refresh SteamCMD status label after a download completes
  const statusEl = document.getElementById('scmd-status');
  const pathEl   = document.getElementById('scmd-path');
  if (statusEl && data.ok) {
    const inf = await API.getSteamcmdInfo();
    if (inf && inf.detected) {
      if (pathEl) pathEl.value = inf.detected;
      statusEl.innerHTML = `<span class="text-green">✓ Found: ${esc(inf.detected)}</span>`;
    }
  }
});

EventBus.on('install_progress', pct => {
  const bar = document.getElementById('install-progress');
  if (bar && !bar.classList.contains('indeterminate')) bar.style.width = pct + '%';
});

EventBus.on('backup_log', msg => toast(msg, 'info', 4000));
EventBus.on('backup_done', data => {
  toast(data.ok ? 'Backup complete ✓' : 'Backup failed', data.ok?'success':'error');
  if (State.page === 'backups') Pages.backups.render();
});

EventBus.on('mod_install_done', data => {
  toast(`Mod ${data.mod_id} ${data.ok?'installed ✓':'FAILED'}`, data.ok?'success':'error');
  if (State.page === 'mods') Pages.mods.render();
});

EventBus.on('update_check', data => {
  const el = document.getElementById('update-status');
  const buildEl = document.getElementById('dash-update-val');
  if (buildEl) buildEl.textContent = data.local || '-';
  if (el) {
    if (data.available) { el.innerHTML = `<span class="text-yellow">⚠ Update available! → ${esc(data.remote)}</span>`; }
    else { el.innerHTML = `<span class="text-green">✓ Up to date (build ${esc(data.local)})</span>`; }
  }
});

// server_log events are no longer pushed - logs page polls get_log_lines() instead

// ═══════════════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════════════

async function init() {
  // Wait for pywebview to be ready
  await new Promise(resolve => {
    if (window.pywebview) resolve();
    else window.addEventListener('pywebviewready', resolve);
  });

  State.config  = await API.getConfig();
  State.profile = await API.getProfile();

  await loadProfiles();
  Search.build();
  Search.initEvents();
  Router.init();
  Router.navigate('dashboard');
  EventBus.poll();
}

init().catch(console.error);
