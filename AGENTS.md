

## 1. Project Overview

This is a Python package called `geminpy` that appears to be a wrapper/automation tool for Google's Gemini CLI. The codebase includes:
- Old code that needs to be ported is in `work/gemini_wrapper.py`
- That code needs to be ported into `src/geminpy/` and suitably refactored.
- Modern Python packaging with Hatch build system
- Comprehensive testing and linting setup

## 2. Key Commands

### 2.1. Development

```bash
# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Type checking
hatch run type-check

# Linting
hatch run lint

# Format code
hatch run fmt

# Fix code issues (including unsafe fixes)
hatch run fix

# Run a single test
hatch run pytest tests/test_package.py::test_name
```

### 2.2. Environment-specific Commands

```bash
# Run all lint checks
hatch env run lint:all

# Build documentation
hatch env run docs:build

# Run CI tests (with XML coverage)
hatch env run ci:test
```

### 2.3. From .cursorrules - After Python changes run:

```bash
fd -e py -x autoflake {}; fd -e py -x pyupgrade --py311-plus {}; fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {}; fd -e py -x ruff format --respect-gitignore --target-version py311 {}; python -m pytest;
```

## 3. Architecture

### 3.1. Package Structure
- **src/geminpy/**: Main package source
  - `geminpy.py`: Core module
  - `__version__.py`: Dynamic version from VCS
- **work/**: Old `gemini_wrapper.py` 
- **tests/**: Test suite

### 3.2. Key Dependencies

- Build: Hatchling with hatch-vcs for version control
- Testing: pytest, pytest-cov, pytest-xdist, pytest-benchmark
- Linting: ruff (extensive rules), mypy (strict mode)
- Formatting: isort, pyupgrade, absolufy-imports
- Documentation: sphinx, sphinx-rtd-theme, myst-parser

### 3.3. Chrome Automation Component
The old `work/gemini_wrapper.py` script:
- Automates Google OAuth flow for Gemini CLI
- Manages Chrome for Testing installation
- Uses Playwright for browser automation
- Handles rate limiting with automatic fallback to flash model
- Stores settings in user data directory

We need to port this code into `src/geminpy/` and suitably refactor it.

## 4. Development Guidelines

- Use `uv pip`, never `pip`
- Use `python -m` when running code
- Write clear docstrings and descriptive names
- Use type hints in simplest form (list, dict, | for unions)
- Use f-strings and structural pattern matching
- Add verbose loguru-based logging
- For CLI scripts, use fire & rich
- Include `this_file` record near top of files
- Minimize confirmations, iterate gradually
- Handle failures gracefully with retries/fallbacks
- Modularize repeated logic into single-purpose functions

## 5. Configuration

### 5.1. Tool Configurations (pyproject.toml)
- **Pytest**: Configured with branch coverage, async support
- **Coverage**: Branch coverage enabled, parallel support
- **Mypy**: Strict mode with comprehensive type checking
- **Ruff**: Extensive linting rules covering security, style, complexity
- **Pre-commit**: Hook manager for code quality

### 5.2. Environment Support
- Python 3.10, 3.11, 3.12
- macOS-specific features in Chrome automation tool
- Git repository with VCS-based versioning

## 6. Old Gemini CLI OAuth Automation Wrapper

An automated OAuth wrapper for Google's `gemini` CLI tool on macOS that eliminates the need for manual authentication steps.

## 7. Overview

The `gemini_wrapper.py` script automates the complete Google OAuth flow for the `gemini` CLI by:

1. **Installing Chrome for Testing** if not available (using `@puppeteer/browsers`)
2. **Temporarily switching default browser** to Chrome for Testing (using `macdefaultbrowsy`)
3. **Launching Chrome** in remote debugging mode (port 9222)
4. **Running the `gemini` CLI** with your specified arguments
5. **Automating OAuth screens** via Playwright-over-CDP - selecting your account and clicking "Sign in"
6. **Restoring original browser** and optionally quitting Chrome when done

## 8. Key Features

### 8.1. 🔐 **Seamless Authentication**
- Automatically handles Google OAuth flow without manual intervention
- Supports specific user account selection via multiple configuration methods
- Remembers your preferred account across sessions

### 8.2. 🌐 **Smart Browser Management**
- Uses Chrome for Testing to avoid conflicts with your regular browser
- Automatically installs Chrome for Testing if needed
- Temporarily switches default browser for OAuth, then restores it

### 8.3. 🔄 **Rate Limit Handling**
- Detects API rate limits in real-time
- Automatically retries with `gemini-2.5-flash` model when rate limited
- Graceful failure handling with informative error messages

### 8.4. 📊 **Clean Response Extraction**
- Filters out authentication noise from gemini CLI output
- Returns clean model responses for programmatic use
- Preserves original CLI behavior for interactive use

## 9. Installation & Requirements

### 9.1. Prerequisites

**macOS only** - This tool requires macOS (Darwin) due to browser management dependencies.

#### 9.1.1. Install required tools:
```bash
# Install macdefaultbrowsy utility
brew install macdefaultbrowsy

# Install Playwright browsers (one-time setup)
playwright install chromium
```

#### 9.1.2. Dependencies (auto-installed via uv):
- `fire>=0.5.0` - CLI interface
- `playwright>=1.43.0` - Browser automation
- `requests>=2.31.0` - HTTP requests
- `platformdirs>=4.0.0` - Cross-platform directories
- `loguru>=0.7.0` - Logging

## 10. Usage

### 10.1. CLI Interface (Direct Replacement)

Use exactly like the regular `gemini` CLI, but with automatic OAuth:

```bash
# Ask a question
./gemini_wrapper.py -p "Explain Python decorators"

# Use specific model
./gemini_wrapper.py -m "gemini-pro" -p "Write a Python function"

# With verbose logging
./gemini_wrapper.py --verbose -p "Hello world"

# Quit Chrome when done
./gemini_wrapper.py --quit-chrome -p "What's the weather?"
```

### 10.2. Programmatic Interface

```python
from gemini_wrapper import ask

# Simple question-answer
response = ask("Explain quantum computing in simple terms")
print(response)

# With specific user account
response = ask("Generate Python code", user="myemail@gmail.com")
print(response)

# With debug logging
response = ask("Help with debugging", verbose=True)
print(response)
```

### 10.3. Advanced Usage

```python
import asyncio
from gemini_wrapper import call_gemini_cli

# Full control over gemini arguments
response = await call_gemini_cli(
    gemini_args=["-m", "gemini-pro", "-p", "Your prompt here"],
    user="specific@email.com",
    verbose=True,
    quit_browser=True
)
```

## 11. User Account Configuration

The wrapper resolves your Google account in this priority order:

1. **`--user` CLI argument**: `./gemini_wrapper.py --user="you@gmail.com" -p "Hello"`
2. **`GEMINI_CLI_USER` environment variable**: `export GEMINI_CLI_USER="you@gmail.com"`
3. **Stored in settings.json**: Automatically saved from previous successful authentications
4. **First available account**: If none specified, uses the first Google account found

## 12. How It Works

### 12.1. Browser Automation Flow

1. **Setup Phase**:
   - Checks if Chrome for Testing is installed, installs if needed
   - Saves current default browser
   - Sets Chrome for Testing as temporary default

2. **Authentication Phase**:
   - Launches Chrome in debugging mode (port 9222)
   - Starts `gemini` CLI which opens OAuth URL in Chrome
   - Playwright connects to Chrome via Chrome DevTools Protocol (CDP)
   - Automatically clicks your account and "Sign in" button

3. **Execution Phase**:
   - Waits for OAuth success redirect
   - Monitors gemini process for completion or rate limits
   - Extracts clean response from mixed CLI output

4. **Cleanup Phase**:
   - Restores original default browser
   - Optionally quits Chrome for Testing
   - Returns clean response text

### 12.2. Rate Limit Handling

When the original request hits rate limits:
```
gemini-wrapper detects: "429" or "Quota exceeded" or "rateLimitExceeded"
↓
Automatically retries with: gemini -m "gemini-2.5-flash" [your-args]
↓
Returns response or fails gracefully
```

## 13. Old File Structure

```
work/
├── gemini_wrapper.py          # Main automation script
└── settings.json              # Auto-generated settings (Chrome path, user email)
```

## 14. Settings Storage

Settings are automatically stored in:
- **Path**: `~/Library/Application Support/com.twardoch.chrometesting/settings.json`
- **Contents**: Chrome for Testing executable path, preferred user email
- **Auto-managed**: No manual editing required

## 15. Troubleshooting

### 15.1. Common Issues

**"Chrome CDP did not become available"**
- Another Chrome instance may be running without `--remote-debugging-port`
- Check if port 9222 is blocked: `curl http://localhost:9222/json/version`
- Look at debug logs: `/tmp/gemini_chrome_stderr.log`

**"macdefaultbrowsy utility missing"**
```bash
brew install macdefaultbrowsy
```

**Authentication fails**
- Enable verbose mode: `--verbose` to see detailed OAuth flow
- Check screenshots saved to: `oauth_error*.png`
- Verify your Google account has access to Gemini

**Rate limits persist**
- The wrapper automatically tries `gemini-2.5-flash` on rate limits
- Wait a few minutes before retrying
- Check your Gemini API quota in Google Cloud Console

### 15.2. Debug Mode

Enable verbose logging to see the full automation process:

```bash
./gemini_wrapper.py --verbose -p "Your question"
```

This shows:
- Chrome installation and launch details
- Browser switching operations  
- OAuth flow step-by-step
- Gemini CLI output parsing
- Error details and screenshots

## 16. Security Notes

- **Browser isolation**: Uses Chrome for Testing, separate from your regular Chrome
- **Temporary access**: Only switches default browser during authentication
- **Local automation**: All OAuth automation happens locally via CDP
- **No credential storage**: No passwords or tokens are stored, only email preference

The wrapper provides a seamless, secure way to use Google's Gemini CLI without manual OAuth interruptions.

We need to port this code into `src/geminpy/` and suitably refactor it.


Be creative, diligent, critical, relentless & funny!