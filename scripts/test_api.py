#!/usr/bin/env python
"""
Script to test the API endpoints.
This script can be used to verify that the API is working correctly.
"""

import argparse
import sys

from pathlib import Path

import requests

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def test_health(base_url):
    """Test the health endpoint."""
    url = f"{base_url}/health"
    logger.info("Testing health endpoint: %s", url)

    try:
        response = requests.get(url, timeout=10)
        logger.info("Health endpoint response: %s", response.status_code)
        logger.info("Response body: %s", response.text)
        return response.status_code == 200
    except Exception as e:
        logger.exception("Error testing health endpoint: %s", str(e))
        return False


def test_root(base_url):
    """Test the root endpoint."""
    url = f"{base_url}/"
    logger.info("Testing root endpoint: %s", url)

    try:
        response = requests.get(url, timeout=10)
        logger.info("Root endpoint response: %s", response.status_code)
        logger.info("Response body: %s", response.text)
        return response.status_code == 200
    except Exception as e:
        logger.exception("Error testing root endpoint: %s", str(e))
        return False


def test_reading_logs(base_url):
    """Test the reading logs endpoints."""
    url = f"{base_url}/reading-logs"
    logger.info("Testing reading logs endpoint: %s", url)

    try:
        # Test GET /reading-logs
        response = requests.get(url, timeout=10)
        logger.info("GET reading logs response: %s", response.status_code)
        logger.info("Response body: %s", response.text)

        # Test POST /reading-logs
        test_data = {"duration": 30, "description": "Test reading log"}
        response = requests.post(url, json=test_data, timeout=10)
        logger.info("POST reading log response: %s", response.status_code)
        logger.info("Response body: %s", response.text)

        if response.status_code == 200:
            # Get the created reading log ID
            reading_log = response.json()
            reading_log_id = reading_log["id"]

            # Test GET /reading-logs/{reading_log_id}
            detail_url = f"{url}/{reading_log_id}"
            response = requests.get(detail_url, timeout=10)
            logger.info("GET reading log detail response: %s", response.status_code)
            logger.info("Response body: %s", response.text)

            # Test PATCH /reading-logs/{reading_log_id}
            update_data = {"duration": 45, "description": "Updated test reading log"}
            response = requests.patch(detail_url, json=update_data, timeout=10)
            logger.info("PATCH reading log response: %s", response.status_code)
            logger.info("Response body: %s", response.text)

            # Test DELETE /reading-logs/{reading_log_id}
            response = requests.delete(detail_url, timeout=10)
            logger.info("DELETE reading log response: %s", response.status_code)
            logger.info("Response body: %s", response.text)

        return True
    except Exception as e:
        logger.exception("Error testing reading logs endpoints: %s", str(e))
        return False


def main():
    """Run the API tests."""
    parser = argparse.ArgumentParser(description="Test the API endpoints")
    parser.add_argument(
        "--url",
        default="http://localhost:8888",
        help="Base URL of the API (default: http://localhost:8888)",
    )
    args = parser.parse_args()

    base_url = args.url
    logger.info("Testing API at %s", base_url)

    # Run the tests
    health_ok = test_health(base_url)
    root_ok = test_root(base_url)
    logs_ok = test_reading_logs(base_url)

    # Print summary
    logger.info("Test results:")
    logger.info("Health endpoint: %s", "OK" if health_ok else "FAILED")
    logger.info("Root endpoint: %s", "OK" if root_ok else "FAILED")
    logger.info("Reading logs endpoints: %s", "OK" if logs_ok else "FAILED")

    # Exit with appropriate status code
    if health_ok and root_ok and logs_ok:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.exception("Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
