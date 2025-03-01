#!/usr/bin/env python
"""
Script to run database migrations on Railway.
This script is used as a pre-start command to ensure the database is properly set up.
"""

import os
import sys
import time

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from dotenv import load_dotenv

from app.db.database import create_db_and_tables
from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)

# Maximum number of retries for database connection
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds


def main():
    """Run database migrations on Railway."""
    # Load environment variables
    load_dotenv()

    logger.info("Running database migrations on Railway...")

    # Log environment variables for debugging (excluding sensitive ones)
    for key, value in os.environ.items():
        if not any(
            sensitive in key.lower()
            for sensitive in ["password", "secret", "key", "token"]
        ):
            logger.info("Environment variable: %s = %s", key, value)

    # Try to create database tables with retries
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(
                "Attempting to create database tables (attempt %s/%s)...",
                attempt + 1,
                MAX_RETRIES,
            )
            create_db_and_tables()
            logger.info("Database migrations completed successfully!")
            return
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(
                    "Database migration failed (attempt %s/%s): %s. Retrying in %s seconds...",
                    attempt + 1,
                    MAX_RETRIES,
                    str(e),
                    RETRY_DELAY,
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.exception(
                    "Database migration failed after %s attempts: %s",
                    MAX_RETRIES,
                    str(e),
                )
                sys.exit(1)


if __name__ == "__main__":
    main()
