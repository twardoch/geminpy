# this_file: tests/test_browser/test_manager.py
"""Tests for the BrowserManager."""

from unittest.mock import MagicMock, patch

from geminpy.browser.manager import BrowserManager


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_get_current_default(mock_run, mock_require):
    """Verify that get_current_default correctly parses macdefaultbrowsy output."""
    mock_process = MagicMock()
    mock_process.stdout = "safari\n* chrome\nfirefox\n"
    mock_run.return_value = mock_process

    default_browser = BrowserManager.get_current_default()
    assert default_browser == "chrome"
    mock_require.assert_called_once()


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_get_current_default_none(mock_run, mock_require):
    """Verify that get_current_default handles empty output."""
    mock_process = MagicMock()
    mock_process.stdout = ""
    mock_run.return_value = mock_process

    default_browser = BrowserManager.get_current_default()
    assert default_browser is None
    mock_require.assert_called_once()


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_get_available_browsers(mock_run, mock_require):
    """Verify that get_available_browsers correctly parses macdefaultbrowsy output."""
    mock_process = MagicMock()
    mock_process.stdout = "safari\n* chrome\nfirefox\n"
    mock_run.return_value = mock_process

    browsers = BrowserManager.get_available_browsers()
    assert browsers == ["safari", "chrome", "firefox"]
    mock_require.assert_called_once()


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_set_default_success(mock_run, mock_require):
    """Verify that set_default calls macdefaultbrowsy with the correct arguments."""
    # Mock get_current_default to return different browser
    mock_process = MagicMock()
    mock_process.stdout = "safari\n* chrome\nfirefox\n"
    mock_run.return_value = mock_process

    result = BrowserManager.set_default("firefox")
    assert result is True
    assert mock_run.call_count == 2  # One for get_current_default, one for set
    mock_require.assert_called()


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_set_default_already_default(mock_run, mock_require):
    """Verify that set_default returns True without calling CLI if browser is already default."""
    # Mock get_current_default to return the same browser
    mock_process = MagicMock()
    mock_process.stdout = "safari\n* firefox\nchrome\n"
    mock_run.return_value = mock_process

    result = BrowserManager.set_default("firefox")
    assert result is True
    assert mock_run.call_count == 1  # Only one call for get_current_default
    assert mock_require.call_count == 2  # Called in both methods


@patch("geminpy.browser.manager.require_command")
@patch("subprocess.run")
def test_list_browsers(mock_run, mock_require):
    """Verify that list_browsers calls macdefaultbrowsy and logs output."""
    mock_process = MagicMock()
    mock_process.stdout = "safari\n* chrome\nfirefox\n"
    mock_run.return_value = mock_process

    BrowserManager.list_browsers()
    mock_require.assert_called_once()
    mock_run.assert_called_once()
