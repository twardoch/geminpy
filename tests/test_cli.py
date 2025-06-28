# this_file: tests/test_cli.py
"""Tests for the CLI interface."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from geminpy.cli import cli, main


class TestCLI:
    """Test the CLI interface."""

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_basic_prompt(self, mock_call_gemini, mock_asyncio_run):
        """Test basic command execution with prompt."""
        # Setup
        mock_response = "The capital of France is Paris."
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute
        cli(p="What is the capital of France?")

        # Verify
        mock_asyncio_run.assert_called_once()
        args = mock_asyncio_run.call_args[0][0]
        assert asyncio.iscoroutine(args)

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_model_shortcut_pro(self, mock_call_gemini, mock_asyncio_run):
        """Test -P shortcut for pro model."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with -P flag
        cli(P=True, p="test prompt")

        # Verify the call
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_model_shortcut_flash(self, mock_call_gemini, mock_asyncio_run):
        """Test -F shortcut for flash model."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with -F flag
        cli(F=True, p="test prompt")

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_interactive_mode(self, mock_call_gemini, mock_asyncio_run):
        """Test interactive mode (no prompt)."""
        # Interactive mode returns empty string
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result("")
        mock_asyncio_run.return_value = ""

        # Execute without prompt
        cli()

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    @patch("geminpy.cli.console")
    def test_error_handling(self, mock_console, mock_call_gemini, mock_asyncio_run):
        """Test error handling when gemini fails."""
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(None)
        mock_asyncio_run.return_value = None

        # Execute
        cli(p="test")

        # Verify error message
        mock_console.print.assert_called_with("[red]Failed to get response from Gemini[/red]")

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_verbose_flag(self, mock_call_gemini, mock_asyncio_run):
        """Test verbose flag propagation."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with verbose
        cli(verbose=True, p="test")

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_user_email_specification(self, mock_call_gemini, mock_asyncio_run):
        """Test user email specification."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with user
        cli(user="test@example.com", p="test")

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_quit_browser_option(self, mock_call_gemini, mock_asyncio_run):
        """Test quit browser option."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with quit_browser
        cli(quit_browser=True, p="test")

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    @patch("geminpy.cli.console")
    def test_model_shortcut_warning(self, mock_console, mock_call_gemini, mock_asyncio_run):
        """Test warning when model shortcuts override existing model arg."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with both -P and existing model
        cli(P=True, m="gemini-1.5-ultra", p="test")

        # Verify warning
        mock_console.print.assert_any_call(
            "[yellow]Warning: -P/--Pro overrides any existing -m/--model argument[/yellow]"
        )

    @patch("geminpy.cli.asyncio.run")
    @patch("geminpy.cli.call_gemini_cli")
    def test_complex_gemini_args(self, mock_call_gemini, mock_asyncio_run):
        """Test passing complex arguments to gemini."""
        mock_response = "Response"
        mock_call_gemini.return_value = asyncio.Future()
        mock_call_gemini.return_value.set_result(mock_response)
        mock_asyncio_run.return_value = mock_response

        # Execute with various args
        cli(p="test", t=0.5, max_tokens=100, json=True)

        # Verify
        mock_asyncio_run.assert_called_once()

    @patch("geminpy.cli.fire.Fire")
    def test_main_entry_point(self, mock_fire):
        """Test the main entry point."""
        main()
        mock_fire.assert_called_once_with(cli)