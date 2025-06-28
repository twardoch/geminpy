# this_file: src/geminpy/__main__.py
"""Entry point for python -m geminpy."""

import sys

from geminpy.cli import main

if __name__ == "__main__":
    sys.exit(main())
