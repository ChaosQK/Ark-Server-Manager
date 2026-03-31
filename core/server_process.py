"""
ARK server process management: start, stop, restart, status monitoring.
Uses only stdlib (no psutil).
"""
from __future__ import annotations
import collections
import os
import queue
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Literal, Optional

StatusType = Literal["stopped", "starting", "running", "crashed"]

# ASE: ShooterGame/Binaries/Win64/ShooterGameServer.exe
# ASA: ShooterGame/Binaries/Win64/ArkAscendedServer.exe
_EXE_MAP = {
    "ase": os.path.join("ShooterGame", "Binaries", "Win64", "ShooterGameServer.exe"),
    "asa": os.path.join("ShooterGame", "Binaries", "Win64", "ArkAscendedServer.exe"),
}

# Logged when the server finishes loading and is ready for connections
_READY_MARKERS = [
    "Server is listening on port",
    "Full init:",
    "Exiting from game thread",      # SA variant
    "Starting UE4 server",
]


class ServerProcess:
    def __init__(self, manager_dir: str):
        self._proc: Optional[subprocess.Popen] = None
        self._status: StatusType = "stopped"
        self._status_callbacks: list[Callable[[StatusType], None]] = []
        self._start_time: Optional[datetime] = None
        self._log_queue: queue.Queue = queue.Queue(maxsize=10000)
        self._log_buffer: collections.deque = collections.deque(maxlen=5000)
        self._monitor_thread: Optional[threading.Thread] = None
        self._health_thread: Optional[threading.Thread] = None
        self._auto_restart = False
        self._auto_restart_delay = 30
        self._manager_dir = manager_dir
        self._log_file: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_status_callback(self, cb: Callable[[StatusType], None]) -> None:
        self._status_callbacks.append(cb)

    @property
    def status(self) -> StatusType:
        return self._status

    @property
    def pid(self) -> Optional[int]:
        if self._proc:
            return self._proc.pid
        return None

    @property
    def uptime(self) -> Optional[timedelta]:
        if self._start_time and self._status == "running":
            return datetime.now() - self._start_time
        return None

    @property
    def log_queue(self) -> queue.Queue:
        return self._log_queue

    def start(
        self,
        server_install_dir: str,
        game: str,
        launch_args: list[str],
        auto_restart: bool = False,
        auto_restart_delay: int = 30,
    ) -> bool:
        """Start the server. Returns True if process launched."""
        if self._status in ("running", "starting"):
            return False

        exe_rel = _EXE_MAP.get(game, _EXE_MAP["ase"])
        exe_path = os.path.join(server_install_dir, exe_rel)
        if not os.path.isfile(exe_path):
            self._log(f"[Manager] Server executable not found: {exe_path}\n")
            return False

        self._auto_restart = auto_restart
        self._auto_restart_delay = auto_restart_delay
        self._set_status("starting")
        self._start_time = datetime.now()

        # Open log file
        os.makedirs(os.path.join(self._manager_dir, "logs"), exist_ok=True)
        log_name = datetime.now().strftime("server_%Y-%m-%d.log")
        self._log_file = os.path.join(self._manager_dir, "logs", log_name)

        cmd = [exe_path] + launch_args
        self._log(f"[Manager] Starting: {' '.join(cmd)}\n")
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW,
                cwd=server_install_dir,
            )
        except Exception as e:
            self._log(f"[Manager] Failed to start: {e}\n")
            self._set_status("stopped")
            return False

        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()
        return True

    def stop(self, graceful: bool = True) -> None:
        """Stop the server."""
        if self._proc is None:
            return
        self._auto_restart = False  # prevent auto-restart on manual stop
        self._log("[Manager] Stopping server...\n")
        try:
            if graceful:
                self._proc.terminate()
                # Give it 30 seconds to shut down gracefully
                try:
                    self._proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
            else:
                self._proc.kill()
        except OSError:
            pass

    def restart(self, server_install_dir: str, game: str, launch_args: list[str]) -> None:
        """Stop then start."""
        self._pending_restart = (server_install_dir, game, launch_args)
        self.stop(graceful=True)

    def is_pid_running(self) -> bool:
        """Check if the tracked PID is still alive (stdlib, no psutil)."""
        pid = self.pid
        if pid is None:
            return False
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return str(pid) in result.stdout
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _set_status(self, new: StatusType) -> None:
        self._status = new
        for cb in self._status_callbacks:
            try:
                cb(new)
            except Exception:
                pass

    def _log(self, line: str) -> None:
        self._log_buffer.append(line)
        try:
            self._log_queue.put_nowait(line)
        except queue.Full:
            pass
        if self._log_file:
            try:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(line)
            except OSError:
                pass

    def _monitor(self) -> None:
        """Read stdout/stderr from server process."""
        pending_restart = None
        try:
            for line in self._proc.stdout:
                self._log(line)
                if self._status == "starting":
                    if any(m in line for m in _READY_MARKERS):
                        self._set_status("running")
        except Exception as e:
            self._log(f"[Manager] Monitor error: {e}\n")
        finally:
            ret = self._proc.wait()
            self._log(f"[Manager] Server exited (code {ret}).\n")
            self._proc = None

            should_restart = self._auto_restart and self._status != "stopped"
            self._set_status("stopped")

            if should_restart:
                self._log(f"[Manager] Auto-restarting in {self._auto_restart_delay}s...\n")
                time.sleep(self._auto_restart_delay)
                pr = getattr(self, "_pending_restart", None)
                if pr:
                    del self._pending_restart
                    self.start(*pr, auto_restart=True,
                               auto_restart_delay=self._auto_restart_delay)
            else:
                pending_restart = getattr(self, "_pending_restart", None)
                if pending_restart:
                    del self._pending_restart
                    time.sleep(2)
                    self.start(*pending_restart)
