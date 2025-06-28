# this_file: src/geminpy/api.py
"""High-level API for Geminpy."""

import asyncio
from pathlib import Path

from geminpy.core.config import AppConfig
from geminpy.core.exceptions import GeminiError
from geminpy.gemini.client import GeminiClient
from geminpy.utils.logging import setup_logging
from geminpy.utils.platform import check_dependencies


async def call_gemini_cli(
    gemini_args: list[str],
    quit_chrome: bool = False,
    user: str | None = None,
    gemini_executable: str | Path = "gemini",
    verbose: bool = False,
) -> str | None:
    """Core function to call gemini CLI with OAuth automation.

    Args:
        gemini_args: Arguments to pass to the gemini CLI
        quit_chrome: Whether to quit Chrome after execution
        user: Optional specific user email to use for authentication
        gemini_executable: Path to the gemini executable
        verbose: Enable debug logging

    Returns:
        Clean response text from Gemini or None if failed

    Raises:
        GeminiError: If authentication or API call fails
    """
    # Setup logging
    setup_logging(verbose)

    # Check dependencies
    check_dependencies()

    # Create configuration
    config = AppConfig(
        verbose=verbose,
        user_email=user,
    )
    config.gemini.executable = gemini_executable
    config.chrome.quit_chrome = quit_chrome

    # Create and run client
    client = GeminiClient(config)
    return await client.execute_with_auth(gemini_args, user)


async def ask_async(
    prompt: str,
    user: str | None = None,
    verbose: bool = False,
) -> str:
    """Async version of ask.

    Args:
        prompt: The question/prompt to ask
        user: Optional specific user email to use for authentication
        verbose: Enable debug logging

    Returns:
        Clean text response from Gemini

    Raises:
        GeminiError: If authentication or API call fails
    """
    gemini_args = ["-p", prompt]
    response = await call_gemini_cli(
        gemini_args=gemini_args, user=user, verbose=verbose
    )

    if response is None:
        msg = "Failed to get response from Gemini"
        raise GeminiError(msg)

    return response


def ask(
    prompt: str,
    user: str | None = None,
    verbose: bool = False,
) -> str:
    """Ask Gemini a question and get a clean response.

    Args:
        prompt: The question/prompt to ask
        user: Optional specific user email to use for authentication
        verbose: Enable debug logging

    Returns:
        Clean text response from Gemini

    Raises:
        GeminiError: If authentication or API call fails
    """
    return asyncio.run(ask_async(prompt, user, verbose))
