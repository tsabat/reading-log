import os

from pathlib import Path

from sqlobject import connectionForURI, sqlhub  # type: ignore

from app.logger import get_logger

logger = get_logger(__name__)


def setup_connection():
    """
    Set up the database connection.
    By default, uses SQLite with a file in the current directory.
    """
    # Create a data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create the database file path
    db_path = data_dir / "reading_tracker.db"

    # Get database URI from environment variable or use the constructed path
    db_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")

    logger.info("Using database: %s", db_uri)

    # Create connection
    connection = connectionForURI(db_uri)
    sqlhub.processConnection = connection

    return connection
