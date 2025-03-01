#!/usr/bin/env python
"""
Script to directly check the PostgreSQL connection and create tables.
This script bypasses SQLModel and uses psycopg2 directly.
"""

import os
import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import psycopg2

from dotenv import load_dotenv

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Check PostgreSQL connection and create tables directly."""
    # Load environment variables
    load_dotenv()

    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql"):
        logger.error("DATABASE_URL environment variable not set or not PostgreSQL")
        sys.exit(1)

    # Log database URL (masking password)
    masked_url = (
        database_url.split("@")[0].split(":")[0] + ":***@" + database_url.split("@")[1]
    )
    logger.info("Database URL: %s", masked_url)

    try:
        # Parse the database URL
        # Format: postgresql://username:password@hostname:port/database
        url_parts = database_url.replace("postgresql://", "").split("@")
        credentials = url_parts[0].split(":")
        username = credentials[0]
        password = credentials[1]

        host_parts = url_parts[1].split("/")
        host_port = host_parts[0].split(":")
        hostname = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        database = host_parts[1]

        logger.info(
            "Connecting to PostgreSQL: host=%s, port=%s, user=%s, database=%s",
            hostname,
            port,
            username,
            database,
        )

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            dbname=database,
            connect_timeout=10,
        )
        logger.info("Connected to PostgreSQL successfully!")

        # Create a cursor
        cur = conn.cursor()

        # Check if the readinglog table exists
        cur.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'readinglog')"
        )
        table_exists = cur.fetchone()[0]

        if table_exists:
            logger.info("Table 'readinglog' already exists")
        else:
            logger.info("Table 'readinglog' does not exist, creating it...")

            # Create the readinglog table
            cur.execute("""
                CREATE TABLE readinglog (
                    id SERIAL PRIMARY KEY,
                    duration INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Table 'readinglog' created successfully!")

        # List all tables in the database
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = [table[0] for table in cur.fetchall()]
        logger.info("Tables in database: %s", tables)

        # Close cursor and connection
        cur.close()
        conn.close()
        logger.info("PostgreSQL connection closed")

        return True
    except Exception as e:
        logger.exception("Error connecting to PostgreSQL: %s", str(e))
        return False


if __name__ == "__main__":
    success = main()
    if success:
        logger.info("PostgreSQL check completed successfully!")
        sys.exit(0)
    else:
        logger.error("PostgreSQL check failed!")
        sys.exit(1)
