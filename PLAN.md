# Geminpy Streamlining Plan

## Executive Summary

This plan outlines a comprehensive approach to streamline the geminpy codebase, addressing critical bugs, improving code quality, enhancing test coverage, and establishing sustainable development practices. The project has a solid foundation but requires focused improvements in reliability, testing, and user experience.

## 1. Critical Bug Fixes (Immediate Priority)

### 1.1 Interactive Mode Output Suppression (Issue #102)

**Problem**: When running gemini CLI in interactive mode (without `-p` argument), the output is incorrectly suppressed, causing the session to appear hung.

**Root Cause**: The `GeminiClient._try_gemini_with_oauth` method captures stdout/stderr even for interactive sessions.

**Solution**:
1. Detect interactive mode by checking for absence of `-p` or `--prompt` arguments
2. When in interactive mode:
   - Pass `stdin=None, stdout=None, stderr=None` to subprocess
   - Let gemini handle I/O directly with the terminal
   - Skip response parsing since there's no programmatic output
3. Return empty string to indicate successful interactive session

**Implementation Details**:
- Modify `GeminiClient._try_gemini_with_oauth` lines 95-164
- Add `is_interactive` flag based on argument detection
- Conditionally set subprocess pipes based on mode
- Update response handling logic

### 1.2 OAuth Button Click Reliability (Issue #102)

**Problem**: The OAuth automation sometimes clicks the wrong button (developer info, help links) instead of the sign-in button.

**Root Cause**: Current selectors are too broad and don't filter out non-authentication buttons effectively.

**Solution**:
1. Implement a more robust button detection strategy:
   - Priority 1: Use Google's stable element IDs (`#submit_approve_access`)
   - Priority 2: Use specific jsname attributes for approve buttons
   - Priority 3: Filter buttons by text content to exclude help/info links
2. Add visual verification:
   - Check button position (should be in main content area)
   - Verify button styling (primary action button)
   - Ensure button is not disabled
3. Implement retry mechanism:
   - If click fails, try next selector strategy
   - Take screenshot after each attempt for debugging
   - Fail gracefully with clear error message

**Implementation Details**:
- Enhance `OAuthAutomator.run_oauth_flow` in `browser/automation.py`
- Add button validation logic before clicking
- Implement selector priority queue
- Add retry decorator with exponential backoff

### 1.3 Misleading macdefaultbrowsy Error Message

**Problem**: Error messages reference a non-existent macdefaultbrowsy CLI tool when the Python package is actually used.

**Root Cause**: Legacy error messages from when the tool used subprocess calls to a CLI.

**Solution**:
1. Update all error messages to reference the Python package
2. Remove CLI availability checks from `platform.py`
3. Update exception handling to show actual Python import/API errors
4. Clean up obsolete subprocess-related code

**Implementation Details**:
- Remove `require_command("macdefaultbrowsy")` from `check_dependencies`
- Update error messages in `BrowserManager` class
- Fix import error handling to show package installation instructions

## 2. Test Coverage Improvements

### 2.1 Critical Path Testing

**Current State**: 
- Overall coverage: ~70%
- Critical gaps: `cli.py` (0%), `gemini/client.py` (0%)
- Integration tests: Missing

**Target**: 90%+ coverage with focus on critical paths

#### 2.1.1 CLI Testing Strategy

**Approach**: Use Fire's testing utilities or mock sys.argv

**Test Cases**:
1. Basic command execution with prompt
2. Model shortcuts (-P, -F)
3. Interactive mode detection
4. Error handling for invalid arguments
5. Verbose flag propagation
6. User email specification
7. Browser quit option

**Implementation**:
```python
# tests/test_cli.py
from unittest.mock import patch, AsyncMock
from geminpy.cli import cli

class TestCLI:
    @patch('geminpy.api.call_gemini_cli')
    async def test_basic_prompt(self, mock_call):
        mock_call.return_value = "Test response"
        # Test implementation
```

#### 2.1.2 Client Orchestration Testing

**Test Scenarios**:
1. Full OAuth flow with browser management
2. Rate limit detection and retry
3. Interactive vs non-interactive mode
4. Error recovery paths
5. Browser restoration on failure
6. Chrome launch and CDP connection

**Approach**:
- Mock all external dependencies
- Test state transitions
- Verify cleanup on exceptions
- Test timeout scenarios

#### 2.1.3 Integration Testing

**New Test Suite**: `tests/integration/`

**Scenarios**:
1. End-to-end OAuth flow (with mock browser)
2. CLI to API flow
3. Settings persistence across runs
4. First-time setup flow
5. Rate limit handling with model fallback

### 2.2 Test Infrastructure Improvements

1. **Fixtures Consolidation**:
   - Create shared fixtures in `conftest.py`
   - Standardize mock objects
   - Add async test utilities

2. **Test Data Management**:
   - Create test data directory
   - Add sample responses
   - Mock OAuth pages

3. **Coverage Configuration**:
   - Add branch coverage requirements
   - Exclude test files from coverage
   - Set minimum coverage thresholds

## 3. Code Quality Enhancements

### 3.1 Configuration Management

**Current Issues**:
- Hardcoded timeouts scattered throughout code
- Magic numbers without explanation
- Configuration spread across multiple modules

**Solution Architecture**:
```python
# core/config.py enhancement
@dataclass
class TimeoutConfig:
    chrome_launch: int = 30
    cdp_ready: int = 30
    oauth_flow: int = 120
    button_click: int = 5
    process_monitor: int = 300

@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_factor: float = 2.0
    max_delay: int = 60
```

**Implementation**:
1. Centralize all timeouts in config
2. Add environment variable overrides
3. Document each configuration option
4. Add validation for config values

### 3.2 Logging Standardization

**Current State**: Mixed logging patterns, inconsistent levels

**Standards to Implement**:
1. **Debug**: Detailed flow information
2. **Info**: Major operations (browser launch, OAuth start)
3. **Warning**: Recoverable issues (retry attempts)
4. **Error**: Failures requiring user attention
5. **Critical**: Unrecoverable errors

**Logging Format**:
```python
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)
```

### 3.3 Error Handling Patterns

**Standardize on**:
1. Always use specific exceptions
2. Chain exceptions with `from e`
3. Log before re-raising
4. Provide actionable error messages
5. Clean up resources in finally blocks

**Example Pattern**:
```python
try:
    result = await operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise OperationError("User-friendly message") from e
finally:
    await cleanup()
```

### 3.4 Type Safety Improvements

1. **Add missing type hints**:
   - Complete all function signatures
   - Add return type annotations
   - Use Protocol types for interfaces

2. **Enable stricter mypy**:
   - `disallow_untyped_defs = true`
   - `warn_return_any = true`
   - `strict_optional = true`

3. **Runtime validation**:
   - Add pydantic models for complex data
   - Validate user inputs
   - Type check at API boundaries

## 4. Architecture Improvements

### 4.1 Dependency Injection

**Current**: Hard dependencies between modules

**Improved Design**:
```python
class GeminiClient:
    def __init__(
        self,
        config: AppConfig,
        browser_manager: BrowserManager | None = None,
        oauth_automator: OAuthAutomator | None = None,
        executor: GeminiExecutor | None = None,
    ):
        self.browser_manager = browser_manager or BrowserManager()
        self.oauth_automator = oauth_automator or OAuthAutomator()
        self.executor = executor or GeminiExecutor(config.gemini.executable)
```

**Benefits**:
- Easier testing with mock injection
- Flexible composition
- Clear dependencies

### 4.2 Event-Driven Architecture

**Add event system for**:
1. OAuth flow progress
2. Process monitoring updates
3. Rate limit detection
4. Browser state changes

**Implementation**:
```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class EventType(Enum):
    OAUTH_STARTED = "oauth_started"
    OAUTH_COMPLETED = "oauth_completed"
    RATE_LIMIT_DETECTED = "rate_limit_detected"
    
@dataclass
class Event:
    type: EventType
    data: dict
    
class EventBus:
    def subscribe(self, event_type: EventType, handler: Callable):
        pass
    
    def publish(self, event: Event):
        pass
```

### 4.3 Plugin System

**Future-proof with plugin architecture**:
1. Model providers (beyond Gemini)
2. Authentication strategies
3. Output formatters
4. Custom retry strategies

## 5. Performance Optimizations

### 5.1 Async Optimizations

1. **Concurrent Operations**:
   - Launch Chrome while checking npm
   - Parallel file I/O operations
   - Batch API calls where possible

2. **Connection Pooling**:
   - Reuse aiohttp session
   - Keep CDP connection alive
   - Cache browser instance

### 5.2 Startup Time Improvements

1. **Lazy Imports**:
   - Import heavy modules only when needed
   - Defer playwright import until OAuth required
   - Load config on demand

2. **Caching**:
   - Cache npm root resolution
   - Store parsed models.js results
   - Remember browser state

### 5.3 Memory Usage

1. **Resource Cleanup**:
   - Proper context managers everywhere
   - Explicit browser cleanup
   - Process termination on exit

2. **Stream Processing**:
   - Handle large outputs in chunks
   - Limit response buffer size
   - Clean up temporary files

## 6. User Experience Enhancements

### 6.1 Better Error Messages

**Template**:
```
Error: {what_happened}
Reason: {why_it_happened}
Solution: {what_to_do}
Details: {technical_info}
```

**Examples**:
```
Error: Could not connect to Chrome
Reason: Chrome for Testing is not installed
Solution: Run 'geminpy' again to auto-install Chrome
Details: Expected at /Applications/Google Chrome for Testing.app
```

### 6.2 Progress Indicators

1. **Rich progress bars for**:
   - Chrome installation
   - OAuth flow steps
   - Long-running queries

2. **Status messages**:
   - Clear operation descriptions
   - Success confirmations
   - Estimated time remaining

### 6.3 Interactive Features

1. **Setup wizard**:
   - Guide through first-time setup
   - Validate configuration
   - Test connectivity

2. **Diagnostics command**:
   - Check all dependencies
   - Verify OAuth setup
   - Test Gemini connectivity

## 7. Documentation Improvements

### 7.1 API Reference

Generate comprehensive API docs:
1. Install sphinx-autodoc
2. Document all public APIs
3. Add usage examples
4. Include error handling guides

### 7.2 Architecture Documentation

Create diagrams for:
1. Component interaction
2. OAuth flow sequence
3. Error handling paths
4. Configuration hierarchy

### 7.3 Troubleshooting Guide

Comprehensive guide covering:
1. Common errors and solutions
2. Debug mode usage
3. Log interpretation
4. Filing bug reports

## 8. Development Workflow Improvements

### 8.1 Pre-commit Hooks

Configure:
1. Code formatting (black, isort)
2. Linting (ruff)
3. Type checking (mypy)
4. Test execution
5. Documentation building

### 8.2 CI/CD Pipeline

GitHub Actions for:
1. Test matrix (Python 3.10, 3.11, 3.12)
2. Coverage reporting
3. Security scanning
4. Release automation
5. Documentation deployment

### 8.3 Release Process

1. Automated changelog generation
2. Version bumping
3. Tag creation
4. PyPI publishing
5. GitHub release notes

## 9. Security Enhancements

### 9.1 Input Validation

1. Sanitize all user inputs
2. Validate file paths
3. Escape shell commands
4. Limit resource usage

### 9.2 Secure Communication

1. Verify CDP connection
2. Validate OAuth redirects
3. Secure temporary files
4. Clear sensitive data

### 9.3 Audit Logging

1. Log security events
2. Track OAuth attempts
3. Monitor resource usage
4. Detect anomalies

## 10. Future Roadmap

### Phase 1: Stability (Current)
- Fix critical bugs
- Improve test coverage
- Standardize code patterns

### Phase 2: Enhancement
- Plugin system
- Performance optimizations
- Advanced features

### Phase 3: Expansion
- Multi-platform support
- Additional AI providers
- Enterprise features

## Implementation Priority

1. **Week 1**: Critical bug fixes (1.1-1.3)
2. **Week 2**: Test coverage for critical paths (2.1)
3. **Week 3**: Configuration and logging standardization (3.1-3.2)
4. **Week 4**: Architecture improvements (4.1-4.2)
5. **Month 2**: Performance and UX enhancements
6. **Month 3**: Documentation and workflow improvements

## Success Metrics

1. **Quality**:
   - 90%+ test coverage
   - 0 critical bugs
   - <5% failure rate

2. **Performance**:
   - <2s startup time
   - <5s OAuth flow
   - <100MB memory usage

3. **Usability**:
   - Clear error messages
   - Intuitive CLI
   - Comprehensive docs

4. **Maintainability**:
   - Consistent code style
   - Modular architecture
   - Automated workflows

This plan provides a clear path to transform geminpy from a functional prototype to a production-ready, maintainable, and user-friendly tool.