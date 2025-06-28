# this_file: src/geminpy/browser/manager.py
"""Manages default browser settings on macOS."""

import macdefaultbrowsy as mdb
from loguru import logger


class BrowserManager:
    """Manages default browser settings on macOS."""

    @classmethod
    def get_current_default(cls) -> str | None:
        """Get current default browser identifier."""
        try:
            return mdb.get_default_browser()
        except Exception as e:
            logger.error(f"Failed to get current default browser: {e}")
            return None

    @classmethod
    def get_available_browsers(cls) -> list[str]:
        """List all available browser identifiers."""
        try:
            return mdb.get_browsers()
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
            # Check if browser is already default to prevent hanging
            current_default = cls.get_current_default()
            if current_default == browser_id:
                logger.info(f"{browser_id} is already the default browser.")
                return True

            logger.debug(f"Setting default browser to: {browser_id}")
            mdb.set_default_browser(browser_id)
            return True
        except Exception as e:
            logger.error(f"Failed to set default browser to {browser_id}: {e}")
            return False

    @classmethod
    def list_browsers(cls) -> None:
        """List all available browsers, marking the default with a *."""
        try:
            browsers = cls.get_available_browsers()
            current = cls.get_current_default()
            for browser in browsers:
                if browser == current:
                    logger.info(f"* {browser}")
                else:
                    logger.info(f"  {browser}")
        except Exception as e:
            logger.error(f"Failed to list browsers: {e}")
