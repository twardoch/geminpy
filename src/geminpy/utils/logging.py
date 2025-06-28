# this_file: src/geminpy/utils/logging.py
"""Centralized logging configuration using Loguru."""

import sys

from loguru import logger


def setup_logging(verbose: bool = False) -> None:
    """Configure loguru logging based on verbose flag."""
    logger.remove()  # Remove default handler

    # Always add a handler, but with different levels based on verbose flag
    level = "DEBUG" if verbose else "INFO"
    format_str = (
        "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        level=level,
        format=format_str,
        colorize=True,
    )
