#!/usr/bin/env python
"""
Script to initialize the database.
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
    """Initialize the database."""
    logger.info("Initializing database...")
    create_db_and_tables()
    logger.info("Database initialized successfully!")


if __name__ == "__main__":
    main()
