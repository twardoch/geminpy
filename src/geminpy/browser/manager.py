# this_file: src/geminpy/browser/manager.py
"""Manages default browser settings on macOS."""

import subprocess

from loguru import logger

from geminpy.utils.platform import require_command


class BrowserManager:
    """Manages default browser settings on macOS."""

    @staticmethod
    def _require_defaultbrowser() -> None:
        """Ensure macdefaultbrowser utility is available."""
        require_command(
            "macdefaultbrowser",
            "Install with: brew install macdefaultbrowser"
        )

    @classmethod
    def get_current_default(cls) -> str | None:
        """Get current default browser identifier."""
        try:
            cls._require_defaultbrowser()
            result = subprocess.run(
                ["macdefaultbrowser"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and line.startswith("* "):
                    return line[2:]
            return (
                result.stdout.splitlines()[0].strip()
                if result.stdout.splitlines() else None
            )
        except Exception as e:
            logger.error(f"Failed to get current default browser: {e}")
            return None

    @classmethod
    def get_available_browsers(cls) -> list[str]:
        """List all available browser identifiers."""
        try:
            cls._require_defaultbrowser()
            result = subprocess.run(
                ["macdefaultbrowser"],
                capture_output=True,
                text=True,
                check=True
            )
            browsers = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    browsers.append(
                        line[2:] if line.startswith("* ") else line
                    )
            return browsers
        except Exception as e:
            logger.error(f"Failed to get available browsers: {e}")
            return []

    @classmethod
    def set_default(cls, browser_id: str) -> bool:
        """Set the default browser with hanging prevention.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            cls._require_defaultbrowser()

            # Check if browser is already default to prevent hanging
            current_default = cls.get_current_default()
            if current_default == browser_id:
                logger.info(f"{browser_id} is already the default browser.")
                return True

            logger.debug(f"Setting default browser to: {browser_id}")
            subprocess.run(["macdefaultbrowser", browser_id], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to set default browser to {browser_id}: {e}")
            return False

    @classmethod
    def list_browsers(cls) -> None:
        """List all available browsers, marking the default with a *."""
        try:
            cls._require_defaultbrowser()
            result = subprocess.run(
                ["macdefaultbrowser"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                logger.info(line.strip())
        except Exception as e:
            logger.error(f"Failed to list browsers: {e}")
