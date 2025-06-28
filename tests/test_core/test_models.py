# this_file: tests/test_core/test_models.py
"""Tests for model name resolution."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from geminpy.core.models import (
    _FALLBACK_MODELS,
    _get_npm_global_root,
    _parse_gemini_models,
    resolve_model_name,
)


class TestModelResolution:
    """Test model name resolution functionality."""

    def test_resolve_pro_shortcut(self):
        """Test that 'pro' resolves to a gemini pro model."""
        result = resolve_model_name("pro")
        assert result is not None
        assert "gemini" in result
        assert "pro" in result.lower()

    def test_resolve_flash_shortcut(self):
        """Test that 'flash' resolves to a gemini flash model."""
        result = resolve_model_name("flash")
        assert result is not None
        assert "gemini" in result
        assert "flash" in result.lower()

    def test_resolve_case_insensitive(self):
        """Test that shortcuts are case-insensitive."""
        pro_lower = resolve_model_name("pro")
        pro_upper = resolve_model_name("PRO")
        pro_mixed = resolve_model_name("Pro")

        assert pro_lower == pro_upper == pro_mixed

        flash_lower = resolve_model_name("flash")
        flash_upper = resolve_model_name("FLASH")
        flash_mixed = resolve_model_name("Flash")

        assert flash_lower == flash_upper == flash_mixed

    def test_passthrough_other_models(self):
        """Test that non-shortcut model names pass through unchanged."""
        assert resolve_model_name("gemini-1.5-ultra") == "gemini-1.5-ultra"
        assert resolve_model_name("some-other-model") == "some-other-model"

    def test_resolve_none(self):
        """Test that None returns None."""
        assert resolve_model_name(None) is None


class TestNpmGlobalRoot:
    """Test npm global root resolution."""

    @patch("subprocess.run")
    def test_get_npm_global_root_success(self, mock_run):
        """Test successful npm root resolution."""
        mock_run.return_value = MagicMock(
            stdout="/usr/local/lib/node_modules",
            returncode=0,
        )

        result = _get_npm_global_root()
        assert result == Path("/usr/local/lib/node_modules")
        mock_run.assert_called_once_with(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_npm_global_root_failure(self, mock_run):
        """Test npm root resolution when npm is not available."""
        mock_run.side_effect = FileNotFoundError()

        result = _get_npm_global_root()
        assert result is None


class TestParseGeminiModels:
    """Test parsing models from Gemini CLI."""

    @patch("geminpy.core.models._get_npm_global_root")
    def test_parse_models_no_npm_root(self, mock_get_root):
        """Test parsing when npm root is not found."""
        mock_get_root.return_value = None

        result = _parse_gemini_models()
        assert result == _FALLBACK_MODELS

    @patch("geminpy.core.models._get_npm_global_root")
    @patch("pathlib.Path.exists")
    def test_parse_models_file_not_found(self, mock_exists, mock_get_root):
        """Test parsing when models.js file doesn't exist."""
        mock_get_root.return_value = Path("/usr/local/lib/node_modules")
        mock_exists.return_value = False

        result = _parse_gemini_models()
        assert result == _FALLBACK_MODELS

    @patch("geminpy.core.models._get_npm_global_root")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_parse_models_success(self, mock_read_text, mock_exists, mock_get_root):
        """Test successful parsing of models.js."""
        mock_get_root.return_value = Path("/usr/local/lib/node_modules")
        mock_exists.return_value = True
        mock_read_text.return_value = """
export const DEFAULT_GEMINI_MODEL = 'gemini-2.5-pro';
export const DEFAULT_GEMINI_FLASH_MODEL = 'gemini-2.5-flash';
export const DEFAULT_GEMINI_EMBEDDING_MODEL = 'gemini-embedding-001';
"""

        result = _parse_gemini_models()
        assert result == {
            "pro": "gemini-2.5-pro",
            "flash": "gemini-2.5-flash",
        }

    @patch("geminpy.core.models._get_npm_global_root")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_parse_models_partial_success(self, mock_read_text, mock_exists, mock_get_root):
        """Test parsing when only some models are found."""
        mock_get_root.return_value = Path("/usr/local/lib/node_modules")
        mock_exists.return_value = True
        mock_read_text.return_value = """
export const DEFAULT_GEMINI_MODEL = 'gemini-3.0-pro';
// Flash model not defined
"""

        result = _parse_gemini_models()
        assert result == {
            "pro": "gemini-3.0-pro",  # Parsed value
            "flash": "gemini-2.5-flash",  # Fallback value
        }
