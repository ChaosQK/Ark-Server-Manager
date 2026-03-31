"""
ARK Workshop mod management.
Downloads mods via SteamCMD and copies them into the server directory.
"""
from __future__ import annotations
import os
import queue
import shutil
from typing import Callable, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# Steam Workshop item details API
_WORKSHOP_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
# ARK: Survival Evolved game AppID (for Workshop)
_ASE_GAME_APPID = "346110"


def get_mod_info(mod_id: str) -> dict:
    """
    Fetch mod metadata from Steam Web API.
    Returns dict with 'title', 'description', 'time_updated', 'file_size'.
    """
    if not _HAS_REQUESTS:
        return {"title": f"Mod {mod_id}", "description": "", "time_updated": 0, "file_size": 0}
    try:
        resp = requests.post(
            _WORKSHOP_API,
            data={"itemcount": 1, "publishedfileids[0]": mod_id},
            timeout=10,
        )
        details = resp.json()["response"]["publishedfiledetails"][0]
        return {
            "title": details.get("title", f"Mod {mod_id}"),
            "description": details.get("description", ""),
            "time_updated": details.get("time_updated", 0),
            "file_size": details.get("file_size", 0),
        }
    except Exception:
        return {"title": f"Mod {mod_id}", "description": "", "time_updated": 0, "file_size": 0}


class ModManager:
    def __init__(self, steamcmd_runner):
        self._steamcmd = steamcmd_runner

    def _workshop_path(self, steamcmd_dir: str, mod_id: str) -> str:
        """Path where SteamCMD downloads Workshop content."""
        return os.path.join(
            steamcmd_dir, "steamapps", "workshop", "content", _ASE_GAME_APPID, mod_id
        )

    def _server_mod_path(self, server_install_dir: str, mod_id: str) -> str:
        return os.path.join(
            server_install_dir, "ShooterGame", "Content", "Mods", mod_id
        )

    def install_mod(
        self,
        mod_id: str,
        steamcmd_dir: str,
        server_install_dir: str,
        log_queue: "queue.Queue[str]",
        done_callback: Callable[[bool], None],
    ) -> None:
        """Download mod via SteamCMD then copy into server directory."""

        def _after_download(success: bool):
            if not success:
                done_callback(False)
                return
            src = self._workshop_path(steamcmd_dir, mod_id)
            dst = self._server_mod_path(server_install_dir, mod_id)
            if not os.path.isdir(src):
                log_queue.put(f"[Mods] Workshop download not found at {src}\n")
                done_callback(False)
                return
            log_queue.put(f"[Mods] Copying mod {mod_id} to server...\n")
            try:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                log_queue.put(f"[Mods] Mod {mod_id} installed.\n")
                done_callback(True)
            except Exception as e:
                log_queue.put(f"[Mods] Copy failed: {e}\n")
                done_callback(False)

        self._steamcmd.install_workshop_mod(mod_id, log_queue, _after_download)

    def remove_mod(self, mod_id: str, server_install_dir: str) -> bool:
        dst = self._server_mod_path(server_install_dir, mod_id)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
            return True
        return False

    def is_mod_installed(self, mod_id: str, server_install_dir: str) -> bool:
        return os.path.isdir(self._server_mod_path(server_install_dir, mod_id))
