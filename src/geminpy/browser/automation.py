# this_file: src/geminpy/browser/automation.py
"""OAuth flow automation using Playwright."""

import asyncio
import os
import re

import requests
from loguru import logger
from playwright.async_api import Page, Playwright, async_playwright

from geminpy.core.constants import CDP_VERSION_URL, SUCCESS_PATTERN
from geminpy.core.exceptions import AuthenticationError


class OAuthAutomator:
    """Handles OAuth flow automation using Playwright."""

    def __init__(self, debug_port: int = 9222):
        """Initialize with Chrome debug port."""
        self.debug_port = debug_port

    async def _connect_playwright(self) -> tuple[Playwright, Page]:
        """Connect to Chrome via CDP and return playwright instance and OAuth page."""
        logger.debug("Connecting to Chrome over CDP...")
        info = requests.get(CDP_VERSION_URL.format(port=self.debug_port), timeout=10).json()
        ws_url = info["webSocketDebuggerUrl"]
        pw = await async_playwright().start()
        browser = await pw.chromium.connect_over_cdp(ws_url)

        if not browser.contexts:
            msg = "No browser contexts found. Is Chrome running correctly?"
            raise AuthenticationError(
                msg
            )
        context = browser.contexts[0]

        # Find the OAuth page
        logger.debug("Searching for Google OAuth page among open tabs...")
        for _ in range(8):  # Reduced from 15 to 8 seconds
            for page in context.pages:
                try:
                    url = page.url
                    if "accounts.google.com" in url:
                        logger.debug(f"Found potential OAuth page: {url}")
                        await page.bring_to_front()
                        return pw, page
                except Exception as e:
                    logger.debug(f"Could not check a page, it might be closed: {e}")
            logger.debug("OAuth page not found yet, retrying...")
            await asyncio.sleep(1)

        msg = "Could not find a Google Accounts page to automate."
        raise AuthenticationError(msg)

    async def _wait_for_url(
        self, page: Page, pattern: re.Pattern, timeout: int = 120
    ) -> None:
        """Wait for page URL to match pattern."""
        await page.wait_for_url(pattern, wait_until="load", timeout=timeout * 1000)

    async def run_oauth_flow(self, user_email: str | None) -> None:
        """Execute the complete OAuth flow."""
        pw, page = await self._connect_playwright()
        try:
            logger.debug(f"Automating page: {page.url}")

            # Wait for page to be ready
            await page.wait_for_load_state(
                "domcontentloaded", timeout=15000
            )  # Reduced from 20s
            await asyncio.sleep(1)  # Reduced from 2 seconds

            # Step 1: Click the account
            if user_email:
                logger.debug(f"Looking for specific account: {user_email}")
                # Try direct data-identifier selection first
                account_locator = page.locator(f'[data-identifier="{user_email}"]')

                if await account_locator.count() == 0:
                    logger.debug(
                        f"Specific account '{user_email}' not found by data-identifier, trying by text content"
                    )
                    # Fallback to searching by text content in links
                    account_locator = page.get_by_role(
                        "link", name=re.compile(user_email, re.IGNORECASE)
                    )

                    if await account_locator.count() == 0:
                        logger.debug(
                            f"Specific account '{user_email}' not found, using first available account"
                        )
                        # Use first element with data-identifier
                        account_locator = page.locator("[data-identifier]").first
            else:
                logger.debug("Looking for first available account")
                # Use first element with data-identifier
                account_locator = page.locator("[data-identifier]").first

            account_count = await account_locator.count()
            if account_count == 0:
                await page.screenshot(path="oauth_error_no_account.png")
                target_desc = f"'{user_email}'" if user_email else "any account"
                msg = f"Could not find {target_desc} using direct selection."
                raise AuthenticationError(
                    msg
                )

            logger.debug(f"Account found ({account_count} matches), clicking it...")
            await account_locator.click()

            # Step 2: Click the sign-in button
            logger.debug("Waiting for the approval page to load...")
            await page.wait_for_load_state(
                "domcontentloaded", timeout=10000
            )  # Reduced from 15s
            await asyncio.sleep(1)  # Reduced from 2 seconds

            logger.debug("Looking for sign-in button...")

            # Try multiple strategies to find the sign-in button
            sign_in_button = None

            # Strategy 1: Look for button by text in multiple languages
            button_texts = [
                "Sign in", "Continue",  # English
                "Zaloguj się", "Dalej", "Kontynuuj",  # Polish
                "Se connecter", "Continuer",  # French
                "Anmelden", "Weiter",  # German
                "Acceder", "Continuar",  # Spanish
                "Accedi", "Continua",  # Italian
                "Войти", "Продолжить",  # Russian
                "ログイン", "続行",  # Japanese
                "登录", "继续",  # Chinese
            ]

            for text in button_texts:
                locator = page.get_by_role("button", name=re.compile(re.escape(text), re.IGNORECASE))
                if await locator.count() > 0:
                    sign_in_button = locator.first
                    logger.debug(f"Found sign-in button with text: {text}")
                    break

            # Strategy 2: If not found by text, look for buttons with specific attributes
            if not sign_in_button:
                # Look for buttons with common sign-in related attributes
                selectors = [
                    'button[type="submit"]',
                    'button[data-action="sign-in"]',
                    'button[jsname]',  # Google often uses jsname attributes
                    'div[role="button"][tabindex="0"]',  # Sometimes buttons are divs
                ]

                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    # Filter to visible elements that look like primary buttons
                    for element in elements:
                        if await element.is_visible():
                            # Check if it's likely a primary button (often blue/colored)
                            box = await element.bounding_box()
                            if box and box.get('width', 0) > 50:  # Reasonable button width
                                sign_in_button = element
                                logger.debug(f"Found sign-in button using selector: {selector}")
                                break
                    if sign_in_button:
                        break

            # Strategy 3: As last resort, look for the most prominent button
            if not sign_in_button:
                all_buttons = await page.query_selector_all('button, div[role="button"]')
                for button in all_buttons:
                    if await button.is_visible():
                        # Check for primary button styling (often has background color)
                        bg_color = await button.evaluate('(el) => window.getComputedStyle(el).backgroundColor')
                        if bg_color and bg_color != 'rgba(0, 0, 0, 0)' and 'rgb' in bg_color:
                            sign_in_button = button
                            logger.debug("Found sign-in button by styling")
                            break

            if not sign_in_button:
                await page.screenshot(path="oauth_error_no_signin.png")
                msg = "Could not find sign-in button using any strategy"
                raise AuthenticationError(msg)

            logger.debug("Sign-in button found, clicking it...")
            await sign_in_button.click()

            # Step 3: Wait for success and close tab
            logger.debug("Waiting for success redirect...")
            await self._wait_for_url(page, re.compile(SUCCESS_PATTERN), timeout=60)
            logger.debug("OAuth flow completed successfully ✔")
            logger.debug(f"Success page reached: {page.url}")

            logger.debug("Closing success tab...")
            await page.close()
            logger.debug("Success tab closed successfully")

        except Exception as e:
            logger.error(f"An error occurred during OAuth automation: {e}")
            await page.screenshot(path="oauth_error.png")
            logger.debug("Saved a screenshot to oauth_error.png for debugging.")
            raise
        finally:
            logger.debug("Stopping Playwright.")
            await pw.stop()


class UserResolver:
    """Resolves the target user email from multiple sources."""

    @staticmethod
    def resolve_user_email(
        cli_user: str | None = None, settings_getter=None
    ) -> str | None:
        """Resolve user email from multiple sources in priority order."""
        # 1. --user command line argument
        if cli_user:
            logger.debug(f"Using user from CLI argument: {cli_user}")
            return cli_user

        # 2. GEMINI_CLI_USER environment variable
        env_user = os.environ.get("GEMINI_CLI_USER")
        if env_user:
            logger.debug(f"Using user from GEMINI_CLI_USER env var: {env_user}")
            return env_user

        # 3. gemini_cli_user in settings.json
        if settings_getter:
            stored_user = settings_getter()
            if stored_user:
                logger.debug(f"Using user from settings.json: {stored_user}")
                return stored_user

        # 4. No specific user - will use first available account
        logger.debug("No specific user configured - will use first available account")
        return None
