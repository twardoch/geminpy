# this_file: src/geminpy/core/config.py
"""Configuration management for Geminpy."""

from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_data_dir


@dataclass
class ChromeConfig:
    """Chrome for Testing configuration."""

    executable_path: Path | None = None
    debug_port: int = 9222
    user_data_dir: Path = Path("/tmp/chrome_gemini_automation")
    quit_browser: bool = False


@dataclass
class GeminiConfig:
    """Gemini CLI configuration."""

    executable: str | Path = "gemini"
    default_model: str = "gemini-2.5-flash"
    timeout: int = 120


@dataclass
class AppConfig:
    """Main application configuration."""

    app_name: str = "com.twardoch.geminpy"
    chrome: ChromeConfig = field(default_factory=ChromeConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    user_email: str | None = None
    verbose: bool = False

    @property
    def settings_dir(self) -> Path:
        """Get the settings directory path."""
        return Path(user_data_dir(appname=self.app_name))
