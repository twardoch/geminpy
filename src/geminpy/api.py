# this_file: src/geminpy/api.py
"""High-level API for Geminpy."""

import asyncio
from pathlib import Path

from geminpy.core.config import AppConfig
from geminpy.core.exceptions import GeminiError
from geminpy.core.models import resolve_model_name
from geminpy.gemini.client import GeminiClient
from geminpy.utils.logging import setup_logging
from geminpy.utils.platform import check_dependencies


async def call_gemini_cli(
    gemini_args: list[str],
    user: str | None = None,
    gemini_executable: str | Path = "gemini",
    quit_browser: bool = False,
    verbose: bool = False,
    retry: bool = False,
) -> str | None:
    """Core function to call gemini CLI with OAuth automation.

    Args:
        gemini_args: Arguments to pass to the gemini CLI
        quit_browser: Whether to quit Chrome after execution
        user: Optional specific user email to use for authentication
        gemini_executable: Path to the gemini executable
        verbose: Enable debug logging
        retry: Enable automatic retry on API failures (rate limits)

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
        retry_on_failure=retry,
    )
    config.gemini.executable = gemini_executable
    config.chrome.quit_browser = quit_browser

    # Create and run client
    client = GeminiClient(config)
    return await client.execute_with_auth(gemini_args, user)


async def ask_async(
    prompt: str,
    user: str | None = None,
    model: str | None = None,
    verbose: bool = False,
    retry: bool = False,
) -> str:
    """Async version of ask.

    Args:
        prompt: The question/prompt to ask
        user: Optional specific user email to use for authentication
        model: Optional model name or shortcut ("pro" for gemini-2.5-pro, "flash" for gemini-2.5-flash)
        verbose: Enable debug logging
        retry: Enable automatic retry on API failures (rate limits)

    Returns:
        Clean text response from Gemini

    Raises:
        GeminiError: If authentication or API call fails
    """
    gemini_args = ["-p", prompt]

    # Add model argument if specified
    resolved_model = resolve_model_name(model)
    if resolved_model:
        gemini_args.extend(["-m", resolved_model])

    response = await call_gemini_cli(
        gemini_args=gemini_args,
        user=user,
        verbose=verbose,
        retry=retry,
    )

    if response is None:
        msg = "Failed to get response from Gemini"
        raise GeminiError(msg)

    return response


def ask(
    prompt: str,
    user: str | None = None,
    model: str | None = None,
    verbose: bool = False,
    retry: bool = False,
) -> str:
    """Ask Gemini a question and get a clean response.

    Args:
        prompt: The question/prompt to ask
        user: Optional specific user email to use for authentication
        model: Optional model name or shortcut ("pro" for gemini-2.5-pro, "flash" for gemini-2.5-flash)
        verbose: Enable debug logging
        retry: Enable automatic retry on API failures (rate limits)

    Returns:
        Clean text response from Gemini

    Raises:
        GeminiError: If authentication or API call fails
    """
    return asyncio.run(ask_async(prompt, user, model, verbose, retry))
