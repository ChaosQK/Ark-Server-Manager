"""
Custom ARK INI parser that preserves duplicate keys, comments, and blank lines.
ARK's Game.ini uses dozens of duplicate keys (e.g. OverrideNamedEngramEntries=)
which standard configparser cannot handle.
"""
from __future__ import annotations
import os
from typing import List, Tuple, Optional


class ArkIniFile:
    """
    Parses and writes ARK .ini files while preserving:
    - Duplicate keys (stored as ordered list of tuples per section)
    - Blank lines and comments (stored as raw lines with sentinel keys)
    - Original key/value formatting
    """

    _BLANK = "\x00blank"
    _COMMENT = "\x00comment"

    def __init__(self, path: str):
        self.path = path
        # dict[section_name, list[tuple[key, value]]]
        # Special keys _BLANK and _COMMENT store raw lines as values
        self._data: dict[str, list[tuple[str, str]]] = {}
        self._section_order: list[str] = []
        # Lines before the first section header
        self._preamble: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> None:
        self._data.clear()
        self._section_order.clear()
        self._preamble.clear()

        if not os.path.exists(self.path):
            return

        current_section: Optional[str] = None
        with open(self.path, "r", encoding="utf-8-sig", errors="replace") as f:
            for raw_line in f:
                line = raw_line.rstrip("\r\n")
                stripped = line.strip()

                # Section header
                if stripped.startswith("[") and stripped.endswith("]"):
                    current_section = stripped[1:-1]
                    if current_section not in self._data:
                        self._data[current_section] = []
                        self._section_order.append(current_section)
                    continue

                if current_section is None:
                    self._preamble.append(line)
                    continue

                # Blank line
                if not stripped:
                    self._data[current_section].append((self._BLANK, line))
                    continue

                # Comment
                if stripped.startswith(";") or stripped.startswith("#"):
                    self._data[current_section].append((self._COMMENT, line))
                    continue

                # Key=Value
                if "=" in stripped:
                    key, _, value = stripped.partition("=")
                    self._data[current_section].append((key.strip(), value.strip()))
                else:
                    # Bare line (no =) - treat as comment to preserve it
                    self._data[current_section].append((self._COMMENT, line))

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) if os.path.dirname(self.path) else ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8", newline="\r\n") as f:
            for pline in self._preamble:
                f.write(pline + "\r\n")

            for section in self._section_order:
                f.write(f"[{section}]\r\n")
                for key, value in self._data[section]:
                    if key in (self._BLANK, self._COMMENT):
                        f.write(value + "\r\n")
                    else:
                        f.write(f"{key}={value}\r\n")

    def get_sections(self) -> list[str]:
        return list(self._section_order)

    def ensure_section(self, section: str) -> None:
        if section not in self._data:
            self._data[section] = []
            self._section_order.append(section)

    def get_value(self, section: str, key: str, default: str = "") -> str:
        """Return first value for key in section, or default."""
        for k, v in self._data.get(section, []):
            if k == key:
                return v
        return default

    def get_all_values(self, section: str, key: str) -> list[str]:
        """Return all values for a duplicate key."""
        return [v for k, v in self._data.get(section, []) if k == key]

    def set_value(self, section: str, key: str, value: str) -> None:
        """Set a single-occurrence key. Creates section if needed."""
        self.ensure_section(section)
        entries = self._data[section]
        for i, (k, _) in enumerate(entries):
            if k == key:
                entries[i] = (key, value)
                return
        entries.append((key, value))

    def set_all_values(self, section: str, key: str, values: list[str]) -> None:
        """Replace all occurrences of key with the given list of values."""
        self.ensure_section(section)
        # Remove existing entries for this key
        self._data[section] = [(k, v) for k, v in self._data[section] if k != key]
        # Append new entries
        for v in values:
            self._data[section].append((key, v))

    def remove_key(self, section: str, key: str) -> None:
        """Remove all occurrences of key in section."""
        if section in self._data:
            self._data[section] = [(k, v) for k, v in self._data[section] if k != key]

    def get_section_items(self, section: str) -> list[tuple[str, str]]:
        """Return all (key, value) pairs in section, excluding blanks/comments."""
        return [(k, v) for k, v in self._data.get(section, [])
                if k not in (self._BLANK, self._COMMENT)]

    def to_string(self) -> str:
        """Render the INI to a string."""
        lines = list(self._preamble)
        for section in self._section_order:
            lines.append(f"[{section}]")
            for key, value in self._data[section]:
                if key in (self._BLANK, self._COMMENT):
                    lines.append(value)
                else:
                    lines.append(f"{key}={value}")
        return "\n".join(lines)

    def load_from_string(self, text: str) -> None:
        """Load from a string (for the raw editor sync)."""
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ini",
                                          encoding="utf-8", delete=False)
        tmp.write(text)
        tmp.close()
        old_path = self.path
        self.path = tmp.name
        self.load()
        self.path = old_path
        os.unlink(tmp.name)
