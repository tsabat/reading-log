import sys

from pathlib import Path

from app.db.connection import setup_connection
from app.logger import get_logger
from app.models.session import Session

logger = get_logger(__name__)


def init_db():
    """Initialize the database by creating tables"""
    try:
        _connection = setup_connection()

        # Create tables
        Session.createTable(ifNotExists=True)

        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error("Error initializing database: %s", e)
        logger.info("Current working directory: %s", Path.cwd())
        return False


if __name__ == "__main__":
    success = init_db()
    if not success:
        sys.exit(1)
