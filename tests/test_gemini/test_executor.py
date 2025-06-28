# this_file: tests/test_gemini/test_executor.py
"""Tests for the GeminiExecutor."""

import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from geminpy.gemini.executor import GeminiExecutor


class TestGeminiExecutor:
    """Tests for the GeminiExecutor class."""

    def test_executor_init_default(self):
        """Verify executor initializes with default gemini executable."""
        executor = GeminiExecutor()
        assert executor.executable == "gemini"

    def test_executor_init_custom(self):
        """Verify executor initializes with custom executable."""
        executor = GeminiExecutor("/custom/path/to/gemini")
        assert executor.executable == "/custom/path/to/gemini"

    @patch("subprocess.Popen")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_execute_basic(self, mock_sleep, mock_popen):
        """Test basic execute method returns process."""
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        executor = GeminiExecutor()
        proc, stdout, stderr = await executor.execute(["-p", "test prompt"])

        assert proc == mock_proc
        assert stdout is None
        assert stderr is None

        # Verify the command was constructed correctly
        expected_cmd = ["gemini", "-y", "-p", "test prompt"]
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == expected_cmd

    @patch("subprocess.Popen")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_execute_with_existing_yes_flag(self, mock_sleep, mock_popen):
        """Test that -y flag is not duplicated if already present."""
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        executor = GeminiExecutor()
        await executor.execute(["-y", "-p", "test"])

        # Verify -y wasn't duplicated
        expected_cmd = ["gemini", "-y", "-p", "test"]
        args, kwargs = mock_popen.call_args
        assert args[0] == expected_cmd

    @patch("subprocess.Popen")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_execute_with_yes_flag(self, mock_sleep, mock_popen):
        """Test that --yes flag prevents adding -y."""
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        executor = GeminiExecutor()
        await executor.execute(["--yes", "-p", "test"])

        # Verify -y wasn't added when --yes is present
        expected_cmd = ["gemini", "--yes", "-p", "test"]
        args, kwargs = mock_popen.call_args
        assert args[0] == expected_cmd

    def test_check_rate_limit_detection(self):
        """Test rate limit detection in text."""
        executor = GeminiExecutor()
        
        # Test positive cases
        assert executor.check_rate_limit("Error 429: Too many requests")
        assert executor.check_rate_limit("Quota exceeded for this request")
        assert executor.check_rate_limit("rateLimitExceeded in API call")
        assert executor.check_rate_limit("RESOURCE_EXHAUSTED error occurred")
        
        # Test negative case
        assert not executor.check_rate_limit("Normal response text")

    @patch("asyncio.get_event_loop")
    @patch("select.select")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_monitor_process_rate_limit_detected(self, mock_sleep, mock_select, mock_loop):
        """Test monitoring process that detects rate limit."""
        # Mock event loop time
        mock_loop.return_value.time.side_effect = [0, 1, 2]  # Simulate time progression
        
        # Mock process
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # Process still running
        mock_proc.stderr.readable.return_value = True
        mock_proc.stderr.readline.return_value = "Error 429: Quota exceeded\n"
        
        # Mock select to indicate stderr data available
        mock_select.return_value = ([mock_proc.stderr], [], [])
        
        executor = GeminiExecutor()
        rate_limit_detected, stderr_lines = await executor.monitor_process(mock_proc, monitor_time=5)
        
        assert rate_limit_detected is True
        assert len(stderr_lines) >= 1
        assert "429" in stderr_lines[0]

    @patch("asyncio.get_event_loop")
    @patch("select.select")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_monitor_process_no_rate_limit(self, mock_sleep, mock_select, mock_loop):
        """Test monitoring process that completes normally."""
        # Mock event loop time
        mock_loop.return_value.time.side_effect = [0, 1, 2, 3, 4, 5, 6]
        
        # Mock process that completes
        mock_proc = MagicMock()
        mock_proc.poll.side_effect = [None, None, 0]  # Running, running, completed
        mock_proc.stderr.readable.return_value = True
        mock_proc.stderr.readline.return_value = ""  # No stderr output
        
        # Mock select to indicate no stderr data
        mock_select.return_value = ([], [], [])
        
        executor = GeminiExecutor()
        rate_limit_detected, stderr_lines = await executor.monitor_process(mock_proc, monitor_time=5)
        
        assert rate_limit_detected is False
        assert len(stderr_lines) == 0

    @pytest.mark.asyncio
    async def test_wait_completion_success(self):
        """Test successful process completion."""
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("Response output", "")
        mock_proc.returncode = 0
        
        executor = GeminiExecutor()
        stdout, stderr = await executor.wait_completion(mock_proc)
        
        assert stdout == "Response output"
        assert stderr == ""
        mock_proc.communicate.assert_called_once_with(timeout=90)

    @pytest.mark.asyncio
    async def test_wait_completion_timeout(self):
        """Test process timeout handling."""
        mock_proc = MagicMock()
        mock_proc.communicate.side_effect = subprocess.TimeoutExpired("cmd", 90)
        
        executor = GeminiExecutor()
        
        with pytest.raises(subprocess.TimeoutExpired):
            await executor.wait_completion(mock_proc, timeout=90)
        
        mock_proc.terminate.assert_called_once()
