"""
State API Endpoint.

This Flask blueprint provides a read-only endpoint for retrieving the current
application state, including:
    • Configured participant prices.
    • Current account balances.
    • Full transaction history.

Note:
    This endpoint is PURE READ-ONLY. It does not seed or mutate any files.
    If prices/balances are empty (e.g., after deleting all users), it returns {}.
"""

from flask import Blueprint, jsonify
from storage import (
    load_json,          # pure read; returns default {} if file missing
    ensure_history,     # make sure history file + header exist (non-destructive)
    read_history,
    PRICES_FILE,
    BALANCES_FILE,
    HISTORY_FILE,
)

# Blueprint registration for state-related operations
state_bp = Blueprint("state", __name__)

@state_bp.get("/api/state")
def get_state_endpoint():
    """
    Retrieve the current system state without seeding defaults.

    Returns:
        200 JSON:
            {
                "prices": { "<name>": <float>, ... },
                "balances": { "<name>": <float>, ... },
                "history": [ ... ]
            }
    """
    # Pure reads; do NOT call _ensure_defaults() here
    prices = load_json(PRICES_FILE, {})        # may be {}
    balances = load_json(BALANCES_FILE, {})    # may be {}

    # Ensure history file exists (non-destructive), then read it
    ensure_history(HISTORY_FILE)
    history = read_history(HISTORY_FILE)

    # Normalize values to floats for JSON compatibility (safe even if already floats)
    prices_out = {k: float(v) for k, v in prices.items()}
    balances_out = {k: float(v) for k, v in balances.items()}

    return jsonify({
        "prices": prices_out,
        "balances": balances_out,
        "history": history,
    }), 200
