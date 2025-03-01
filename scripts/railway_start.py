#!/usr/bin/env python
"""
Script to start the application on Railway.
This script properly handles the PORT environment variable.
"""

import os
import sys
import traceback

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

        # Check if DATABASE_URL is set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            sys.exit(1)

        # Log the database URL (masking password)
        if ":" in database_url and "@" in database_url:
            masked_url = (
                database_url.split("@")[0].split(":")[0]
                + ":***@"
                + database_url.split("@")[1]
            )
            logger.info("DATABASE_URL: %s", masked_url)

        # Check if we're using Railway's internal PostgreSQL
        if "railway.internal" in database_url:
            logger.info("Using Railway's internal PostgreSQL")

            # Try to resolve the hostname
            try:
                import socket

                hostname = database_url.split("@")[1].split("/")[0].split(":")[0]
                logger.info("Attempting to resolve hostname: %s", hostname)
                ip_address = socket.gethostbyname(hostname)
                logger.info("Hostname resolved to IP: %s", ip_address)
            except Exception as e:
                logger.warning("Failed to resolve hostname: %s", str(e))

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
        logger.exception(
            "Failed to start application: %s\n%s", str(e), traceback.format_exc()
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
