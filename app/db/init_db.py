import os
import sys

from app.db.connection import setup_connection
from app.models.session import Session


def init_db():
    """Initialize the database by creating tables"""
    try:
        connection = setup_connection()

        # Create tables
        Session.createTable(ifNotExists=True)

        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = init_db()
    if not success:
        sys.exit(1)
