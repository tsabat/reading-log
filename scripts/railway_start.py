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

from dotenv import load_dotenv

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Start the application on Railway."""
    # Load environment variables
    load_dotenv()

    # Get port from environment variable or use default
    try:
        port = int(os.environ.get("PORT", 8888))
        logger.info("Starting application on Railway with port %s", port)

        # Log all environment variables for debugging (excluding sensitive ones)
        for key, value in os.environ.items():
            if not any(
                sensitive in key.lower()
                for sensitive in ["password", "secret", "key", "token"]
            ):
                logger.info("Environment variable: %s = %s", key, value)

        # Run the application with proper error handling
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",  # noqa: S104
            port=port,
            log_level="info",
            proxy_headers=True,  # Important for Railway's proxy setup
            forwarded_allow_ips="*",  # Allow forwarded IPs from Railway's proxy
        )
    except Exception as e:
        logger.exception("Failed to start application: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
