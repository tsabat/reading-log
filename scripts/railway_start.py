#!/usr/bin/env python
"""
Script to start the application on Railway.
This script properly handles the PORT environment variable.
"""

import os
import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import uvicorn

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Start the application on Railway."""
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8888))

    logger.info("Starting application on Railway with port %s", port)

    # Run the application
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)  # noqa: S104


if __name__ == "__main__":
    main()
