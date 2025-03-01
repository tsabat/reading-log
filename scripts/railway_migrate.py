#!/usr/bin/env python
"""
Script to run database migrations on Railway.
This script is used as a pre-start command to ensure the database is properly set up.
"""

import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.db.database import create_db_and_tables
from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Run database migrations on Railway."""
    logger.info("Running database migrations on Railway...")

    try:
        create_db_and_tables()
        logger.info("Database migrations completed successfully!")
    except Exception as e:
        logger.error("Database migration failed: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
