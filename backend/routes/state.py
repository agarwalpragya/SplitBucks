"""
State API Endpoint.

This Flask blueprint provides a read-only endpoint for retrieving the current
application state, including:
    • Configured participant prices.
    • Current account balances.
    • Full transaction history.

Intended for client consumption to synchronize with the current backend state.
"""

from flask import Blueprint, jsonify
from storage import (
    _ensure_defaults,   # Ensures default prices/balances/history files exist
    HISTORY_FILE,
    read_history,
)

# Blueprint registration for state-related operations
state_bp = Blueprint("state", __name__)

@state_bp.get("/api/state")
def get_state_endpoint():
    """
    Retrieve the current system state.

    Behavior:
        - Ensures default price and balance data are loaded.
        - Serializes Decimal values to floats for JSON output.
        - Includes full transaction history for client synchronization.

    Returns:
        tuple: Flask JSON response and HTTP status code (200 on success):
            {
                "prices": { "<name>": <float>, ... },
                "balances": { "<name>": <float>, ... },
                "history": [ ... ]   # List of transaction records from history.csv
            }
    """
    # Ensure initial data files exist, retrieve as Decimal values
    prices_dec, balances_dec = _ensure_defaults()

    # Return normalized floats for JSON compatibility
    return jsonify({
        "prices": {name: float(price) for name, price in prices_dec.items()},
        "balances": {name: float(balance) for name, balance in balances_dec.items()},
        "history": read_history(HISTORY_FILE),
    }), 200
