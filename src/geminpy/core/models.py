# this_file: src/geminpy/core/models.py
"""Model name mapping and utilities."""

import re
import subprocess
from pathlib import Path

from loguru import logger

# Fallback model names if we can't parse from Gemini CLI
_FALLBACK_MODELS = {
    "pro": "gemini-2.5-pro",
    "flash": "gemini-2.5-flash",
}


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
    models_path = npm_root / "@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/config/models.js"

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
        pro_match = re.search(r"export\s+const\s+DEFAULT_GEMINI_MODEL\s*=\s*['\"]([^'\"]+)['\"]", content)
        if pro_match:
            models["pro"] = pro_match.group(1)
            logger.debug(f"Parsed pro model: {models['pro']}")

        # Look for DEFAULT_GEMINI_FLASH_MODEL
        flash_match = re.search(r"export\s+const\s+DEFAULT_GEMINI_FLASH_MODEL\s*=\s*['\"]([^'\"]+)['\"]", content)
        if flash_match:
            models["flash"] = flash_match.group(1)
            logger.debug(f"Parsed flash model: {models['flash']}")

        # Use parsed values or fall back to defaults
        return {
            "pro": models.get("pro", _FALLBACK_MODELS["pro"]),
            "flash": models.get("flash", _FALLBACK_MODELS["flash"]),
        }

    except Exception as e:
        logger.debug(f"Error parsing models.js: {e}")
        return _FALLBACK_MODELS


# Initialize model shortcuts by parsing from Gemini CLI
MODEL_SHORTCUTS = _parse_gemini_models()


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
    if model.lower() in MODEL_SHORTCUTS:
        return MODEL_SHORTCUTS[model.lower()]

    # Otherwise pass through as-is
    return model
