"""
Backup and restore ARK SavedArks data.
Backups are stored as timestamped directories under <manager_dir>/backups/.
"""
from __future__ import annotations
import os
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional


@dataclass
class BackupEntry:
    path: Path
    label: str
    timestamp: datetime
    size_bytes: int

    @property
    def size_str(self) -> str:
        mb = self.size_bytes / 1_048_576
        if mb >= 1024:
            return f"{mb/1024:.1f} GB"
        return f"{mb:.1f} MB"

    @property
    def timestamp_str(self) -> str:
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")


def _dir_size(path: str) -> int:
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total


class BackupManager:
    def __init__(self, manager_dir: str):
        self.backups_dir = os.path.join(manager_dir, "backups")
        self._timer: Optional[threading.Timer] = None
        self._on_backup: Optional[Callable[[str], None]] = None

    def _saved_path(self, server_install_dir: str) -> str:
        return os.path.join(server_install_dir, "ShooterGame", "Saved")

    def create_backup(
        self,
        server_install_dir: str,
        label: str = "manual",
        progress_cb: Optional[Callable[[str], None]] = None,
    ) -> Optional[Path]:
        """Copy ShooterGame/Saved to a new backup folder. Returns path or None."""
        saved = self._saved_path(server_install_dir)
        if not os.path.isdir(saved):
            if progress_cb:
                progress_cb(f"Saved directory not found: {saved}")
            return None

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest_name = f"{ts}_{label}"
        dest = Path(self.backups_dir) / dest_name
        os.makedirs(dest, exist_ok=True)

        if progress_cb:
            progress_cb(f"Creating backup: {dest_name}")
        try:
            shutil.copytree(saved, str(dest / "Saved"))
            if progress_cb:
                progress_cb(f"Backup complete: {dest_name}")
            return dest
        except Exception as e:
            if progress_cb:
                progress_cb(f"Backup failed: {e}")
            return None

    def restore_backup(
        self,
        backup_path: Path,
        server_install_dir: str,
        progress_cb: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """Overwrite server's Saved directory with the backup. Returns True on success."""
        src = backup_path / "Saved"
        if not src.exists():
            if progress_cb:
                progress_cb(f"Backup has no Saved directory: {backup_path}")
            return False

        dest = self._saved_path(server_install_dir)
        if progress_cb:
            progress_cb(f"Restoring backup from {backup_path.name}...")
        try:
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            shutil.copytree(str(src), dest)
            if progress_cb:
                progress_cb("Restore complete.")
            return True
        except Exception as e:
            if progress_cb:
                progress_cb(f"Restore failed: {e}")
            return False

    def list_backups(self) -> list[BackupEntry]:
        entries = []
        if not os.path.isdir(self.backups_dir):
            return entries
        for name in os.listdir(self.backups_dir):
            full = Path(self.backups_dir) / name
            if not full.is_dir():
                continue
            # Parse timestamp from name: YYYY-MM-DD_HH-MM-SS_label
            parts = name.split("_", 3)
            try:
                dt = datetime.strptime(f"{parts[0]}_{parts[1]}_{parts[2]}", "%Y-%m-%d_%H-%M-%S")
                label = parts[3] if len(parts) > 3 else "backup"
            except (ValueError, IndexError):
                dt = datetime.fromtimestamp(full.stat().st_mtime)
                label = name
            size = _dir_size(str(full))
            entries.append(BackupEntry(path=full, label=label, timestamp=dt, size_bytes=size))
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries

    def delete_backup(self, backup_path: Path) -> bool:
        try:
            shutil.rmtree(str(backup_path))
            return True
        except OSError:
            return False

    def prune_old_backups(self, keep_count: int) -> None:
        entries = self.list_backups()
        for entry in entries[keep_count:]:
            self.delete_backup(entry.path)

    def schedule_backup(
        self,
        server_install_dir: str,
        interval_minutes: int,
        keep_count: int,
        on_complete: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Start (or restart) the auto-backup timer."""
        self.stop_schedule()
        self._schedule_next(server_install_dir, interval_minutes, keep_count, on_complete)

    def stop_schedule(self) -> None:
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _schedule_next(self, server_dir, interval_min, keep_count, cb):
        def _run():
            self.create_backup(server_dir, label="auto", progress_cb=cb)
            self.prune_old_backups(keep_count)
            if cb:
                cb(f"Next auto-backup in {interval_min} minutes")
            self._schedule_next(server_dir, interval_min, keep_count, cb)

        self._timer = threading.Timer(interval_min * 60, _run)
        self._timer.daemon = True
        self._timer.start()
