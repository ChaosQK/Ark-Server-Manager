"""
SteamCMD download, installation, and server update management.
"""
from __future__ import annotations
import os
import queue
import re
import subprocess
import threading
import zipfile
from pathlib import Path
from typing import Callable, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

STEAMCMD_ZIP_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
ASE_SERVER_APPID = "376030"
ASA_SERVER_APPID = "2430930"


def find_steamcmd(hint_dir: str = "") -> Optional[str]:
    """Try to locate steamcmd.exe. Returns path or None."""
    candidates = []
    if hint_dir:
        # hint_dir may be a full exe path (stored after download) or a directory
        if hint_dir.lower().endswith(".exe") and os.path.isfile(hint_dir):
            return hint_dir
        candidates.append(os.path.join(hint_dir, "steamcmd.exe"))
    candidates += [
        r"C:\SteamCMD\steamcmd.exe",
        r"C:\steamcmd\steamcmd.exe",
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Steam", "steamcmd.exe"),
        os.path.join(os.environ.get("USERPROFILE", ""), "SteamCMD", "steamcmd.exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def download_steamcmd(dest_dir: str, progress_cb: Callable[[str, float], None]) -> str:
    """
    Download and extract SteamCMD to dest_dir.
    progress_cb(message, fraction 0-1)
    Returns path to steamcmd.exe.
    """
    if not _HAS_REQUESTS:
        raise RuntimeError("requests library is required to download SteamCMD")

    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "steamcmd.zip")

    progress_cb("Downloading SteamCMD...", 0.0)
    response = requests.get(STEAMCMD_ZIP_URL, stream=True, timeout=30)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    progress_cb(f"Downloading... {downloaded//1024} KB", downloaded / total * 0.7)

    progress_cb("Extracting SteamCMD...", 0.75)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    os.remove(zip_path)

    exe = os.path.join(dest_dir, "steamcmd.exe")
    progress_cb("SteamCMD ready.", 1.0)
    return exe


class SteamCMDRunner:
    """Runs SteamCMD commands and streams output to a queue."""

    # Matches: Update state (0x61) downloading, progress: 45.32 (2134/4710)
    _PROGRESS_RE = re.compile(r"progress:\s*([\d.]+)\s*\((\d+)/(\d+)\)")

    def __init__(self, steamcmd_exe: str):
        self.exe = steamcmd_exe
        self._proc: Optional[subprocess.Popen] = None
        self._cancelled = False

    def install_or_update_server(
        self,
        install_dir: str,
        game: str,
        log_queue: "queue.Queue[str]",
        done_callback: Callable[[bool], None],
        branch: str = "",
    ) -> None:
        """
        Run server install/update asynchronously.
        Lines go to log_queue. done_callback(success) called on finish.
        branch: SteamCMD beta branch name, e.g. "experimental". Empty = Live (default).
        """
        appid = ASE_SERVER_APPID if game == "ase" else ASA_SERVER_APPID
        self._cancelled = False

        def _run():
            os.makedirs(install_dir, exist_ok=True)
            app_update_args = [appid]
            if branch:
                app_update_args += ["-beta", branch]
            app_update_args.append("validate")
            cmd = [
                self.exe,
                "+@ShutdownOnFailedCommand", "1",
                "+@NoPromptForPassword", "1",
                "+login", "anonymous",
                "+force_install_dir", install_dir,
                "+app_update", *app_update_args,
                "+quit",
            ]
            log_queue.put(f"[SteamCMD] Starting: {' '.join(cmd)}\n")
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                for line in self._proc.stdout:
                    if self._cancelled:
                        self._proc.terminate()
                        log_queue.put("[SteamCMD] Cancelled.\n")
                        done_callback(False)
                        return
                    log_queue.put(line)
                self._proc.wait()
                success = self._proc.returncode == 0
                log_queue.put(
                    f"[SteamCMD] Finished (exit code {self._proc.returncode}).\n"
                )
                done_callback(success)
            except Exception as e:
                log_queue.put(f"[SteamCMD] Error: {e}\n")
                done_callback(False)
            finally:
                self._proc = None

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def install_workshop_mod(
        self,
        mod_id: str,
        log_queue: "queue.Queue[str]",
        done_callback: Callable[[bool], None],
    ) -> None:
        """Download a Workshop mod (ARK ASE AppID 346110)."""
        self._cancelled = False

        def _run():
            cmd = [
                self.exe,
                "+@ShutdownOnFailedCommand", "1",
                "+@NoPromptForPassword", "1",
                "+login", "anonymous",
                "+workshop_download_item", "346110", mod_id, "validate",
                "+quit",
            ]
            log_queue.put(f"[SteamCMD] Downloading mod {mod_id}...\n")
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                for line in self._proc.stdout:
                    log_queue.put(line)
                self._proc.wait()
                success = self._proc.returncode == 0
                log_queue.put(f"[SteamCMD] Mod {mod_id} download {'succeeded' if success else 'failed'}.\n")
                done_callback(success)
            except Exception as e:
                log_queue.put(f"[SteamCMD] Error: {e}\n")
                done_callback(False)
            finally:
                self._proc = None

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def cancel(self) -> None:
        self._cancelled = True
        if self._proc:
            try:
                self._proc.terminate()
            except OSError:
                pass
