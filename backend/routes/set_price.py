"""
Set Price API Endpoint.

This Flask blueprint provides an administrative endpoint to create or update
the configured price for a specified individual. The operation includes
server-side validation of both the participant name and the price value.

Intended for administrative use only.
"""

from flask import Blueprint, request, jsonify
from storage import (
    _ensure_defaults,
    PRICES_FILE,
    BALANCES_FILE,
    save_json,               # Atomic JSON writer
    validate_person_name,    # Business rule: allowed name format
    parse_price_to_decimal,  # Safe parsing to Decimal with validation
)

# Blueprint for set-price operations
set_price_bp = Blueprint("set_price", __name__)

@set_price_bp.post("/api/set-price")
def set_price_endpoint():
    """
    Create or update the configured price for a specified participant.

    Request Body (JSON):
        name (str):
            Participant name. Must be 1–40 characters: letters, spaces,
            apostrophes, or hyphens only.
        price (str|float|int):
            New price to assign to this participant. Must be a positive number.

    Behavior:
        - Validates participant name against business rules.
        - Parses and validates price into a Decimal.
        - Loads current prices and balances from storage.
        - Updates the participant's price, adding balance entry if missing.
        - Persists updated data atomically.

    Returns:
        tuple: Flask JSON response and HTTP status code.
            200 on success:
                {
                    "ok": True,
                    "prices": { "<name>": <float>, ... },
                    "balances": { "<name>": <float>, ... }
                }
            400 on validation error:
                {
                    "error": "<description>"
                }
    """
    # Parse and sanitize request payload
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    price_raw = payload.get("price")

    # Validate business rules for participant name
    if not validate_person_name(name):
        return jsonify({
            "error": "Invalid name. Use 1–40 letters, spaces, hyphen (-), or apostrophe (') only."
        }), 400

    # Parse and validate price value
    price_dec = parse_price_to_decimal(price_raw)
    if price_dec is None or price_dec <= 0:
        return jsonify({
            "error": "Invalid price. Must be a positive number."
        }), 400

    # Ensure necessary data structures are loaded from storage
    prices_dec, balances_dec = _ensure_defaults()

    # Convert Decimals to floats for JSON serialization
    prices = {k: float(v) for k, v in prices_dec.items()}
    balances = {k: float(v) for k, v in balances_dec.items()}

    # Apply update: set price and ensure balance entry exists
    prices[name] = float(price_dec)
    balances.setdefault(name, 0.0)

    # Persist changes atomically
    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    return jsonify({
        "ok": True,
        "prices": prices,
        "balances": balances
    }), 200
