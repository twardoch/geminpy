# geminpy

**Automated OAuth wrapper for Google's Gemini CLI on macOS**

`geminpy` eliminates the manual authentication steps required by Google's `gemini` CLI tool. It automatically handles the entire OAuth flow - from browser management to account selection - letting you use Gemini programmatically without interruption.

## Why It Exists

Google's official `gemini` CLI requires manual OAuth authentication through a web browser each time you use it. This makes automation impossible and interrupts workflows. `geminpy` solves this by:

1. **Automating the OAuth dance** - No manual clicking through Google's authentication screens
2. **Managing browser contexts** - Uses isolated Chrome for Testing to avoid conflicts
3. **Handling rate limits gracefully** - Automatically retries with flash model when rate limited
4. **Providing clean outputs** - Filters authentication noise from responses

## What It Does

`geminpy` acts as a transparent wrapper around the official `gemini` CLI, adding automation capabilities:

- **Drop-in CLI replacement**: Use it exactly like the original `gemini` command
- **Programmatic API**: Call Gemini from Python code with `ask()` function
- **Multi-language support**: Handles OAuth pages in 9+ languages
- **Smart user detection**: Remembers your preferred Google account
- **Rate limit resilience**: Automatic fallback to `gemini-2.5-flash` when quota exceeded
- **Browser isolation**: Uses Chrome for Testing to avoid disrupting your main browser

## How It Works

### Technical Architecture

The package orchestrates several components to achieve seamless automation:

```
User Request → GeminiClient → Browser Setup → OAuth Automation → Gemini CLI → Response
                     ↓              ↓               ↓                ↓
              BrowserManager  ChromeManager  OAuthAutomator  GeminiExecutor
                     ↓              ↓               ↓                ↓
              macdefaultbrowser  Chrome CDP    Playwright      subprocess
```

### Automation Flow

1. **Browser Preparation**

   - Installs Chrome for Testing if needed (via `@puppeteer/browsers`)
   - Saves current default browser
   - Temporarily switches to Chrome for Testing

2. **OAuth Automation**

   - Launches Chrome with remote debugging (`--remote-debugging-port=9222`)
   - Starts `gemini` CLI which opens OAuth URL
   - Playwright connects via Chrome DevTools Protocol
   - Automatically clicks your Google account
   - Detects and clicks sign-in button (multi-language, multi-strategy)
   - Waits for authentication success

3. **Execution & Monitoring**

   - Monitors gemini process output in real-time
   - Detects rate limits (429, quota exceeded, etc.)
   - Automatically retries with fallback model if needed
   - Extracts clean response from CLI output

4. **Cleanup**
   - Restores original default browser
   - Optionally quits Chrome
   - Returns pure response text

### Key Components

- **`browser.manager`**: Controls macOS default browser via `macdefaultbrowser`
- **`browser.chrome`**: Manages Chrome for Testing installation and lifecycle
- **`browser.automation`**: Playwright-based OAuth flow automation
- **`gemini.client`**: Main orchestrator coordinating all components
- **`gemini.executor`**: Subprocess management with real-time monitoring
- **`gemini.parser`**: Response extraction and cleaning

## Installation

### Prerequisites

**macOS only** - Browser automation requires macOS-specific tools.

# Install geminpy

```bash
uv pip install geminpy
```

One-time setup: Install Playwright browsers

```bash
playwright install chromium
```

## Usage

### CLI Usage

Use exactly like the original `gemini` CLI:

```bash
# Ask a question
geminpy -p "Explain Python decorators"

# Use specific model with new shortcuts
geminpy -P -p "Write a Python function"  # Uses gemini-2.5-pro
geminpy -F -p "Quick question"           # Uses gemini-2.5-flash

# Traditional model selection still works
geminpy -m "gemini-pro" -p "Complex analysis"

# Enable verbose logging
geminpy --verbose -p "Debug this"

# Quit Chrome after completion
geminpy --quit-chrome -p "One-off query"
```

### Programmatic Usage

```python
from geminpy import ask

# Simple question-answer
response = ask("Explain quantum computing")
print(response)

# Async usage with full control
import asyncio
from geminpy import call_gemini_cli

async def main():
    response = await call_gemini_cli(
        gemini_args=["-m", "gemini-pro", "-p", "Your prompt"],
        user="your.email@gmail.com",
        verbose=True,
        quit_chrome=True
    )
    print(response)

asyncio.run(main())
```

## Configuration

### User Account Resolution

`geminpy` determines which Google account to use in this priority order:

1. **CLI argument**: `--user="you@gmail.com"`
2. **Environment variable**: `GEMINI_CLI_USER="you@gmail.com"`
3. **Stored settings**: From previous successful authentication
4. **First available**: Uses first Google account found

### Settings Storage

Settings are automatically persisted to:

```
~/Library/Application Support/com.twardoch.chrometesting/settings.json
```

Contains:

- Chrome for Testing executable path
- Last used Google account email

## Advanced Features

### Multi-Language OAuth Support

Detects sign-in buttons in multiple languages:

- English, Polish, French, German, Spanish
- Italian, Russian, Japanese, Chinese
- Falls back to attribute and style-based detection

### Rate Limit Handling

Automatic detection and retry logic:

```
Original request → Rate limit detected → Retry with gemini-2.5-flash → Final response
```

### Browser Isolation

- Uses dedicated Chrome for Testing instance
- Preserves your regular browser state
- No profile contamination
- Clean OAuth every time

## Troubleshooting

### Common Issues

**"Chrome CDP did not become available"**

- Check if port 9222 is available: `lsof -i :9222`
- Look at Chrome logs: `/tmp/gemini_chrome_stderr.log`

**"Could not find sign-in button"**

- Enable verbose mode: `--verbose`
- Check screenshots: `oauth_error.png`, `oauth_error_no_signin.png`
- Ensure your Google account has Gemini access

**"macdefaultbrowser utility missing"**

```bash
brew install macdefaultbrowser
```

### Debug Mode

Enable comprehensive logging:

```bash
geminpy --verbose -p "Your question"
```

Shows:

- Chrome installation progress
- Browser switching operations
- OAuth automation steps
- Gemini CLI interactions
- Response parsing details

## Development

### Project Structure

```
src/geminpy/
├── browser/          # Browser automation components
│   ├── automation.py # OAuth flow automation
│   ├── chrome.py     # Chrome for Testing management
│   └── manager.py    # Default browser control
├── gemini/           # Gemini CLI integration
│   ├── client.py     # Main orchestrator
│   ├── executor.py   # Process management
│   └── parser.py     # Response extraction
├── core/             # Core utilities
│   ├── config.py     # Configuration
│   ├── constants.py  # Constants
│   └── exceptions.py # Custom exceptions
├── utils/            # Utilities
│   ├── platform.py   # Platform checks
│   └── storage.py    # Settings persistence
├── api.py            # Public API
└── cli.py            # CLI interface
```

### Running Tests

```bash
# Run all tests
uvx hatch run test

# Run with coverage
uvx hatch run test-cov

# Type checking
uvx hatch run type-check

# Linting
uvx hatch run lint
```

### Building

```bash
# Build package
uvx hatch build

# Install locally
uv pip install --system -e .
```

## Security

- **No credential storage** - Only stores email preference
- **Local automation only** - All OAuth happens on your machine
- **Temporary browser access** - Restored after each use
- **Process isolation** - Chrome runs in separate process

## Requirements

- **Platform**: macOS (Darwin) only
- **Python**: 3.10, 3.11, or 3.12
- **System**: `macdefaultbrowser` utility
- **Browser**: Chrome for Testing (auto-installed)

## License

MIT License - see LICENSE file for details.

