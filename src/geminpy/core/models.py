# this_file: src/geminpy/core/models.py
"""Model name mapping and utilities."""

import re
import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

# Fallback model names if we can't parse from Gemini CLI
_FALLBACK_MODELS = {
    "pro": "gemini-2.5-pro",
    "flash": "gemini-2.5-flash",
}

# Cache for model shortcuts to avoid repeated parsing
_model_shortcuts_cache: dict[str, str] | None = None


def _get_npm_global_root() -> Path | None:
    """Get the npm global root directory cross-platform."""
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            check=True,
        )
        npm_root = result.stdout.strip()
        if npm_root:
            return Path(npm_root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.debug("Could not get npm global root")
    return None


def _parse_gemini_models() -> dict[str, str]:
    """Parse model constants from Gemini CLI's models.js file."""
    npm_root = _get_npm_global_root()
    if not npm_root:
        logger.debug("Using fallback models - npm root not found")
        return _FALLBACK_MODELS

    # Try to find the models.js file
    gemini_cli_path = "@google/gemini-cli/node_modules/"
    gemini_core_path = "@google/gemini-cli-core/dist/src/config/models.js"
    models_path = npm_root / gemini_cli_path / gemini_core_path

    if not models_path.exists():
        # Try alternate path without node_modules
        models_path = npm_root / "@google/gemini-cli-core/dist/src/config/models.js"

    if not models_path.exists():
        logger.debug(f"Using fallback models - models.js not found at {models_path}")
        return _FALLBACK_MODELS

    try:
        content = models_path.read_text()

        # Parse the JavaScript export statements
        models = {}

        # Look for DEFAULT_GEMINI_MODEL
        pro_pattern = (
            r"export\s+const\s+DEFAULT_GEMINI_MODEL\s*=\s*"
            r"['\"]([^'\"]+)['\"]"
        )
        pro_match = re.search(pro_pattern, content)
        if pro_match:
            models["pro"] = pro_match.group(1)

        # Look for DEFAULT_GEMINI_FLASH_MODEL
        flash_pattern = (
            r"export\s+const\s+DEFAULT_GEMINI_FLASH_MODEL\s*=\s*"
            r"['\"]([^'\"]+)['\"]"
        )
        flash_match = re.search(flash_pattern, content)
        if flash_match:
            models["flash"] = flash_match.group(1)

        # Use parsed values or fall back to defaults
        return {
            "pro": models.get("pro", _FALLBACK_MODELS["pro"]),
            "flash": models.get("flash", _FALLBACK_MODELS["flash"]),
        }

    except Exception as e:
        logger.debug(f"Error parsing models.js: {e}")
        return _FALLBACK_MODELS


def get_model_shortcuts() -> dict[str, str]:
    """Get model shortcuts, parsing from Gemini CLI on first call."""
    global _model_shortcuts_cache
    if _model_shortcuts_cache is None:
        _model_shortcuts_cache = _parse_gemini_models()
    return _model_shortcuts_cache


def __getattr__(name: str) -> Any:
    """Lazy loading for MODEL_SHORTCUTS."""
    if name == "MODEL_SHORTCUTS":
        return get_model_shortcuts()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def resolve_model_name(model: str | None) -> str | None:
    """Resolve model name from shortcuts or pass through.

    Args:
        model: Model name or shortcut ("pro", "flash")

    Returns:
        Resolved model name or None if no model specified
    """
    if model is None:
        return None

    # Check if it's a known shortcut
    shortcuts = get_model_shortcuts()
    if model.lower() in shortcuts:
        return shortcuts[model.lower()]

    # Otherwise pass through as-is
    return model
