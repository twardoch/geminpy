# this_file: src/geminpy/__init__.py
"""Geminpy - Automated OAuth wrapper for Google's Gemini CLI."""

try:
    from geminpy.__version__ import __version__
except ImportError:
    __version__ = "0.0.0"  # Default version when not installed

from geminpy.api import ask, call_gemini_cli

__all__ = ["__version__", "ask", "call_gemini_cli"]
