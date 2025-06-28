# this_file: tests/test_utils/test_platform.py
"""Tests for the platform utilities."""

import subprocess
from unittest.mock import patch

import pytest

from geminpy.core.exceptions import PlatformError
from geminpy.utils.platform import (
    check_dependencies,
    require_command,
    require_macos,
)


def test_require_macos_on_mac():
    """Verify that require_macos does not raise on macOS."""
    with patch("platform.system", return_value="Darwin"):
        require_macos()  # Should not raise


def test_require_macos_on_other_os():
    """Verify that require_macos raises PlatformError on other OS."""
    with patch("platform.system", return_value="Linux"):
        with pytest.raises(PlatformError, match="currently only supports macOS"):
            require_macos()


def test_require_command_exists():
    """Verify that require_command does not raise if command exists."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        require_command("any_command", "install hint")  # Should not raise


def test_require_command_does_not_exist():
    """Verify that require_command raises PlatformError if command is missing."""
    with (
        patch("subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(PlatformError, match="Required command 'any_command' not found"),
    ):
        require_command("any_command", "install hint")


def test_check_dependencies_success():
    """Verify check_dependencies runs without error when all dependencies are met."""
    with patch("geminpy.utils.platform.require_macos") as mock_require_macos:
        with patch("geminpy.utils.platform.require_command") as mock_require_command:
            check_dependencies()
            assert mock_require_macos.called
            assert mock_require_command.call_count == 1  # Only npx now


def test_check_dependencies_missing_command():
    """Verify check_dependencies raises PlatformError if a command is missing."""
    with patch("geminpy.utils.platform.require_macos"):
        with patch("geminpy.utils.platform.require_command", side_effect=PlatformError):
            with pytest.raises(PlatformError):
                check_dependencies()
