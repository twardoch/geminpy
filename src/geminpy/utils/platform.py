# this_file: src/geminpy/utils/platform.py
"""Platform utilities and dependency checks."""

import platform
import subprocess

from geminpy.core.exceptions import PlatformError


def require_macos() -> None:
    """Ensure running on macOS."""
    if platform.system() != "Darwin":
        msg = "This package currently only supports macOS"
        raise PlatformError(msg)


def require_command(command: str, install_hint: str) -> None:
    """Check if command exists, raise with install hint if not."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        msg = f"Required command '{command}' not found. {install_hint}"
        raise PlatformError(msg)


def check_dependencies() -> None:
    """Verify all required dependencies are available."""
    require_macos()
    require_command("macdefaultbrowser", "Install with: brew install macdefaultbrowser")
    require_command("npx", "Install Node.js from https://nodejs.org")
