# this_file: tests/test_browser/test_automation.py
"""Tests for the OAuthAutomator."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from geminpy.browser.automation import OAuthAutomator, UserResolver
from geminpy.core.exceptions import AuthenticationError


class TestUserResolver:
    """Tests for the UserResolver class."""

    def test_resolve_user_email_cli_priority(self):
        """Verify CLI argument has highest priority."""
        result = UserResolver.resolve_user_email(cli_user="cli@example.com")
        assert result == "cli@example.com"

    @patch.dict(os.environ, {"GEMINI_CLI_USER": "env@example.com"})
    def test_resolve_user_email_env_priority(self):
        """Verify environment variable has second priority."""
        result = UserResolver.resolve_user_email()
        assert result == "env@example.com"

    def test_resolve_user_email_settings_priority(self):
        """Verify stored settings have third priority."""

        def mock_getter():
            return "stored@example.com"

        result = UserResolver.resolve_user_email(settings_getter=mock_getter)
        assert result == "stored@example.com"

    def test_resolve_user_email_none_fallback(self):
        """Verify fallback to None when no user configured."""
        result = UserResolver.resolve_user_email()
        assert result is None


class TestOAuthAutomator:
    """Tests for the OAuthAutomator class."""

    def test_oauth_automator_init(self):
        """Verify OAuthAutomator initializes with correct debug port."""
        automator = OAuthAutomator(debug_port=9999)
        assert automator.debug_port == 9999

    def test_oauth_automator_default_port(self):
        """Verify OAuthAutomator uses default port 9222."""
        automator = OAuthAutomator()
        assert automator.debug_port == 9222

    @patch("geminpy.browser.automation.aiohttp.ClientSession")
    @patch("geminpy.browser.automation.async_playwright")
    @pytest.mark.asyncio
    async def test_connect_playwright_success(self, mock_playwright, mock_session_class):
        """Test successful Playwright connection to Chrome."""
        # Mock the aiohttp ClientSession and response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser"})

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        # Mock Playwright components
        mock_pw = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_pw)
        mock_browser = AsyncMock()
        mock_pw.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)

        # Mock browser context and page
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_page.url = "https://accounts.google.com/signin/oauth"
        mock_context.pages = [mock_page]
        mock_browser.contexts = [mock_context]

        automator = OAuthAutomator()
        pw, page = await automator._connect_playwright()

        assert pw == mock_pw
        assert page == mock_page
        mock_page.bring_to_front.assert_called_once()

    @patch("geminpy.browser.automation.asyncio.sleep", new_callable=AsyncMock)
    @patch("geminpy.browser.automation.aiohttp.ClientSession")
    @patch("geminpy.browser.automation.async_playwright")
    @pytest.mark.asyncio
    async def test_connect_playwright_no_oauth_page(self, mock_playwright, mock_session_class, mock_sleep):
        """Test failure when no OAuth page is found."""
        # Mock the aiohttp ClientSession and response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser"})

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        # Mock Playwright components
        mock_pw = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_pw)
        mock_browser = AsyncMock()
        mock_pw.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)

        # Mock browser context with no OAuth pages
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"  # Not an OAuth page
        mock_context.pages = [mock_page]
        mock_browser.contexts = [mock_context]

        automator = OAuthAutomator()

        with pytest.raises(AuthenticationError, match="Could not find a Google Accounts page"):
            await automator._connect_playwright()

        # Verify sleep was called (indicating the retry loop ran)
        assert mock_sleep.call_count == 8  # Should retry 8 times
