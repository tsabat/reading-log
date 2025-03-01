#!/usr/bin/env python
"""
Script to check if the database is accessible.
This script can be used to diagnose database connection issues.
"""

import os
import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from dotenv import load_dotenv
from sqlmodel import Session, select

from app.db.database import engine
from app.models import ReadingLog
from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def check_database_connection():
    """Check if the database is accessible."""
    # Load environment variables
    load_dotenv()

    logger.info("Checking database connection...")

    # Log database URL (masking password)
    database_url = os.getenv("DATABASE_URL", "Not set")
    if database_url != "Not set" and ":" in database_url and "@" in database_url:
        parts = database_url.split("@")
        credentials = parts[0].split(":")
        if len(credentials) > 2:
            masked_url = f"{credentials[0]}:***@{parts[1]}"
            logger.info("Database URL: %s", masked_url)
        else:
            logger.info("Database URL format not recognized")
    else:
        logger.info("Database URL: %s", database_url)

    # Try to connect to the database
    try:
        with Session(engine) as session:
            # Try to execute a simple query
            result = session.exec(select(ReadingLog).limit(1)).all()
            logger.info("Database connection successful!")
            logger.info("Found %s reading logs", len(result))
            return True
    except Exception as e:
        logger.exception("Database connection failed: %s", str(e))
        return False


def main():
    """Run the database check."""
    success = check_database_connection()
    if success:
        logger.info("Database check completed successfully!")
        sys.exit(0)
    else:
        logger.error("Database check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
