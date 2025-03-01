#!/usr/bin/env python
"""
Script to debug port forwarding issues.
This script starts a simple HTTP server on the specified port
to test if the port is accessible from outside the container.
"""

import http.server
import os
import socketserver
import sys

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from dotenv import load_dotenv

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Start a simple HTTP server to debug port forwarding."""
    # Load environment variables from .env file
    load_dotenv()

    # Get port from environment variable or use default
    port = int(os.getenv("API_PORT", "8888"))

    # Create a simple handler that returns a success message
    class DebugHandler(http.server.SimpleHTTPRequestHandler):
        # This method name must be do_GET as it's a standard method name in SimpleHTTPRequestHandler
        # We're overriding it, so we need to keep the same name
        def do_GET(self):  # noqa: N802
            """Handle GET requests with a simple success message."""
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body>")
            self.wfile.write(b"<h1>Port Forwarding Test Successful!</h1>")
            self.wfile.write(
                b"<p>If you can see this message, port forwarding is working correctly.</p>"
            )
            self.wfile.write(b"</body></html>")

    # Create the server - we intentionally bind to all interfaces for port forwarding testing
    with socketserver.TCPServer(("0.0.0.0", port), DebugHandler) as httpd:  # noqa: S104
        logger.info("Starting debug server on port %s...", port)
        logger.info(
            "Open http://localhost:%s in your browser to test port forwarding.", port
        )
        logger.info("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped.")


if __name__ == "__main__":
    main()
