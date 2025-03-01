#!/usr/bin/env python
"""
Diagnostic script for PostgreSQL connection issues on Railway.
This script performs detailed checks on the PostgreSQL connection and schema.
"""

import os
import socket
import sys
import traceback

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import psycopg2

from dotenv import load_dotenv

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Run detailed PostgreSQL diagnostics."""
    # Load environment variables
    load_dotenv()

    # Log all environment variables for debugging (excluding sensitive ones)
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if not any(
            sensitive in key.lower()
            for sensitive in ["password", "secret", "key", "token"]
        ):
            logger.info("  %s = %s", key, value)

    # Check for PostgreSQL-specific environment variables
    pg_vars = {
        "PGHOST": os.getenv("PGHOST"),
        "PGUSER": os.getenv("PGUSER"),
        "PGPASSWORD": "***" if os.getenv("PGPASSWORD") else None,
        "PGDATABASE": os.getenv("PGDATABASE"),
        "PGPORT": os.getenv("PGPORT"),
    }
    logger.info("PostgreSQL environment variables: %s", pg_vars)

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
            "Parsed connection details: host=%s, port=%s, user=%s, database=%s",
            hostname,
            port,
            username,
            database,
        )

        # Try to resolve the hostname
        try:
            logger.info("Attempting to resolve hostname: %s", hostname)
            ip_address = socket.gethostbyname(hostname)
            logger.info("Hostname resolved to IP: %s", ip_address)
        except Exception as e:
            logger.warning("Failed to resolve hostname: %s", str(e))

            # If hostname is postgres.railway.internal, try to use the PGHOST environment variable
            if hostname == "postgres.railway.internal":
                pghost = os.getenv("PGHOST")
                if pghost:
                    logger.info("Using PGHOST environment variable: %s", pghost)
                    hostname = pghost

                    # Try to resolve the new hostname
                    try:
                        logger.info("Attempting to resolve PGHOST: %s", hostname)
                        ip_address = socket.gethostbyname(hostname)
                        logger.info("PGHOST resolved to IP: %s", ip_address)
                    except Exception as e2:
                        logger.warning("Failed to resolve PGHOST: %s", str(e2))

        # Try connection with parsed details
        logger.info("Attempting to connect to PostgreSQL with parsed details...")
        try:
            conn = psycopg2.connect(
                host=hostname,
                port=port,
                user=username,
                password=password,
                dbname=database,
                connect_timeout=10,
            )
            logger.info("Connected to PostgreSQL successfully with parsed details!")
        except Exception as e:
            logger.warning(
                "Failed to connect with parsed details: %s\n%s",
                str(e),
                traceback.format_exc(),
            )

            # Try connection with environment variables if available
            if all(
                [
                    os.getenv("PGHOST"),
                    os.getenv("PGUSER"),
                    os.getenv("PGPASSWORD"),
                    os.getenv("PGDATABASE"),
                ]
            ):
                logger.info(
                    "Attempting to connect to PostgreSQL with environment variables..."
                )
                try:
                    conn = psycopg2.connect(
                        host=os.getenv("PGHOST"),
                        port=int(os.getenv("PGPORT", "5432")),
                        user=os.getenv("PGUSER"),
                        password=os.getenv("PGPASSWORD"),
                        dbname=os.getenv("PGDATABASE"),
                        connect_timeout=10,
                    )
                    logger.info(
                        "Connected to PostgreSQL successfully with environment variables!"
                    )
                except Exception as e2:
                    logger.error(
                        "Failed to connect with environment variables: %s\n%s",
                        str(e2),
                        traceback.format_exc(),
                    )
                    raise e  # Re-raise the original exception
            else:
                raise

        # Create a cursor
        cur = conn.cursor()

        # Get PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        logger.info("PostgreSQL version: %s", version)

        # Get current database
        cur.execute("SELECT current_database();")
        current_db = cur.fetchone()[0]
        logger.info("Current database: %s", current_db)

        # Get current schema
        cur.execute("SELECT current_schema();")
        current_schema = cur.fetchone()[0]
        logger.info("Current schema: %s", current_schema)

        # Get search path
        cur.execute("SHOW search_path;")
        search_path = cur.fetchone()[0]
        logger.info("Search path: %s", search_path)

        # List all schemas
        cur.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = [schema[0] for schema in cur.fetchall()]
        logger.info("Available schemas: %s", schemas)

        # List all tables in the current schema
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema();"
        )
        tables_in_current_schema = [table[0] for table in cur.fetchall()]
        logger.info("Tables in current schema: %s", tables_in_current_schema)

        # List all tables in the public schema
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables_in_public = [table[0] for table in cur.fetchall()]
        logger.info("Tables in public schema: %s", tables_in_public)

        # Try to create a test table in the current schema
        try:
            logger.info("Attempting to create a test table in the current schema...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS diagnostic_test (
                    id SERIAL PRIMARY KEY,
                    test_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Test table created successfully in the current schema!")

            # Verify the test table was created
            cur.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'diagnostic_test');"
            )
            test_table_exists = cur.fetchone()[0]
            logger.info("Test table exists: %s", test_table_exists)

            # Insert a test row
            cur.execute(
                "INSERT INTO diagnostic_test (test_value) VALUES (%s) RETURNING id;",
                ("Test value from diagnostic script",),
            )
            test_id = cur.fetchone()[0]
            conn.commit()
            logger.info("Inserted test row with ID: %s", test_id)

            # Retrieve the test row
            cur.execute("SELECT * FROM diagnostic_test WHERE id = %s;", (test_id,))
            test_row = cur.fetchone()
            logger.info("Retrieved test row: %s", test_row)

        except Exception as e:
            logger.exception(
                "Failed to create or use test table: %s\n%s",
                str(e),
                traceback.format_exc(),
            )
            conn.rollback()

        # Check user permissions
        logger.info("Checking user permissions...")
        cur.execute("""
            SELECT
                r.rolname,
                r.rolsuper,
                r.rolinherit,
                r.rolcreaterole,
                r.rolcreatedb,
                r.rolcanlogin
            FROM
                pg_roles r
            WHERE
                r.rolname = current_user;
        """)
        user_info = cur.fetchone()
        if user_info:
            logger.info(
                "Current user: %s, is_superuser: %s, can_inherit: %s, can_create_role: %s, can_create_db: %s, can_login: %s",
                user_info[0],
                user_info[1],
                user_info[2],
                user_info[3],
                user_info[4],
                user_info[5],
            )

        # Check table privileges
        logger.info("Checking table privileges...")
        cur.execute("""
            SELECT
                table_name,
                privilege_type
            FROM
                information_schema.table_privileges
            WHERE
                grantee = current_user
                AND table_schema = 'public'
            ORDER BY
                table_name,
                privilege_type;
        """)
        privileges = cur.fetchall()
        for privilege in privileges:
            logger.info("Table: %s, Privilege: %s", privilege[0], privilege[1])

        # Close cursor and connection
        cur.close()
        conn.close()
        logger.info("PostgreSQL connection closed")

        return True
    except Exception as e:
        logger.exception(
            "Error during PostgreSQL diagnostics: %s\n%s",
            str(e),
            traceback.format_exc(),
        )
        return False


if __name__ == "__main__":
    success = main()
    if success:
        logger.info("PostgreSQL diagnostics completed successfully!")
        sys.exit(0)
    else:
        logger.error("PostgreSQL diagnostics failed!")
        sys.exit(1)
