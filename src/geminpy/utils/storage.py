# this_file: src/geminpy/utils/storage.py
"""Settings storage management using platformdirs."""

import json
from pathlib import Path

from loguru import logger


class SettingsManager:
    """Manages persistent settings storage."""

    def __init__(self, settings_dir: Path):
        """Initialize settings manager with directory path."""
        self.settings_dir = settings_dir
        self.settings_file = settings_dir / "settings.json"

    def _load_settings(self) -> dict:
        """Load settings from disk."""
        if not self.settings_file.exists():
            return {}
        try:
            with open(self.settings_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load settings: {e}")
            return {}

    def _save_settings(self, settings: dict) -> None:
        """Save settings to disk."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value."""
        settings = self._load_settings()
        return settings.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set a setting value."""
        settings = self._load_settings()
        settings[key] = value
        self._save_settings(settings)

    def delete(self, key: str) -> None:
        """Delete a setting."""
        settings = self._load_settings()
        if key in settings:
            del settings[key]
            self._save_settings(settings)
