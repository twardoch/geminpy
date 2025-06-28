# this_file: src/geminpy/cli.py
"""CLI interface for Geminpy using Fire and Rich."""

import asyncio
from pathlib import Path

import fire
from rich.console import Console

from geminpy.api import call_gemini_cli
from geminpy.core.models import MODEL_SHORTCUTS

console = Console()


def cli(
    quit_browser: bool = False,
    verbose: bool = False,
    user: str | None = None,
    gemini_executable: str | Path = "gemini",
    P: bool = False,
    Pro: bool = False,
    F: bool = False,
    Flash: bool = False,
    **gemini_args,
) -> None:
    """CLI interface for gemini with automated OAuth via Playwright.

    Args:
        quit_browser: Quit Chrome after execution
        verbose: Enable verbose debug logging
        user: Specific user email to use for authentication
        gemini_executable: Path to the gemini executable
        P, Pro: Shortcut for -m 'gemini-2.5-pro'
        F, Flash: Shortcut for -m 'gemini-2.5-flash'
        **gemini_args: Arguments to pass to the gemini CLI
    """
    # Handle model shortcuts
    if P or Pro:
        if "m" in gemini_args or "model" in gemini_args:
            console.print("[yellow]Warning: -P/--Pro overrides any existing -m/--model argument[/yellow]")
        gemini_args["m"] = MODEL_SHORTCUTS["pro"]
    elif F or Flash:
        if "m" in gemini_args or "model" in gemini_args:
            console.print("[yellow]Warning: -F/--Flash overrides any existing -m/--model argument[/yellow]")
        gemini_args["m"] = MODEL_SHORTCUTS["flash"]

    # Convert gemini_args dict to CLI argument list
    cli_args = []
    for key, value in gemini_args.items():
        # Use single dash for single char, double dash for multi-char
        flag = f"-{key}" if len(key) == 1 else f"--{key}"
        cli_args.append(flag)

        # Only add value if it's not a boolean True (flags don't need values)
        if value is not True:
            if value is False:
                # Skip false flags entirely
                cli_args.pop()  # Remove the flag we just added
            else:
                cli_args.append(str(value))

    # Run the command
    response = asyncio.run(
        call_gemini_cli(
            gemini_args=cli_args,
            quit_browser=quit_browser,
            user=user,
            gemini_executable=gemini_executable,
            verbose=verbose,
        )
    )

    # Handle response based on mode
    if response is not None:
        # Empty string means interactive mode completed successfully
        if response == "":
            # Interactive mode - gemini already handled I/O
            pass
        else:
            # Non-interactive mode - print the response
            console.print(response)
    else:
        console.print("[red]Failed to get response from Gemini[/red]")


def main():
    """Main entry point for the CLI."""
    fire.Fire(cli)


if __name__ == "__main__":
    main()
