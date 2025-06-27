#!/usr/bin/env -S uv run -s
# /// script
# dependencies = [
#   "fire>=0.5.0",
#   "playwright>=1.43.0",
#   "requests>=2.31.0",
#   "platformdirs>=4.0.0",
#   "loguru>=0.7.0",
# ]
# ///
# this_file: geminiclu/gemini_wrapper.py
"""gemini_wrapper.py

Automates Google OAuth flow for the `gemini` CLI on macOS by:
1. Installing Chrome for Testing if not available (using @puppeteer/browsers).
2. Temporarily setting Chrome for Testing as the default browser
   (using *macdefaultbrowser testing*).
3. Launching Chrome for Testing in remote-debugging mode (port 9222).
4. Running the `gemini` CLI with given arguments.
5. Connecting to the running Chrome via Playwright-over-CDP and completing the
   OAuth screens automatically — picking either the account specified in
   ``$GEMINI_CLI_USER`` or the first available account, then pressing
   *Sign in*.
6. Restoring the original default browser and optionally quitting Chrome.

Notes
-----
* Playwright browsers must be installed once: ``playwright install chromium``.
* Chrome for Testing is downloaded automatically via @puppeteer/browsers.
"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import fire  # type: ignore
import platformdirs  # type: ignore
import requests  # type: ignore
from loguru import logger  # type: ignore
from playwright.async_api import Playwright, Page, async_playwright  # type: ignore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEBUG_PORT = 9222
CDP_VERSION_URL = f"http://localhost:{DEBUG_PORT}/json/version"
TESTING_BROWSER_ID = "testing"

OAUTH_SIGNIN_RE = re.compile(r"accounts\.google\.com/signin/oauth")
SUCCESS_RE = re.compile(
    r"developers\.google\.com/gemini-code-assist/auth/auth_success_gemini"
)

# Settings storage
SETTINGS_DIR = Path(platformdirs.user_data_dir(appname="com.twardoch.chrometesting"))
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


# ---------------------------------------------------------------------------
# Chrome for Testing Management
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    logger.debug(message)


class ChromeTestingManager:
    """Manages Chrome for Testing installation and configuration."""

    @staticmethod
    def _load_settings() -> dict:
        """Load Chrome for Testing settings from disk."""
        if not SETTINGS_FILE.exists():
            return {}
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def _save_settings(settings: dict) -> None:
        """Save Chrome for Testing settings to disk."""
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)

    @classmethod
    def get_stored_path(cls) -> Optional[str]:
        """Get the stored Chrome for Testing executable path."""
        settings = cls._load_settings()
        return settings.get("chrome_testing_path")

    @classmethod
    def set_stored_path(cls, path: str) -> None:
        """Store the Chrome for Testing executable path."""
        settings = cls._load_settings()
        settings["chrome_testing_path"] = path
        cls._save_settings(settings)

    @classmethod
    def get_stored_user(cls) -> Optional[str]:
        """Get the stored gemini CLI user email."""
        settings = cls._load_settings()
        return settings.get("gemini_cli_user")

    @classmethod
    def set_stored_user(cls, user_email: str) -> None:
        """Store the gemini CLI user email."""
        settings = cls._load_settings()
        settings["gemini_cli_user"] = user_email
        cls._save_settings(settings)

    @classmethod
    def install(cls) -> str:
        """Install Chrome for Testing and return the executable path."""
        log("Installing Chrome for Testing...")

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

        log(f"Running: {' '.join(cmd)}")
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
            raise RuntimeError(
                f"Could not parse Chrome for Testing path from output: {result.stdout}"
            )

        if not Path(executable_path).exists():
            raise RuntimeError(
                f"Chrome for Testing executable not found at: {executable_path}"
            )

        log(f"Chrome for Testing installed at: {executable_path}")
        cls.set_stored_path(executable_path)
        return executable_path

    @classmethod
    def ensure_available(cls) -> str:
        """Ensure Chrome for Testing is available and return the executable path."""
        # Check if we already have the path stored
        stored_path = cls.get_stored_path()
        if stored_path and Path(stored_path).exists():
            log(f"Using existing Chrome for Testing: {stored_path}")
            return stored_path

        # Check if 'testing' browser is available in macdefaultbrowser
        available_browsers = BrowserManager.get_available_browsers()
        if TESTING_BROWSER_ID not in available_browsers:
            log(
                f"'{TESTING_BROWSER_ID}' browser not found in available browsers: {available_browsers}"
            )
            log("Installing Chrome for Testing...")
            return cls.install()
        else:
            log(f"'{TESTING_BROWSER_ID}' browser found in available browsers")
            stored_path = cls.get_stored_path()
            if stored_path and Path(stored_path).exists():
                return stored_path
            else:
                log("Chrome for Testing path not found, reinstalling...")
                return cls.install()


# ---------------------------------------------------------------------------
# Browser Management
# ---------------------------------------------------------------------------


class BrowserManager:
    """Manages default browser settings."""

    @staticmethod
    def _require_mac() -> None:
        if platform.system() != "Darwin":
            raise RuntimeError("This helper only supports macOS (Darwin)")

    @staticmethod
    def _require_defaultbrowser() -> None:
        try:
            subprocess.run(["macdefaultbrowser"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "`macdefaultbrowser` utility missing — brew install macdefaultbrowser"
            )

    @classmethod
    def get_current_default(cls) -> str:
        """Return the current default browser identifier."""
        cls._require_defaultbrowser()
        result = subprocess.run(
            ["macdefaultbrowser"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and line.startswith("* "):
                return line[2:]
        return (
            result.stdout.splitlines()[0].strip() if result.stdout.splitlines() else ""
        )

    @classmethod
    def get_available_browsers(cls) -> list[str]:
        """Return list of available browser identifiers."""
        cls._require_defaultbrowser()
        result = subprocess.run(
            ["macdefaultbrowser"], capture_output=True, text=True, check=True
        )
        browsers = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                browsers.append(line[2:] if line.startswith("* ") else line)
        return browsers

    @classmethod
    def set_default(cls, browser_id: str) -> None:
        """Set the default browser."""
        cls._require_defaultbrowser()
        subprocess.run(["macdefaultbrowser", browser_id], check=True)


# ---------------------------------------------------------------------------
# Chrome Process Management
# ---------------------------------------------------------------------------


class ChromeManager:
    """Manages Chrome for Testing processes."""

    @staticmethod
    def launch(executable_path: str) -> subprocess.Popen:
        """Launch Chrome for Testing with CDP enabled."""
        user_data_dir = "/tmp/chrome_gemini_automation"
        args = [
            executable_path,
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "about:blank",
        ]

        log(f"exec: {' '.join(args)}")

        # Capture stderr for debugging
        stderr_file = "/tmp/gemini_chrome_stderr.log"
        with open(stderr_file, "w") as f:
            f.write(f"Chrome for Testing launch command: {' '.join(args)}\n")
            f.write("=" * 50 + "\n")

        log(f"Chrome stderr will be logged to: {stderr_file}")

        return subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=open(stderr_file, "a")
        )

    @staticmethod
    def is_cdp_ready(port: int = DEBUG_PORT) -> bool:
        """Check if Chrome CDP endpoint is ready."""
        try:
            response = requests.get(f"http://localhost:{port}/json/version", timeout=1)
            return response.status_code == 200
        except requests.RequestException:
            return False

    @classmethod
    async def wait_for_cdp(cls, timeout: int = 20) -> None:
        """Wait for Chrome's CDP to be ready."""
        log("Waiting for Chrome CDP port to open...")
        start_time = time.time()
        retry_count = 0
        max_retries = 20

        while time.time() - start_time < timeout:
            retry_count += 1
            try:
                response = requests.get(CDP_VERSION_URL, timeout=1)
                if response.status_code == 200:
                    log(f"Chrome CDP is ready after {retry_count} attempts.")
                    return
                else:
                    log(
                        f"retry {retry_count}/{max_retries} … HTTP {response.status_code}"
                    )
            except requests.ConnectionError:
                log(f"retry {retry_count}/{max_retries} … connection refused")
            except requests.RequestException as e:
                log(f"retry {retry_count}/{max_retries} … {type(e).__name__}: {e}")

            await asyncio.sleep(1)

        error_msg = f"""
ERROR: Chrome never opened port {DEBUG_PORT} after {retry_count} attempts.

Possible causes:
• Another Chrome instance was already running without --remote-debugging-port
• A firewall is blocking localhost:{DEBUG_PORT}
• Chrome failed to start (check /tmp/gemini_chrome_stderr.log)

Try manually:
  curl http://localhost:{DEBUG_PORT}/json/version

You should get a JSON response with 'webSocketDebuggerUrl'.
"""
        logger.error(error_msg.strip())
        raise RuntimeError(
            f"Chrome CDP did not become available after {retry_count} attempts."
        )


# ---------------------------------------------------------------------------
# User Resolution
# ---------------------------------------------------------------------------


class UserResolver:
    """Resolves the target user email from multiple sources."""

    @staticmethod
    def resolve_user_email(cli_user: Optional[str] = None) -> Optional[str]:
        """Resolve user email from multiple sources in priority order."""
        # 1. --user command line argument
        if cli_user:
            log(f"Using user from CLI argument: {cli_user}")
            return cli_user

        # 2. GEMINI_CLI_USER environment variable
        env_user = os.environ.get("GEMINI_CLI_USER")
        if env_user:
            log(f"Using user from GEMINI_CLI_USER env var: {env_user}")
            return env_user

        # 3. gemini_cli_user in settings.json
        stored_user = ChromeTestingManager.get_stored_user()
        if stored_user:
            log(f"Using user from settings.json: {stored_user}")
            return stored_user

        # 4. No specific user - will use first available account
        log("No specific user configured - will use first available account")
        return None


# ---------------------------------------------------------------------------
# OAuth Automation
# ---------------------------------------------------------------------------


class OAuthAutomator:
    """Handles OAuth flow automation using Playwright."""

    @staticmethod
    async def _connect_playwright() -> tuple[Playwright, Page]:
        """Connect to Chrome via CDP and return playwright instance and OAuth page."""
        log("Connecting to Chrome over CDP...")
        info = requests.get(CDP_VERSION_URL, timeout=10).json()
        ws_url = info["webSocketDebuggerUrl"]
        pw = await async_playwright().start()
        browser = await pw.chromium.connect_over_cdp(ws_url)

        if not browser.contexts:
            raise RuntimeError(
                "No browser contexts found. Is Chrome running correctly?"
            )
        context = browser.contexts[0]

        # Find the OAuth page
        log("Searching for Google OAuth page among open tabs...")
        for _ in range(8):  # Reduced from 15 to 8 seconds
            for page in context.pages:
                try:
                    url = page.url
                    if "accounts.google.com" in url:
                        log(f"Found potential OAuth page: {url}")
                        await page.bring_to_front()
                        return pw, page
                except Exception as e:
                    log(f"Could not check a page, it might be closed: {e}")
            log("OAuth page not found yet, retrying...")
            await asyncio.sleep(1)

        raise RuntimeError("Could not find a Google Accounts page to automate.")

    @staticmethod
    async def _wait_for_url(
        page: Page, pattern: re.Pattern, timeout: int = 120
    ) -> None:
        """Wait for page URL to match pattern."""
        await page.wait_for_url(pattern, wait_until="load", timeout=timeout * 1000)

    @classmethod
    async def run_oauth_flow(cls, user_email: Optional[str]) -> None:
        """Execute the complete OAuth flow."""
        pw, page = await cls._connect_playwright()
        try:
            log(f"Automating page: {page.url}")

            # Wait for page to be ready
            await page.wait_for_load_state(
                "domcontentloaded", timeout=15000
            )  # Reduced from 20s
            await asyncio.sleep(1)  # Reduced from 2 seconds

            # Step 1: Click the account
            if user_email:
                log(f"Looking for specific account: {user_email}")
                # Try direct data-identifier selection first
                account_locator = page.locator(f'[data-identifier="{user_email}"]')

                if await account_locator.count() == 0:
                    log(
                        f"Specific account '{user_email}' not found by data-identifier, trying by text content"
                    )
                    # Fallback to searching by text content in links
                    account_locator = page.get_by_role(
                        "link", name=re.compile(user_email, re.IGNORECASE)
                    )

                    if await account_locator.count() == 0:
                        log(
                            f"Specific account '{user_email}' not found, using first available account"
                        )
                        # Use first element with data-identifier
                        account_locator = page.locator("[data-identifier]").first
            else:
                log("Looking for first available account")
                # Use first element with data-identifier
                account_locator = page.locator("[data-identifier]").first

            account_count = await account_locator.count()
            if account_count == 0:
                await page.screenshot(path="oauth_error_no_account.png")
                target_desc = f"'{user_email}'" if user_email else "any account"
                raise RuntimeError(
                    f"Could not find {target_desc} using direct selection."
                )

            log(f"Account found ({account_count} matches), clicking it...")
            await account_locator.click()

            # Step 2: Click the sign-in button
            log("Waiting for the approval page to load...")
            await page.wait_for_load_state(
                "domcontentloaded", timeout=10000
            )  # Reduced from 15s
            await asyncio.sleep(1)  # Reduced from 2 seconds

            log("Looking for sign-in button...")
            sign_in_locator = page.get_by_role(
                "button", name=re.compile("Sign in|Continue", re.IGNORECASE)
            )

            if await sign_in_locator.count() == 0:
                await page.screenshot(path="oauth_error_no_signin.png")
                raise RuntimeError(
                    "Could not find 'Sign in' or 'Continue' button using get_by_role."
                )

            log("Sign-in button found, clicking it...")
            await sign_in_locator.first.click()

            # Step 3: Wait for success and close tab
            log("Waiting for success redirect...")
            await cls._wait_for_url(page, SUCCESS_RE, timeout=60)
            log("OAuth flow completed successfully ✔")
            log(f"Success page reached: {page.url}")

            log("Closing success tab...")
            await page.close()
            log("Success tab closed successfully")

        except Exception as e:
            logger.error(f"An error occurred during OAuth automation: {e}")
            await page.screenshot(path="oauth_error.png")
            log("Saved a screenshot to oauth_error.png for debugging.")
            raise
        finally:
            log("Stopping Playwright.")
            await pw.stop()


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------


class GeminiWrapper:
    """Main application class for Gemini OAuth automation."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._setup_logging()
        BrowserManager._require_mac()

    def _setup_logging(self) -> None:
        """Configure loguru logging based on verbose flag."""
        logger.remove()  # Remove default handler
        if self.verbose:
            logger.add(
                sys.stderr,
                level="DEBUG",
                format="<level>{message}</level>",
                colorize=True,
            )

    async def _try_gemini_with_oauth_and_return_response(
        self,
        gemini_args: list[str],
        gemini_executable: str | Path,
        user_email: Optional[str],
    ) -> Optional[str]:
        """Try running gemini with OAuth automation. Returns clean response text or None if failed."""
        # Launch Gemini CLI tool
        gemini_cmd = [str(gemini_executable), *gemini_args]
        log(f"Running gemini: {' '.join(gemini_cmd)}")

        # Capture stderr to detect rate limits in real-time
        gemini_proc = subprocess.Popen(
            gemini_cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )

        # Give gemini a moment to open the URL
        await asyncio.sleep(2)  # Reduced from 5 seconds

        # Run OAuth automation
        log("Starting OAuth automation flow...")
        try:
            await OAuthAutomator.run_oauth_flow(user_email)
            log("Automation flow finished.")
        except Exception as e:
            log(f"OAuth automation failed: {e}")
            gemini_proc.terminate()
            return None

        # Monitor stderr output in real-time for rate limits
        log("Waiting for gemini process to complete...")
        log(f"Gemini process status: running={gemini_proc.poll() is None}")

        rate_limit_detected = False
        stderr_lines = []

        # Monitor process for up to 15 seconds for rate limit detection
        start_time = asyncio.get_event_loop().time()
        while (
            gemini_proc.poll() is None
            and (asyncio.get_event_loop().time() - start_time) < 15
        ):  # Reduced from 30s
            # Check if there's new stderr output
            if gemini_proc.stderr and gemini_proc.stderr.readable():
                try:
                    # Non-blocking read of available stderr data
                    import select

                    if select.select([gemini_proc.stderr], [], [], 0.1)[0]:
                        line = gemini_proc.stderr.readline()
                        if line:
                            stderr_lines.append(line)
                            log(f"Gemini stderr: {line.strip()}")

                            # Check for rate limit indicators
                            if (
                                "429" in line
                                or "Quota exceeded" in line
                                or "rateLimitExceeded" in line
                                or "RESOURCE_EXHAUSTED" in line
                            ):
                                log("Rate limit detected in real-time output!")
                                rate_limit_detected = True
                                break
                except:
                    pass

            await asyncio.sleep(0.5)

        # If rate limit detected, terminate and return failure
        if rate_limit_detected:
            log("Terminating gemini process due to rate limit detection")
            gemini_proc.terminate()
            return None

        # If process is still running after 15s, assume it's working and wait for completion
        try:
            stdout, stderr = gemini_proc.communicate(timeout=90)

            log(f"Gemini process completed with return code: {gemini_proc.returncode}")
            if stdout:
                log(f"Gemini stdout: {stdout}")
            if stderr:
                stderr_lines.append(stderr)
                log(f"Gemini stderr (final): {stderr}")

            # Final check for rate limits in all stderr
            all_stderr = "".join(stderr_lines)
            if (
                "429" in all_stderr
                or "Quota exceeded" in all_stderr
                or "rateLimitExceeded" in all_stderr
                or "RESOURCE_EXHAUSTED" in all_stderr
            ):
                log("Rate limit detected in final output")
                return None

            if gemini_proc.returncode == 0:
                log("Gemini process completed successfully.")

                # Parse stdout to extract clean model response
                if stdout:
                    clean_response = self._extract_model_response(stdout)
                    if clean_response:
                        log(f"Clean model response: {clean_response}")
                        return clean_response
                    else:
                        log("No clean model response found in output")
                        return None

                return None
            else:
                log(f"Gemini process failed with return code: {gemini_proc.returncode}")
                return None

        except subprocess.TimeoutExpired:
            log("Gemini process timed out - terminating...")
            gemini_proc.terminate()
            return None

    def _extract_model_response(self, stdout: str) -> Optional[str]:
        """Extract the clean model response from gemini's mixed stdout output."""
        lines = stdout.strip().split("\n")

        # Skip authentication-related lines and find the actual response
        response_lines = []
        found_auth_complete = False

        for line in lines:
            line = line.strip()

            # Skip dotenv messages
            if line.startswith("[dotenv@"):
                continue

            # Skip authentication messages
            if any(
                auth_phrase in line
                for auth_phrase in [
                    "Code Assist login required",
                    "Attempting to open authentication page",
                    "Otherwise navigate to:",
                    "https://accounts.google.com/o/oauth2",
                    "Waiting for authentication...",
                    "Authentication successful",
                ]
            ):
                continue

            # Skip empty lines at the start
            if not line and not response_lines:
                continue

            # If we find "Waiting for authentication...", the next non-empty line is likely the response
            if "Waiting for authentication..." in stdout:
                found_auth_complete = True

            # Collect non-authentication content
            if line:
                response_lines.append(line)

        # Return the cleaned response
        if response_lines:
            # If there's authentication flow, the response is typically the last meaningful content
            if found_auth_complete and response_lines:
                # Find the first line after authentication that looks like a response
                for i, line in enumerate(response_lines):
                    if not any(
                        skip_phrase in line
                        for skip_phrase in [
                            "dotenv",
                            "Code Assist",
                            "Attempting",
                            "navigate",
                            "oauth2",
                            "Waiting",
                        ]
                    ):
                        # Return from this line to the end
                        return "\n".join(response_lines[i:])

            # Fallback: return all non-auth lines
            return "\n".join(response_lines)

        return None


async def call_gemini_cli(
    gemini_args: list[str],
    quit_chrome: bool = False,
    user: Optional[str] = None,
    gemini_executable: str | Path = "gemini",
    verbose: bool = False,
) -> Optional[str]:
    """Core function to call gemini CLI with OAuth automation. Returns clean response text."""
    wrapper = GeminiWrapper(verbose=verbose)

    # Ensure "-y" flag is present
    if "-y" not in gemini_args and "--yes" not in gemini_args:
        gemini_args.insert(0, "-y")

    orig_browser = BrowserManager.get_current_default()
    user_email = UserResolver.resolve_user_email(user)
    log(f"Original default browser: {orig_browser}")

    # Ensure Chrome for Testing is available
    chrome_testing_path = ChromeTestingManager.ensure_available()
    log(f"Chrome for Testing path: {chrome_testing_path}")

    chrome_proc: Optional[subprocess.Popen] = None
    try:
        # Set Chrome for Testing as default browser
        if orig_browser != TESTING_BROWSER_ID:
            log(f"Setting '{TESTING_BROWSER_ID}' as default browser")
            BrowserManager.set_default(TESTING_BROWSER_ID)

        # Launch Chrome if needed
        if ChromeManager.is_cdp_ready():
            log("Chrome CDP already listening — using existing browser.")
        else:
            log("Launching Chrome for Testing with remote debugging…")
            chrome_proc = ChromeManager.launch(chrome_testing_path)

        # Wait for Chrome CDP to be ready
        await ChromeManager.wait_for_cdp()

        # Try running gemini with original args first
        response = await wrapper._try_gemini_with_oauth_and_return_response(
            gemini_args, gemini_executable, user_email
        )

        if response is None:
            # Check if we should retry with flash model
            if "-m" not in gemini_args and "--model" not in gemini_args:
                log("Rate limit detected, retrying with gemini-2.5-flash model...")
                flash_args = ["-m", "gemini-2.5-flash"] + gemini_args
                response = await wrapper._try_gemini_with_oauth_and_return_response(
                    flash_args, gemini_executable, user_email
                )
            else:
                log("Rate limit detected but model already specified, not retrying")

        return response

    finally:
        # Clean up
        log("Cleaning up...")
        if orig_browser != TESTING_BROWSER_ID:
            BrowserManager.set_default(orig_browser)
            log(f"Restored default browser to {orig_browser}")

        if chrome_proc and chrome_proc.poll() is None and quit_chrome:
            log("Quitting Chrome for Testing as requested.")
            chrome_proc.terminate()
            await asyncio.sleep(1)

        log("Script finished.")


def ask(prompt: str, user: Optional[str] = None, verbose: bool = False) -> str:
    """Ask Gemini a question and get a clean text response.

    Args:
        prompt: The question/prompt to ask
        user: Optional specific user email to use for authentication
        verbose: Enable debug logging

    Returns:
        Clean text response from Gemini

    Raises:
        RuntimeError: If authentication or API call fails
    """
    gemini_args = ["-p", prompt]
    response = asyncio.run(
        call_gemini_cli(gemini_args=gemini_args, user=user, verbose=verbose)
    )

    if response is None:
        raise RuntimeError("Failed to get response from Gemini")

    return response


def cli(
    quit_chrome: bool = False,
    verbose: bool = False,
    user: Optional[str] = None,
    gemini_executable: str | Path = "gemini",
    **gemini_args,
) -> None:
    """CLI interface for gemini with automated OAuth via Playwright using Chrome for Testing."""
    # Convert gemini_args dict to CLI argument list
    cli_args = []
    for key, value in gemini_args.items():
        # Use single dash for single char, double dash for multi-char
        flag = f"-{key}" if len(key) == 1 else f"--{key}"
        cli_args.append(flag)

        # Only add value if it's not a boolean True (flags don't need values)
        if value is not True:
            if value is False:
                # Skip false flags entirely
                cli_args.pop()  # Remove the flag we just added
            else:
                cli_args.append(str(value))

    log(f"Running gemini with CLI args: {cli_args}")

    response = asyncio.run(
        call_gemini_cli(
            gemini_args=cli_args,
            quit_chrome=quit_chrome,
            user=user,
            gemini_executable=gemini_executable,
            verbose=verbose,
        )
    )

    # Print response if we got one (for CLI usage)
    if response:
        print(response)


if __name__ == "__main__":
    fire.Fire(cli)
