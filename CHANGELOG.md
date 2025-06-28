# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multi-language OAuth Support**: Enhanced OAuth button detection to support 9+ languages
  - Added support for Polish, French, German, Spanish, Italian, Russian, Japanese, and Chinese
  - Implemented multiple fallback strategies for button detection (by text, attributes, and styling)
  - Addresses issue #101 where authentication failed on non-English Google OAuth pages
- **CLI Model Shortcuts**: Added convenient shortcuts for common Gemini models
  - `-P` / `--Pro` as shortcut for `-m 'gemini-2.5-pro'`
  - `-F` / `--Flash` as shortcut for `-m 'gemini-2.5-flash'`
  - Includes warnings when shortcuts override existing model arguments
- **Enhanced Browser Management**: Improved `BrowserManager` with hanging prevention
  - Added check to prevent hanging when setting browser that's already default
  - Enhanced error handling and logging throughout browser management
  - Maintains compatibility with `macdefaultbrowser` CLI tool
- **Comprehensive Test Suite**: 45 tests with 72% overall coverage
  - Browser module tests: OAuth automation, Chrome management, browser switching
  - Gemini module tests: CLI execution, response parsing, rate limit detection
  - Core utilities tests: Platform checks, settings management, error handling
  - All tests use proper mocking and async/await patterns

### Changed
- Improved OAuth automation robustness with multi-strategy button detection
- Enhanced CLI argument handling with Fire framework
- Improved code quality with automatic linting and formatting fixes
- Enhanced error handling and type safety throughout the codebase
- **Browser Management**: Investigated using `macdefaultbrowsy` Python package but reverted to CLI approach due to incomplete package

### Technical Notes
- Attempted integration with `macdefaultbrowsy` Python package for more reliable browser management
- Package was found to be incomplete (missing core modules) so reverted to `macdefaultbrowser` CLI
- Added hanging prevention logic directly in `BrowserManager.set_default()` method
- All tests updated and passing with the CLI-based approach

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