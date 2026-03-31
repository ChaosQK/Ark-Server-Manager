"""
Checks whether a newer ARK server build is available via the Steam API.
Reads the current build from steamapps/appmanifest_<appid>.acf.
"""
from __future__ import annotations
import os
import re
import threading
from typing import Callable, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# AppIDs
ASE_SERVER_APPID = "376030"
ASA_SERVER_APPID = "2430930"
ASE_GAME_APPID = "346110"


def _parse_acf_buildid(acf_path: str) -> Optional[str]:
    """Extract buildid from a Steam appmanifest .acf file."""
    try:
        with open(acf_path, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'"buildid"\s+"(\d+)"', content)
        if m:
            return m.group(1)
    except OSError:
        pass
    return None


def get_local_build(server_install_dir: str, game: str) -> Optional[str]:
    """Return the local server build ID, or None if not installed."""
    appid = ASE_SERVER_APPID if game == "ase" else ASA_SERVER_APPID
    acf = os.path.join(server_install_dir, "steamapps", f"appmanifest_{appid}.acf")
    return _parse_acf_buildid(acf)


def get_remote_build(game: str) -> Optional[str]:
    """Fetch the latest build ID from the Steam API. Returns None on error."""
    if not _HAS_REQUESTS:
        return None
    appid = ASE_SERVER_APPID if game == "ase" else ASA_SERVER_APPID
    url = f"https://api.steampowered.com/ISteamApps/UpToDateCheck/v1/?appid={appid}&version=0&format=json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        # The UpToDateCheck response includes 'required_version' when not up to date
        result = data.get("response", {})
        if "required_version" in result:
            return str(result["required_version"])
        # Alternatively query the store API for build info
        return None
    except Exception:
        return None


def check_for_update(
    server_install_dir: str,
    game: str,
    callback: Callable[[bool, str, str], None],
) -> None:
    """
    Check asynchronously. Calls callback(update_available, local_build, remote_build).
    """
    def _run():
        local = get_local_build(server_install_dir, game) or "unknown"
        remote = get_remote_build(game) or "unknown"
        update_available = (
            local != "unknown"
            and remote != "unknown"
            and local != remote
        )
        callback(update_available, local, remote)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
