# this_file: src/geminpy/core/exceptions.py
"""Custom exceptions for Geminpy."""


class GeminiError(Exception):
    """Base exception for all Geminpy errors."""


class ChromeError(GeminiError):
    """Chrome-related errors."""


class BrowserManagementError(ChromeError):
    """Browser switching/management errors."""


class ChromeInstallationError(ChromeError):
    """Chrome for Testing installation errors."""


class AuthenticationError(GeminiError):
    """OAuth authentication errors."""


class RateLimitError(GeminiError):
    """API rate limit errors."""


class PlatformError(GeminiError):
    """Platform compatibility errors."""
