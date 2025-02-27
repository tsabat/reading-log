import os

from sqlobject import connectionForURI, sqlhub


def setup_connection():
    """
    Set up the database connection.
    By default, uses SQLite with a file in the current directory.
    """
    # Create a data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    os.makedirs(data_dir, exist_ok=True)

    # Create the database file path
    db_path = os.path.join(data_dir, "reading_tracker.db")

    # Get database URI from environment variable or use the constructed path
    db_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")

    print(f"Using database: {db_uri}")

    # Create connection
    connection = connectionForURI(db_uri)
    sqlhub.processConnection = connection

    return connection
