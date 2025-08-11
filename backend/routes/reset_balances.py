"""
Reset Balances API Endpoint.

This Flask blueprint provides an administrative operation to reset all account
balances to zero. The operation can optionally clear the transaction history
log file while preserving its CSV schema/header.

Intended for privileged/administrative use only.
"""

from flask import Blueprint, request, jsonify
from storage import (
    _ensure_defaults,
    BALANCES_FILE,
    save_json,           # Safe atomic write for JSON storage
    HISTORY_FILE,
    read_history,
    reset_history,
)

# Blueprint for balance reset operations
reset_balances_bp = Blueprint("reset_balances", __name__)

@reset_balances_bp.post("/api/reset-balances")
def reset_balances_endpoint():
    """
    Reset all user balances to zero, with optional transaction history clearing.

    Request Body (JSON):
        clear_history (bool, optional):
            If True, all transaction history entries will be deleted, leaving only
            the CSV header.

    Behavior:
        - Validates request payload.
        - Loads and ensures all system default data is present.
        - Sets all participant balances to 0.00.
        - Optionally clears historical transaction records.

    Returns:
        tuple: Flask JSON response and HTTP status code.
            200 on success:
                {
                    "ok": True,
                    "prices": { "<name>": <float>, ... },
                    "balances": { "<name>": 0.0, ... },
                    "history": [...]   # Cleared history if requested
                }
    """
    # Parse request JSON, defaulting to empty dict
    payload = request.get_json(silent=True) or {}
    clear_history_flag = bool(payload.get("clear_history"))

    # Load system defaults and ensure all known participants are initialized
    prices_dec, _ = _ensure_defaults()

    # Create zeroed balances for each known participant
    zeroed_balances = {name: 0.0 for name in prices_dec.keys()}

    # Save updated balances using safe atomic write
    save_json(BALANCES_FILE, zeroed_balances)

    # Purge transaction history if requested
    if clear_history_flag:
        reset_history(HISTORY_FILE)

    # Return updated state to client
    return jsonify({
        "ok": True,
        "prices": {name: float(value) for name, value in prices_dec.items()},
        "balances": zeroed_balances,
        "history": read_history(HISTORY_FILE),
    }), 200
