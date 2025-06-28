# this_file: tests/test_api.py
"""Tests for the high-level API."""

from geminpy.api import ask


def test_ask_importable():
    """Verify that the ask function can be imported."""
    assert callable(ask)
