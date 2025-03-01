#!/usr/bin/env python
"""
Script to run the application.
"""

import os
import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import uvicorn

from dotenv import load_dotenv

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Run the application."""
    # Load environment variables from .env file
    load_dotenv()

    # Get host and port from environment variables or use defaults
    # Always use 0.0.0.0 to bind to all interfaces, making it accessible from outside the container
    host = "0.0.0.0"  # noqa: S104
    port = int(os.getenv("API_PORT", "8888"))

    logger.info("Starting application on %s:%s", host, port)
    logger.info("API documentation available at:")
    logger.info("  - Swagger UI: http://localhost:%s/docs", port)
    logger.info("  - ReDoc: http://localhost:%s/redoc", port)

    # Run the application
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
