# this_file: src/geminpy/gemini/executor.py
"""Manages Gemini CLI subprocess execution."""

import asyncio
import subprocess
from pathlib import Path

from loguru import logger

from geminpy.core.constants import RateLimitIndicators


class GeminiExecutor:
    """Manages Gemini CLI subprocess execution."""

    def __init__(self, executable: str | Path = "gemini"):
        """Initialize with Gemini executable path."""
        self.executable = str(executable)

    async def execute(self, args: list[str], timeout: int = 120, interactive: bool = False) -> tuple[int, str, str]:
        """Execute gemini CLI and return (returncode, stdout, stderr)."""
        # Ensure -y flag is present
        if "-y" not in args and "--yes" not in args:
            args = ["-y", *args]

        cmd = [self.executable, *args]
        logger.debug(f"Running gemini: {' '.join(cmd)}")

        # Create subprocess with appropriate I/O handling
        if interactive:
            # For interactive mode, connect stdin/stdout directly to terminal
            proc = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        else:
            # For non-interactive mode, capture stdout for parsing
            proc = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

        # Give gemini a moment to open the URL
        await asyncio.sleep(2)

        return proc, None, None  # Return process for monitoring

    def check_rate_limit(self, text: str) -> bool:
        """Check if text contains rate limit indicators."""
        return any(pattern in text for pattern in RateLimitIndicators.PATTERNS)

    async def monitor_process(self, proc: subprocess.Popen, monitor_time: int = 15) -> tuple[bool, list[str]]:
        """Monitor process for rate limits and collect stderr."""
        rate_limit_detected = False
        stderr_lines = []

        # Monitor process for up to monitor_time seconds
        start_time = asyncio.get_event_loop().time()
        while proc.poll() is None and (asyncio.get_event_loop().time() - start_time) < monitor_time:
            # Check if there's new stderr output
            if proc.stderr and proc.stderr.readable():
                try:
                    # Non-blocking read of available stderr data
                    import select

                    if select.select([proc.stderr], [], [], 0.1)[0]:
                        line = proc.stderr.readline()
                        if line:
                            stderr_lines.append(line)
                            logger.debug(f"Gemini stderr: {line.strip()}")

                            # Check for rate limit indicators
                            if self.check_rate_limit(line):
                                logger.debug("Rate limit detected in real-time output!")
                                rate_limit_detected = True
                                break
                except:
                    pass

            await asyncio.sleep(0.5)

        return rate_limit_detected, stderr_lines

    async def wait_completion(self, proc: subprocess.Popen, timeout: int = 90) -> tuple[str, str]:
        """Wait for process completion and return stdout, stderr."""
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            logger.debug(f"Gemini process completed with return code: {proc.returncode}")
            return stdout or "", stderr or ""
        except subprocess.TimeoutExpired:
            logger.debug("Gemini process timed out - terminating...")
            proc.terminate()
            raise
