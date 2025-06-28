# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multi-language OAuth Support**: Enhanced OAuth button detection to support 9+ languages
  - Added support for Polish, French, German, Spanish, Italian, Russian, Japanese, and Chinese
  - Implemented multiple fallback strategies for button detection (by text, attributes, and styling)
  - Added filtering to avoid clicking developer info or help links
  - Addresses issue #101 where authentication failed on non-English Google OAuth pages
- **CLI Model Shortcuts**: Added convenient shortcuts for common Gemini models
  - `-P` / `--Pro` as shortcut for `-m 'gemini-2.5-pro'`
  - `-F` / `--Flash` as shortcut for `-m 'gemini-2.5-flash'`
  - Includes warnings when shortcuts override existing model arguments
- **Interactive Mode Support**: Fixed gemini CLI interactive mode handling
  - Properly detects when no `-p` argument is provided
  - Allows gemini to handle stdin/stdout directly for interactive sessions
  - Addresses issue #102 where interactive mode would hang
- **Enhanced Browser Management**: Improved `BrowserManager` with hanging prevention
  - Added check to prevent hanging when setting browser that's already default
  - Enhanced error handling and logging throughout browser management
  - Switched to `macdefaultbrowsy` Python package instead of CLI tool
- **Comprehensive Test Suite**: 46 tests with improved coverage
  - Browser module tests: OAuth automation, Chrome management, browser switching
  - Gemini module tests: CLI execution, response parsing, rate limit detection
  - Core utilities tests: Platform checks, settings management, error handling
  - All tests use proper mocking and async/await patterns
- **API Model Parameter**: Enhanced `ask()` and `ask_async()` functions with model parameter
  - Added optional `model` parameter to programmatic API
  - Supports shortcuts: `model="pro"` for gemini-2.5-pro, `model="flash"` for gemini-2.5-flash
  - Full model names pass through unchanged (e.g., `model="gemini-1.5-ultra"`)
- **Dynamic Model Resolution**: Smart model name resolution from Gemini CLI
  - Automatically parses model constants from Google's Gemini CLI installation
  - Reads `DEFAULT_GEMINI_MODEL` and `DEFAULT_GEMINI_FLASH_MODEL` from models.js
  - Falls back to hardcoded defaults if Gemini CLI is not installed
  - Ensures shortcuts stay synchronized with Google's official model definitions
  - Cross-platform npm global directory resolution

### Changed
- Improved OAuth automation robustness with multi-strategy button detection
- Enhanced CLI argument handling with Fire framework
- Improved code quality with automatic linting and formatting fixes
- Enhanced error handling and type safety throughout the codebase
- **Browser Management**: Now uses `macdefaultbrowsy` Python package for direct API access
- **Model Shortcuts**: Centralized in `core.models` module for consistency between API and CLI

### Fixed
- Fixed button clicking reliability in OAuth flow (issue #102)
- Fixed interactive mode hanging when no prompt provided
- Fixed incorrect error messages about missing macdefaultbrowser CLI tool
- Added `macdefaultbrowsy` as a proper dependency
- Added interactive user email prompt during first-time setup (issue #103)
- Cleaned up unnecessary macdefaultbrowsy availability checks
- Fixed unnecessary gemini-2.5-flash fallback retry after normal interactive mode exit

### Technical Notes
- Switched from subprocess calls to macdefaultbrowser CLI to using macdefaultbrowsy Python package
- Interactive mode now properly passes stdin/stdout to gemini subprocess
- Button detection includes text content filtering to avoid non-signin buttons
- All tests updated to mock the Python package interface instead of subprocess calls
- First-time setup now prompts for default Google account email when Chrome for Testing is installed
- Simplified BrowserManager by removing redundant package availability checks
- Model resolution uses regex parsing of JavaScript export statements
- Added `aiohttp` dependency for async HTTP requests in OAuth automation

## [0.1.0] - 2024-07-26

### Added
- Initial release of `geminpy`.
- Ported all functionality from the original `work/gemini_wrapper.py` script.
- Created a structured Python package with a modular architecture.
- **Core**: Configuration, custom exceptions, and constants.
- **Browser Management**:
    - `BrowserManager` for macOS default browser control.
    - `ChromeTestingManager` for automatic installation and management of Chrome for Testing.
    - `ChromeManager` for launching Chrome with remote debugging enabled.
- **OAuth Automation**:
    - `OAuthAutomator` using Playwright for automated Google account selection and sign-in.
    - `UserResolver` for intelligent user account resolution from multiple sources.
- **Gemini Integration**:
    - `GeminiClient` as the main orchestrator combining all components.
    - `GeminiExecutor` for subprocess management with real-time monitoring.
    - `ResponseParser` for extracting clean responses from CLI output.
- **Utilities**:
    - Platform validation ensuring macOS compatibility.
    - Settings management using platformdirs for cross-platform storage.
    - Centralized logging with Loguru.
- **High-Level API**:
    - Simple `ask()` function for direct usage.
    - Async `call_gemini_cli()` for advanced scenarios.
- **CLI Interface**:
    - Fire-based command-line interface with Rich formatting.
    - Full backward compatibility with original script arguments.
- **Error Handling**:
    - Automatic rate limit detection and retry with fallback model.
    - Comprehensive error types for different failure scenarios.
    - Graceful degradation and informative error messages.
- **Modern Python Features**:
    - Full type hints with union syntax (str | None).
    - Async/await throughout for non-blocking operations.
    - Dataclasses for configuration management.
    - Context managers for resource cleanup.

### Technical Details
- **Dependencies**: Fire, Playwright, Requests, Platformdirs, Loguru, Rich
- **Python Support**: 3.10, 3.11, 3.12
- **Build System**: Hatchling with VCS versioning
- **Code Quality**: Ruff linting, MyPy type checking, comprehensive test suite
- **Platform**: macOS only (due to browser management requirements)

### Migration Notes
- All original `gemini_wrapper.py` functionality is preserved
- Settings are automatically migrated to new location
- CLI arguments remain identical for seamless transition
- New programmatic API available for integration use cases 