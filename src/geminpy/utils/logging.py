# this_file: src/geminpy/utils/logging.py
"""Centralized logging configuration using Loguru."""

import sys

from loguru import logger


def setup_logging(verbose: bool = False) -> None:
    """Configure loguru logging based on verbose flag."""
    logger.remove()  # Remove default handler
    if verbose:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<level>{message}</level>",
            colorize=True,
        )
