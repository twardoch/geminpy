# this_file: tests/test_browser/test_chrome.py
"""Tests for the ChromeManager and ChromeTestingManager."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from geminpy.browser.chrome import ChromeManager, ChromeTestingManager
from geminpy.core.config import AppConfig, ChromeConfig


@pytest.fixture
def app_config(tmp_path):
    """Pytest fixture for a mock AppConfig."""
    with patch("geminpy.core.config.user_data_dir", return_value=str(tmp_path)):
        yield AppConfig()


@pytest.fixture
def chrome_testing_manager(app_config):
    """Pytest fixture for a ChromeTestingManager instance."""
    return ChromeTestingManager(app_config)


@pytest.fixture
def chrome_manager():
    """Pytest fixture for a ChromeManager instance."""
    return ChromeManager(ChromeConfig())


def test_chrome_testing_manager_get_stored_path(chrome_testing_manager):
    """Verify that the manager can retrieve a stored path."""
    test_path = "/fake/chrome/path"
    chrome_testing_manager.settings.set("chrome_testing_path", test_path)
    assert chrome_testing_manager.get_stored_path() == Path(test_path)


@patch("pathlib.Path.exists", return_value=True)
def test_ensure_available_with_stored_path(mock_exists, chrome_testing_manager):
    """Verify that ensure_available returns a stored path if it exists."""
    test_path = "/fake/chrome/path"
    chrome_testing_manager.settings.set("chrome_testing_path", str(test_path))
    assert chrome_testing_manager.ensure_available() == Path(test_path)
    mock_exists.assert_called()


@patch("geminpy.browser.chrome.subprocess.run")
@patch("geminpy.browser.manager.BrowserManager.get_available_browsers", return_value=[])
def test_ensure_available_installs_if_needed(
    mock_browsers, mock_run, chrome_testing_manager, tmp_path
):
    """Verify that ensure_available installs Chrome if it's not found."""
    install_path = tmp_path / "chrome"
    mock_run.return_value.stdout = f"chrome@stable {install_path}"

    # Mock the path's existence to avoid a FileNotFoundError in the test
    with patch.object(Path, "exists", return_value=True):
        result_path = chrome_testing_manager.install()

    assert result_path == install_path
    assert chrome_testing_manager.get_stored_path() == install_path


@patch("subprocess.Popen")
def test_chrome_manager_launch(mock_popen, chrome_manager, tmp_path):
    """Verify that ChromeManager launches Chrome with the correct arguments."""
    executable_path = tmp_path / "chrome"
    chrome_manager.launch(executable_path)
    mock_popen.assert_called_once()
    args, _ = mock_popen.call_args
    assert str(executable_path) in args[0]
    assert (
        f"--remote-debugging-port={chrome_manager.config.debug_port}" in args[0]
    )


@patch("requests.get")
def test_chrome_manager_is_cdp_ready(mock_get, chrome_manager):
    """Verify that is_cdp_ready correctly checks the CDP endpoint."""
    mock_get.return_value.status_code = 200
    assert chrome_manager.is_cdp_ready() is True

    mock_get.side_effect = requests.RequestException
    assert chrome_manager.is_cdp_ready() is False


@patch("requests.get")
@patch("asyncio.sleep", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_chrome_manager_wait_for_cdp(
    mock_sleep, mock_get, chrome_manager
):
    """Verify that wait_for_cdp waits for a successful connection."""
    mock_get.return_value.status_code = 200
    await chrome_manager.wait_for_cdp()
    mock_get.assert_called_once()
    mock_sleep.assert_not_called()
