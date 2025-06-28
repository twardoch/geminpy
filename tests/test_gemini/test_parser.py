# this_file: tests/test_gemini/test_parser.py
"""Tests for the ResponseParser."""

from geminpy.gemini.parser import ResponseParser


class TestResponseParser:
    """Tests for the ResponseParser class."""

    def test_extract_clean_response_with_auth_noise(self):
        """Verify that auth-related lines are filtered out."""
        parser = ResponseParser()
        stdout = """Code Assist login required
Attempting to open authentication page
Otherwise navigate to: https://accounts.google.com/o/oauth2/auth
Waiting for authentication...
Authentication successful
[dotenv@1.0.0] Loaded configuration

This is the actual model response.
It spans multiple lines.
And contains the real content.
"""
        result = parser.extract_clean_response(stdout)
        expected = "This is the actual model response.\nIt spans multiple lines.\nAnd contains the real content."
        assert result == expected

    def test_extract_clean_response_no_auth_noise(self):
        """Verify that clean output without auth noise is returned as-is."""
        parser = ResponseParser()
        stdout = "Simple response without any authentication noise."
        result = parser.extract_clean_response(stdout)
        assert result == "Simple response without any authentication noise."

    def test_extract_clean_response_empty_input(self):
        """Verify that empty input returns None."""
        parser = ResponseParser()
        result = parser.extract_clean_response("")
        assert result is None

    def test_extract_clean_response_only_auth_noise(self):
        """Verify that input with only auth noise returns None."""
        parser = ResponseParser()
        stdout = """Code Assist login required
Attempting to open authentication page
Authentication successful
[dotenv@1.0.0] Loaded configuration
"""
        result = parser.extract_clean_response(stdout)
        assert result is None

    def test_extract_clean_response_mixed_content(self):
        """Verify that mixed content with auth noise in between is handled correctly."""
        parser = ResponseParser()
        stdout = """Here is some initial content.
Code Assist login required
Authentication successful
More content after auth.
[dotenv@1.0.0] Loaded configuration
Final content line.
"""
        result = parser.extract_clean_response(stdout)
        expected = "Here is some initial content.\nMore content after auth.\nFinal content line."
        assert result == expected

    def test_extract_clean_response_with_whitespace(self):
        """Verify that leading/trailing whitespace is handled correctly."""
        parser = ResponseParser()
        stdout = """
Code Assist login required
   This is the response.
   Another line.

"""
        result = parser.extract_clean_response(stdout)
        expected = "This is the response.\nAnother line."
        assert result == expected
