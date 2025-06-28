# this_file: src/geminpy/gemini/client.py
"""Main orchestrator for Gemini CLI automation."""

import asyncio
import subprocess

from loguru import logger

from geminpy.browser.automation import OAuthAutomator, UserResolver
from geminpy.browser.chrome import ChromeManager, ChromeTestingManager
from geminpy.browser.manager import BrowserManager
from geminpy.core.config import AppConfig
from geminpy.core.constants import BrowserID
from geminpy.core.exceptions import RateLimitError
from geminpy.gemini.executor import GeminiExecutor
from geminpy.gemini.parser import ResponseParser


class GeminiClient:
    """Main orchestrator for Gemini CLI automation."""

    def __init__(self, config: AppConfig):
        """Initialize with app configuration."""
        self.config = config
        self.browser_manager = BrowserManager()
        self.chrome_testing_manager = ChromeTestingManager(config)
        self.chrome_manager = ChromeManager(config.chrome)
        self.oauth_automator = OAuthAutomator(config.chrome.debug_port)
        self.executor = GeminiExecutor(config.gemini.executable)
        self.parser = ResponseParser()

    async def execute_with_auth(self, args: list[str], user_email: str | None = None) -> str | None:
        """Execute Gemini CLI with automatic OAuth handling."""
        # Resolve user email
        resolved_email = UserResolver.resolve_user_email(user_email, self.chrome_testing_manager.get_stored_user)

        # Save original browser
        orig_browser = self.browser_manager.get_current_default()
        logger.debug(f"Original default browser: {orig_browser}")

        # Ensure Chrome for Testing is available
        chrome_testing_path = self.chrome_testing_manager.ensure_available()
        logger.debug(f"Chrome for Testing path: {chrome_testing_path}")

        chrome_proc = None
        try:
            # Set Chrome for Testing as default browser
            if orig_browser != BrowserID.TESTING:
                logger.debug(f"Setting '{BrowserID.TESTING}' as default browser")
                self.browser_manager.set_default(BrowserID.TESTING)

            # Launch Chrome if needed
            if self.chrome_manager.is_cdp_ready():
                logger.debug("Chrome CDP already listening — using existing browser.")
            else:
                logger.debug("Launching Chrome for Testing with remote debugging…")
                chrome_proc = self.chrome_manager.launch(chrome_testing_path)

            # Wait for Chrome CDP to be ready
            await self.chrome_manager.wait_for_cdp()

            # Try running gemini with original args
            response = await self._try_gemini_with_oauth(args, resolved_email)

            # Only retry if retry is enabled and we got None (failure/rate limit), not empty string (interactive success)
            if response is None and self.config.retry_on_failure:
                # Check if we should retry with flash model
                if "-m" not in args and "--model" not in args:
                    logger.debug("Rate limit detected, retrying with gemini-2.5-flash model...")
                    flash_args = ["-m", "gemini-2.5-flash", *args]
                    response = await self._try_gemini_with_oauth(flash_args, resolved_email)
                else:
                    logger.debug("Rate limit detected but model already specified, not retrying")
            elif response is None and not self.config.retry_on_failure:
                logger.debug("API failure detected but retry disabled (use --retry to enable)")

            # Store successful user for future use (response is not None means success)
            if response is not None and resolved_email:
                self.chrome_testing_manager.set_stored_user(resolved_email)

            return response

        finally:
            # Restore browser
            if orig_browser != BrowserID.TESTING:
                self.browser_manager.set_default(orig_browser)
                logger.debug(f"Restored default browser to {orig_browser}")

            # Optionally quit Chrome
            if chrome_proc and chrome_proc.poll() is None and self.config.chrome.quit_browser:
                logger.debug("Quitting Chrome for Testing as requested.")
                chrome_proc.terminate()
                await asyncio.sleep(1)

    async def _try_gemini_with_oauth(self, args: list[str], user_email: str | None) -> str | None:
        """Try running gemini with OAuth automation."""
        # Check if this is interactive mode (no -p argument)
        is_interactive = "-p" not in args and "--prompt" not in args

        # Start Gemini CLI process
        proc, _, _ = await self.executor.execute(args, self.config.gemini.timeout, interactive=is_interactive)

        # Run OAuth automation
        logger.debug("Starting OAuth automation flow...")
        try:
            await self.oauth_automator.run_oauth_flow(user_email)
            logger.debug("Automation flow finished.")
        except Exception as e:
            logger.debug(f"OAuth automation failed: {e}")
            proc.terminate()
            return None

        # For interactive mode, we need to handle I/O differently
        if is_interactive:
            logger.debug("Running in interactive mode - showing full gemini output")
            # Don't monitor for rate limits in interactive mode
            # Just wait for the process to complete naturally
            try:
                # Let the process run interactively
                await proc.wait()
                # Return empty string to indicate success without parsing
                return ""
            except Exception as e:
                logger.debug(f"Interactive mode error: {e}")
                return None

        # Non-interactive mode - continue with normal flow
        logger.debug("Waiting for gemini process to complete...")
        rate_limit_detected, stderr_lines = await self.executor.monitor_process(proc)

        if rate_limit_detected:
            logger.debug("Terminating gemini process due to rate limit detection")
            proc.terminate()
            return None

        # Wait for completion
        try:
            stdout, stderr = await self.executor.wait_completion(proc, self.config.gemini.timeout)

            if stderr:
                stderr_lines.append(stderr)

            # Final check for rate limits
            all_stderr = "".join(stderr_lines)
            if self.executor.check_rate_limit(all_stderr):
                logger.debug("Rate limit detected in final output")
                return None

            if proc.returncode == 0:
                logger.debug("Gemini process completed successfully.")

                # Parse stdout to extract clean model response
                if stdout:
                    clean_response = self.parser.extract_clean_response(stdout)
                    if clean_response:
                        logger.debug(f"Clean model response: {clean_response}")
                        return clean_response
                    logger.debug("No clean model response found in output")
                    return None

            else:
                logger.debug(f"Gemini process failed with return code: {proc.returncode}")

            return None

        except subprocess.TimeoutExpired:
            logger.debug("Gemini process timed out")
            proc.terminate()
            return None
