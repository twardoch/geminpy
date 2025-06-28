# this_file: tests/test_browser/test_manager.py
"""Tests for the BrowserManager."""

from unittest.mock import MagicMock, patch

from geminpy.browser.manager import BrowserManager


@patch("geminpy.browser.manager.mdb")
def test_get_current_default(mock_mdb):
    """Verify that get_current_default correctly returns the default browser."""
    mock_mdb.get_default_browser.return_value = "chrome"

    default_browser = BrowserManager.get_current_default()
    assert default_browser == "chrome"
    mock_mdb.get_default_browser.assert_called_once()


@patch("geminpy.browser.manager.mdb")
def test_get_current_default_error(mock_mdb):
    """Verify that get_current_default handles errors gracefully."""
    mock_mdb.get_default_browser.side_effect = Exception("Test error")

    default_browser = BrowserManager.get_current_default()
    assert default_browser is None


@patch("geminpy.browser.manager.mdb")
def test_get_available_browsers(mock_mdb):
    """Verify that get_available_browsers correctly returns the browser list."""
    mock_mdb.get_browsers.return_value = ["safari", "chrome", "firefox"]

    browsers = BrowserManager.get_available_browsers()
    assert browsers == ["safari", "chrome", "firefox"]
    mock_mdb.get_browsers.assert_called_once()


@patch("geminpy.browser.manager.mdb")
def test_set_default_success(mock_mdb):
    """Verify that set_default calls macdefaultbrowsy with the correct arguments."""
    # Mock get_current_default to return different browser
    mock_mdb.get_default_browser.return_value = "chrome"
    mock_mdb.set_default_browser.return_value = None

    result = BrowserManager.set_default("firefox")
    assert result is True
    mock_mdb.get_default_browser.assert_called_once()
    mock_mdb.set_default_browser.assert_called_once_with("firefox")


@patch("geminpy.browser.manager.mdb")
def test_set_default_already_default(mock_mdb):
    """Verify that set_default returns True without setting if browser is already default."""
    # Mock get_current_default to return the same browser
    mock_mdb.get_default_browser.return_value = "firefox"

    result = BrowserManager.set_default("firefox")
    assert result is True
    mock_mdb.get_default_browser.assert_called_once()
    mock_mdb.set_default_browser.assert_not_called()


@patch("geminpy.browser.manager.mdb")
def test_list_browsers(mock_mdb):
    """Verify that list_browsers displays browsers with current marked."""
    mock_mdb.get_browsers.return_value = ["safari", "chrome", "firefox"]
    mock_mdb.get_default_browser.return_value = "chrome"

    # Just verify it doesn't raise an exception
    BrowserManager.list_browsers()
    mock_mdb.get_browsers.assert_called_once()
    mock_mdb.get_default_browser.assert_called_once()
