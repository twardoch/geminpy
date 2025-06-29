# geminpy

**Automated OAuth wrapper for Google's Gemini CLI on macOS**

`geminpy` streamlines your interaction with Google's `gemini` CLI by automating the often-manual OAuth 2.0 authentication process. Designed for macOS users, it intelligently manages browser contexts and handles common CLI challenges, allowing for uninterrupted programmatic use and scripting.

## Why `geminpy`?

Google's official `gemini` CLI requires users to manually authenticate through a web browser. This is cumbersome for frequent use and a blocker for automation. `geminpy` solves this by:

1.  **Automating the OAuth Dance**: No more clicking through Google's sign-in screens.
2.  **Isolating Browser Sessions**: Uses a dedicated Chrome for Testing instance, keeping your main browser profile untouched.
3.  **Handling Rate Limits Gracefully**: Detects API rate limits and can automatically retry with a less demanding model.
4.  **Providing Clean Output**: Filters authentication-related messages, giving you just the Gemini model's response.

## Target Audience

`geminpy` is for developers, scripters, and anyone on macOS who frequently uses the Gemini CLI and wants a smoother, automatable experience.

## Key Features

*   **Transparent CLI Wrapper**: Use `geminpy` as a drop-in replacement for the `gemini` command.
*   **Programmatic API**: Integrate Gemini into your Python scripts with a simple `ask()` function.
*   **Multi-Language OAuth**: Successfully navigates OAuth pages in English, Polish, French, German, Spanish, Italian, Russian, Japanese, and Chinese.
*   **Smart User Account Management**:
    *   Remembers your preferred Google account.
    *   Prompts for email during first-time setup.
    *   Resolves user via CLI arguments, environment variables, or stored settings.
*   **Rate Limit Resilience**: Automatically falls back to `gemini-2.5-flash` if the default model hits a quota.
*   **Chrome for Testing Management**:
    *   Automatically installs Chrome for Testing if not found.
    *   Manages its execution and remote debugging connection.
*   **Dynamic Model Aliases**: Uses official model names for "pro" and "flash" by parsing your local Gemini CLI installation, ensuring aliases stay current.

## Requirements

*   **Platform**: macOS (Darwin)
*   **Python**: 3.10 or newer
*   **Playwright Browsers**: A one-time setup is needed for Playwright's browser automation.
    ```bash
    playwright install chromium
    ```

## Installation

Install `geminpy` using `uv` (or `pip`):

```bash
uv pip install geminpy
```

## Quick Start

### Command-Line Interface (CLI)

Use `geminpy` just like you would use `gemini`:

```bash
# Basic prompt
geminpy -p "Explain the theory of relativity in simple terms."

# Use model shortcuts (Pro or Flash)
geminpy -P -p "Write a Python function for factorial."  # Uses Gemini Pro
geminpy -F -p "What's the capital of France?"          # Uses Gemini Flash

# Enable verbose logging for debugging
geminpy --verbose -p "Hello world"

# Automatically quit the automation browser when done
geminpy --quit-chrome -p "A quick question"
```

### Programmatic API

Integrate Gemini into your Python scripts:

```python
from geminpy import ask

# Simple query
response = ask("What is the main ingredient in bread?")
print(response)

# Query with a specific model (e.g., "pro" or "flash")
pro_response = ask("Suggest three innovative uses for AI in education.", model="pro")
print(pro_response)

# For more advanced control (async)
import asyncio
from geminpy import call_gemini_cli

async def advanced_query():
    response = await call_gemini_cli(
        gemini_args=["-m", "gemini-1.5-ultra", "-p", "Elaborate on dark matter."],
        user="your.email@example.com", # Optional: specify user
        verbose=True,
        quit_browser=True
    )
    if response is not None:
        print(response)
    else:
        print("Failed to get a response.")

if __name__ == "__main__":
    asyncio.run(advanced_query())
```

## User Account Configuration

`geminpy` resolves the Google account for OAuth in the following order of priority:

1.  **`--user` CLI Argument**: e.g., `geminpy --user="you@example.com" -p "Hello"`
2.  **`GEMINI_CLI_USER` Environment Variable**: e.g., `export GEMINI_CLI_USER="you@example.com"`
3.  **Stored Setting**: From `settings.json`, saved from a previous successful authentication or first-time setup.
4.  **First Available Account**: If none of the above are specified, `geminpy` will attempt to use the first Google account it detects on the OAuth page.

During the first-time setup (when Chrome for Testing is installed), `geminpy` will interactively prompt you to enter your preferred Google account email.

## Troubleshooting

*   **"Chrome CDP did not become available"**:
    *   Another Chrome instance might be running without remote debugging.
    *   Check if port 9222 is blocked: `curl http://localhost:9222/json/version`.
    *   Examine Chrome's error log: `/tmp/gemini_chrome_stderr.log`.
*   **"Could not find sign-in button" / Authentication Fails**:
    *   Run with `--verbose` to see detailed OAuth flow logs.
    *   Check screenshots saved on error (e.g., `oauth_error.png`, `oauth_error_no_signin.png`).
    *   Ensure your Google account has access to Gemini services.
*   **Rate Limits Persist**:
    *   `geminpy` automatically tries `gemini-2.5-flash` on rate limits.
    *   If issues continue, wait a few minutes or check your Gemini API quota in the Google Cloud Console.

## Technical Deep Dive

### How It Works: The Automation Flow

1.  **Initialization & Setup**:
    *   `GeminiClient` is initialized.
    *   Dependencies (`npx`) are checked via `check_dependencies`.
    *   User email is resolved by `UserResolver`.
    *   Model name (if using shortcuts like "pro" or "flash") is resolved by `resolve_model_name`, which dynamically parses Google's official Gemini CLI's `models.js` file to get the current default model names.

2.  **Browser Preparation**:
    *   `ChromeTestingManager` ensures Chrome for Testing is available. If not found or its path isn't stored, it installs it using `npx @puppeteer/browsers install chrome@stable --platform mac --path /Applications`. If this is the first time, it prompts for a default Google user email.
    *   `BrowserManager` (utilizing the `macdefaultbrowsy` Python package) saves the current macOS default browser.
    *   It then sets Chrome for Testing as the temporary default browser. This is crucial for the `gemini` CLI to open its OAuth URL in the correct, controlled browser instance.

3.  **Chrome Launch & Connection**:
    *   `ChromeManager` launches the Chrome for Testing executable with remote debugging enabled on a specific port (default 9222).
    *   It waits for the Chrome DevTools Protocol (CDP) endpoint to become available.

4.  **Gemini CLI and OAuth Trigger**:
    *   `GeminiExecutor` starts the `gemini` CLI as a subprocess. The CLI attempts to open an OAuth authentication URL in the (now) default browser (Chrome for Testing).

5.  **OAuth Automation via Playwright**:
    *   `OAuthAutomator` connects to the running Chrome for Testing instance via Playwright over the CDP.
    *   It identifies the Google OAuth page.
    *   **Account Selection**: It clicks the specified user account. If no user is specified, it attempts to click the first available account.
    *   **Sign-In**: It locates and clicks the "Sign in" (or equivalent in other languages) button. This step uses robust selectors like `id="submit_approve_access"` or `jsname="uRHG6"` first, falling back to other strategies if needed.
    *   It waits for the success redirect URL.

6.  **Execution Monitoring & Response Handling**:
    *   `GeminiExecutor` monitors the `gemini` CLI's output.
    *   If a rate limit is detected in the output, `GeminiClient` can automatically retry the command using the `gemini-2.5-flash` model (if no model was originally specified).
    *   `ResponseParser` cleans the raw output from the CLI, removing authentication-related messages to provide just the model's response.

7.  **Cleanup**:
    *   `BrowserManager` restores the original macOS default browser.
    *   If the `--quit-chrome` flag was used, `ChromeManager` terminates the Chrome for Testing process.

### Project Structure

```
src/geminpy/
├── api.py            # Public functions (ask, call_gemini_cli)
├── cli.py            # Command-Line Interface logic (using Fire)
├── __init__.py       # Package entry point
├── __main__.py       # For `python -m geminpy`
├── browser/
│   ├── automation.py # OAuthAutomator: Playwright logic
│   ├── chrome.py     # ChromeManager, ChromeTestingManager
│   └── manager.py    # BrowserManager: Default browser switching
├── core/
│   ├── config.py     # AppConfig, ChromeConfig, GeminiConfig dataclasses
│   ├── constants.py  # AuthStatus, RateLimitIndicators, URLs
│   ├── exceptions.py # Custom Geminpy exceptions
│   └── models.py     # Model shortcut resolution (MODEL_SHORTCUTS)
├── gemini/
│   ├── client.py     # GeminiClient: Main orchestrator
│   ├── executor.py   # GeminiExecutor: Subprocess handling
│   └── parser.py     # ResponseParser: Cleaning CLI output
└── utils/
    ├── logging.py    # Loguru setup
    ├── platform.py   # macOS checks, command requirements
    └── storage.py    # SettingsManager for settings.json
```

### Key Components & Responsibilities

*   **`GeminiClient`**: The central coordinator. It uses other components to manage the browser, run OAuth, execute Gemini, and parse the response.
*   **`OAuthAutomator`**: Employs Playwright to interact with Google's OAuth pages, selecting accounts and clicking buttons.
*   **`ChromeTestingManager`**: Handles the installation (via `npx @puppeteer/browsers`), path storage, and user email storage for Chrome for Testing.
*   **`ChromeManager`**: Launches and manages the Chrome for Testing process, ensuring its CDP port is ready.
*   **`BrowserManager`**: Uses the `macdefaultbrowsy` Python package to get/set the macOS default browser.
*   **`GeminiExecutor`**: Runs the `gemini` CLI as a subprocess, monitors its output for specific events like rate limits.
*   **`ResponseParser`**: Cleans the raw stdout from the Gemini CLI to extract the actual model response.
*   **`UserResolver`**: Determines the target Google account email based on CLI arguments, environment variables, or stored settings.
*   **Configuration Dataclasses (`AppConfig`, etc.)**: Define the structure for application, Chrome, and Gemini settings.
*   **`SettingsManager`**: Manages persistence of settings (like Chrome path and user email) in `settings.json`.
*   **`MODEL_SHORTCUTS` & `resolve_model_name`**: Dynamically determine the correct full model names for shortcuts like "pro" and "flash" by parsing the local Gemini CLI's JavaScript files.

### Settings Storage

`geminpy` stores its settings in:
`~/Library/Application Support/com.twardoch.geminpy/settings.json`

This file may contain:
*   `chrome_testing_path`: The path to the Chrome for Testing executable.
*   `gemini_cli_user`: The preferred Google account email for OAuth.

### Error Handling

`geminpy` defines custom exceptions (e.g., `AuthenticationError`, `RateLimitError`, `ChromeError`, `PlatformError`) to provide specific error information. On OAuth failures, it attempts to save a screenshot (e.g., `oauth_error.png`) for debugging.

### Security Notes

*   **Browser Isolation**: Uses Chrome for Testing, keeping automation separate from your main browser profile and history.
*   **Local Automation**: All browser interactions for OAuth occur locally on your machine via Playwright and CDP.
*   **No Credential Storage**: `geminpy` does not store passwords or authentication tokens. It only saves your preferred email address if you provide it.

## Development & Contribution

`geminpy` is built using [Hatch](https://hatch.pypa.io/).

### Setup

1.  Clone the repository.
2.  Ensure you have `uv` installed (`pip install uv`).
3.  Install dependencies in a virtual environment: `uv pip install -e .[dev,test]`

### Key Development Commands

*   **Run tests**: `uvx hatch run test`
*   **Run tests with coverage**: `uvx hatch run test-cov`
*   **Type checking (MyPy)**: `uvx hatch run type-check`
*   **Linting (Ruff)**: `uvx hatch run lint`
*   **Formatting (Ruff Format)**: `uvx hatch run fmt`
*   **Build package**: `uvx hatch build`

### Coding Conventions (from `CLAUDE.md` & `AGENTS.md`)

*   Use `uv pip` for dependency management.
*   Prefer `python -m <module>` for running modules.
*   Write clear docstrings and descriptive names.
*   Use modern type hints (e.g., `list`, `dict`, `str | None`).
*   Employ f-strings for string formatting.
*   Use Loguru for logging, with verbose options.
*   Use Fire and Rich for CLI interfaces.
*   Include a `this_file: path/to/file.py` comment near the top of Python files.
*   Modularize logic into single-purpose functions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
