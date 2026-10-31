#!/usr/bin/env python3
"""
==============================================================================
FILE: scripts/serve_southgate.py
==============================================================================

PURPOSE:
Lightweight static Hypertext Transfer Protocol (HTTP) server to serve the
reconstructed Southgate Surgery website mock-up remotely across the local
network and external interfaces on port 8085.

WHAT THIS FILE IS NOT FOR:
- Does not modify or write client website files.
- Does not require third-party dependencies outside the Python Standard Library.

INVARIANTS:
1. Binds to 0.0.0.0 on port 8085 to permit remote access across interfaces.
2. Serves static files rooted at clients/southgatesurgery.
==============================================================================
"""

import http.server
import os
from pathlib import Path
import socketserver
import sys

# Directory path of the surgery client mock-up.
REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT_DIR = REPO_ROOT / "clients" / "southgatesurgery"

# Listening port requested by operator.
PORT = 8085

# Bind address to allow remote network access.
HOST = "0.0.0.0"


class SurgeryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom request handler that serves files from the Southgate Surgery mock-up
    directory.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the handler with the client directory."""
        super().__init__(*args, directory=str(CLIENT_DIR), **kwargs)

    def log_message(self, format_str, *args):
        """Log incoming requests with timestamp to standard output."""
        sys.stdout.write(
            f"[{self.log_date_time_string()}] {self.address_string()} - "
            f"{format_str % args}\n"
        )
        sys.stdout.flush()


def main() -> None:
    """Initialise and run the HTTP server on port 8085."""
    # Step 1: Confirm the client mock-up directory exists before serving.
    if not CLIENT_DIR.is_dir():
        sys.stderr.write(
            f"Error: Directory not found: {CLIENT_DIR}\n"
        )
        sys.exit(1)

    # Step 2: Enable socket address reuse to prevent port binding conflicts.
    socketserver.TCPServer.allow_reuse_address = True

    # Step 3: Instantiate and start the TCP server.
    with socketserver.TCPServer((HOST, PORT), SurgeryHTTPRequestHandler) as srv:
        print(f"Southgate Surgery Mock-Up Server active.")
        print(f"Serving directory: {CLIENT_DIR}")
        print(f"Local URL:         http://localhost:{PORT}/")
        print(f"Network URL:       http://192.168.0.13:{PORT}/")
        print(f"Listening on:      {HOST}:{PORT}")
        sys.stdout.flush()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            srv.shutdown()


if __name__ == "__main__":
    main()
