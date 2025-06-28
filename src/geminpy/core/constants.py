# this_file: src/geminpy/core/constants.py
"""Constants and enums for Geminpy."""

from enum import Enum


class AuthStatus(Enum):
    """OAuth authentication status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


class RateLimitIndicators:
    """Patterns indicating rate limit errors."""

    PATTERNS = ["429", "Quota exceeded", "rateLimitExceeded", "RESOURCE_EXHAUSTED"]


class BrowserID:
    """Browser identifiers."""

    TESTING = "testing"


# URLs and patterns
CDP_VERSION_URL = "http://localhost:{port}/json/version"
OAUTH_SIGNIN_PATTERN = r"accounts\.google\.com/signin/oauth"
SUCCESS_PATTERN = r"developers\.google\.com/gemini-code-assist/auth/auth_success_gemini"
