"""
Clear History API Endpoint.

This standalone Flask blueprint exposes an administrative endpoint to
reset the transaction history log to an empty state. The operation
will preserve the CSV file's schema/header while removing all recorded
entries.

Intended for restricted administrative use.
"""

from flask import Blueprint, jsonify
from storage import HISTORY_FILE, reset_history, read_history, ensure_history

# Blueprint registration for clear-history operations
clear_history_bp = Blueprint("clear_history", __name__)

@clear_history_bp.post("/api/clear-history")
def clear_history_endpoint():
    """
    Clear all transaction records while retaining the CSV file header.

    This operation:
        • Ensures the history file exists and contains the proper header.
        • Removes all transaction rows from the history file.
        • Returns the resulting (empty) history to the client.

    Returns:
        tuple: Flask JSON response and HTTP status code (200 on success)
            {
                "ok": True,
                "history": [...]  # List of remaining history rows (empty if cleared)
            }
    """
    # Ensure the history file exists with correct structure before clearing
    ensure_history(HISTORY_FILE)

    # Remove all entries but keep the header intact
    reset_history(HISTORY_FILE)

    # Retrieve the current (cleared) state of history for the response
    return jsonify({
        "ok": True,
        "history": read_history(HISTORY_FILE)
    }), 200
