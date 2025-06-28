# this_file: src/geminpy/browser/chrome.py
"""Chrome for Testing management and process control."""

import asyncio
import subprocess
import time
from pathlib import Path

import requests
from loguru import logger

from geminpy.core.config import AppConfig, ChromeConfig
from geminpy.core.constants import CDP_VERSION_URL, BrowserID
from geminpy.core.exceptions import ChromeError, ChromeInstallationError
from geminpy.utils.storage import SettingsManager


class ChromeTestingManager:
    """Manages Chrome for Testing installation and configuration."""

    def __init__(self, config: AppConfig):
        """Initialize with app configuration."""
        self.config = config
        self.settings = SettingsManager(config.settings_dir)

    def get_stored_path(self) -> Path | None:
        """Get the stored Chrome for Testing executable path."""
        path_str = self.settings.get("chrome_testing_path")
        return Path(path_str) if path_str else None

    def set_stored_path(self, path: Path) -> None:
        """Store the Chrome for Testing executable path."""
        self.settings.set("chrome_testing_path", str(path))

    def get_stored_user(self) -> str | None:
        """Get the stored gemini CLI user email."""
        return self.settings.get("gemini_cli_user")

    def set_stored_user(self, user_email: str) -> None:
        """Store the gemini CLI user email."""
        self.settings.set("gemini_cli_user", user_email)

    def install(self) -> Path:
        """Install Chrome for Testing and return the executable path."""
        logger.debug("Installing Chrome for Testing...")

        cmd = [
            "npx",
            "-y",
            "@puppeteer/browsers",
            "install",
            "chrome@stable",
            "--platform",
            "mac",
            "--path",
            "/Applications",
            "--quiet",
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output to find the executable path
        executable_path = None
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("Downloading"):
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    executable_path = parts[1]
                    break

        if not executable_path:
            msg = f"Could not parse Chrome for Testing path from output: {result.stdout}"
            raise ChromeInstallationError(
                msg
            )

        path = Path(executable_path)
        if not path.exists():
            msg = f"Chrome for Testing executable not found at: {executable_path}"
            raise ChromeInstallationError(
                msg
            )

        logger.debug(f"Chrome for Testing installed at: {executable_path}")
        self.set_stored_path(path)
        return path

    def ensure_available(self) -> Path:
        """Ensure Chrome for Testing is available and return the executable path."""
        from geminpy.browser.manager import BrowserManager

        # Check if we already have the path stored
        stored_path = self.get_stored_path()
        if stored_path and stored_path.exists():
            logger.debug(f"Using existing Chrome for Testing: {stored_path}")
            return stored_path

        # Check if 'testing' browser is available in macdefaultbrowser
        available_browsers = BrowserManager.get_available_browsers()
        if BrowserID.TESTING not in available_browsers:
            logger.debug(
                f"'{BrowserID.TESTING}' browser not found in available browsers: {available_browsers}"
            )
            logger.debug("Installing Chrome for Testing...")
            return self.install()
        logger.debug(f"'{BrowserID.TESTING}' browser found in available browsers")
        stored_path = self.get_stored_path()
        if stored_path and stored_path.exists():
            return stored_path
        logger.debug("Chrome for Testing path not found, reinstalling...")
        return self.install()


class ChromeManager:
    """Manages Chrome for Testing processes."""

    def __init__(self, config: ChromeConfig):
        """Initialize with Chrome configuration."""
        self.config = config

    def launch(self, executable_path: Path) -> subprocess.Popen:
        """Launch Chrome for Testing with CDP enabled."""
        args = [
            str(executable_path),
            f"--remote-debugging-port={self.config.debug_port}",
            f"--user-data-dir={self.config.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "about:blank",
        ]

        logger.debug(f"exec: {' '.join(args)}")

        # Capture stderr for debugging
        stderr_file = "/tmp/gemini_chrome_stderr.log"
        with open(stderr_file, "w") as f:
            f.write(f"Chrome for Testing launch command: {' '.join(args)}\n")
            f.write("=" * 50 + "\n")

        logger.debug(f"Chrome stderr will be logged to: {stderr_file}")

        return subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=open(stderr_file, "a")
        )

    def is_cdp_ready(self) -> bool:
        """Check if Chrome CDP endpoint is ready."""
        try:
            response = requests.get(
                CDP_VERSION_URL.format(port=self.config.debug_port), timeout=1
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    async def wait_for_cdp(self, timeout: int = 20) -> None:
        """Wait for Chrome's CDP to be ready."""
        logger.debug("Waiting for Chrome CDP port to open...")
        start_time = time.time()
        retry_count = 0
        max_retries = 20

        while time.time() - start_time < timeout:
            retry_count += 1
            try:
                response = requests.get(
                    CDP_VERSION_URL.format(port=self.config.debug_port), timeout=1
                )
                if response.status_code == 200:
                    logger.debug(f"Chrome CDP is ready after {retry_count} attempts.")
                    return
                logger.debug(
                    f"retry {retry_count}/{max_retries} … HTTP {response.status_code}"
                )
            except requests.ConnectionError:
                logger.debug(f"retry {retry_count}/{max_retries} … connection refused")
            except requests.RequestException as e:
                logger.debug(
                    f"retry {retry_count}/{max_retries} … {type(e).__name__}: {e}"
                )

            await asyncio.sleep(1)

        error_msg = f"""
ERROR: Chrome never opened port {self.config.debug_port} after {retry_count} attempts.

Possible causes:
• Another Chrome instance was already running without --remote-debugging-port
• A firewall is blocking localhost:{self.config.debug_port}
• Chrome failed to start (check /tmp/gemini_chrome_stderr.log)

Try manually:
  curl http://localhost:{self.config.debug_port}/json/version

You should get a JSON response with 'webSocketDebuggerUrl'.
"""
        logger.error(error_msg.strip())
        msg = f"Chrome CDP did not become available after {retry_count} attempts."
        raise ChromeError(
            msg
        )
