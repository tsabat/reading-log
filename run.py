#!/usr/bin/env python
"""
Entry point for the application.
This file is kept for backward compatibility.
"""

import sys

from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.joinpath("scripts").resolve()))

from run_app import main

if __name__ == "__main__":
    main()
