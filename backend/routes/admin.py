"""
Admin API endpoints for managing user price lists, account balances, and financial transaction history.

This Flask Blueprint exposes administrative operations for:
    • Creating or updating user-specific prices.
    • Removing user entries from the system.
    • Resetting account balances to zero.
    • Clearing recorded transaction history.

All modifications are persisted to JSON storage files, and historical financial
records are maintained in CSV format for audit purposes.

Intended for privileged/administrative use only.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

# Pydantic schemas for request validation
from schemas.set_price import SetPriceRequest
from schemas.remove_person import RemovePersonRequest

# Storage interface and persistent file constants
from storage import (
    load_json,
    save_json,            # Atomic write to JSON storage
    reset_history,
    read_history,
    PRICES_FILE,
    BALANCES_FILE,
    HISTORY_FILE,
)

# Blueprint registration: Admin API
admin_bp = Blueprint("admin", __name__, url_prefix="/api")


# ---------------------------------------------------------------------
# Endpoint: Set Price
# ---------------------------------------------------------------------
@admin_bp.route("/set-price", methods=["POST"])
def set_price():
    """
    Create or update the configured price for a given individual.

    Parameters (JSON body, validated via SetPriceRequest):
        name (str): The identifier for the individual.
        price (float): The new or updated price assigned to this individual.

    Returns:
        JSON response containing:
            ok (bool): True if operation succeeded.
            prices (dict): All current prices.
            balances (dict): All current balances.
    """
    try:
        payload = SetPriceRequest.parse_obj(request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"ok": False, "errors": e.errors()}), 400

    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})

    # Update the price and ensure corresponding balance exists
    prices[payload.name] = float(payload.price)
    balances.setdefault(payload.name, 0.0)

    # Commit changes atomically to storage
    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    return jsonify({"ok": True, "prices": prices, "balances": balances}), 200


# ---------------------------------------------------------------------
# Endpoint: Remove Person
# ---------------------------------------------------------------------
@admin_bp.route("/remove-person", methods=["POST"])
def remove_person():
    """
    Remove an individual's price and balance records from the system.

    Parameters (JSON body, validated via RemovePersonRequest):
        name (str): The identifier for the individual to remove.

    Returns:
        JSON response containing:
            ok (bool): True if the record existed and was removed.
            prices (dict): Updated price list.
            balances (dict): Updated balance list.
    """
    try:
        payload = RemovePersonRequest.parse_obj(request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"ok": False, "errors": e.errors()}), 400

    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})
    removed = False

    # Remove from both prices and balances if present
    if payload.name in prices:
        del prices[payload.name]
        removed = True
    if payload.name in balances:
        del balances[payload.name]
        removed = True

    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    return jsonify({"ok": removed, "prices": prices, "balances": balances}), 200


# ---------------------------------------------------------------------
# Endpoint: Reset Balances
# ---------------------------------------------------------------------
@admin_bp.route("/reset-balances", methods=["POST"])
def reset_balances():
    """
    Reset all user balances to zero, with optional history clearing.

    Parameters (Optional JSON body):
        clear_history (bool): If True, transaction history will be erased.

    Returns:
        JSON response containing:
            ok (bool): True if reset completed successfully.
            prices (dict): Current price list (unchanged).
            balances (dict): All balances reset to zero.
            history (list): Transaction history after reset (may be empty).
    """
    request_data = request.get_json(silent=True) or {}
    clear_history_flag = bool(request_data.get("clear_history"))

    prices = load_json(PRICES_FILE, {})
    zero_balances = {name: 0.0 for name in prices.keys()}
    save_json(BALANCES_FILE, zero_balances)

    if clear_history_flag:
        reset_history(HISTORY_FILE)

    return jsonify({
        "ok": True,
        "prices": prices,
        "balances": zero_balances,
        "history": read_history(HISTORY_FILE),
    }), 200


# ---------------------------------------------------------------------
# Endpoint: Clear History
# ---------------------------------------------------------------------
@admin_bp.route("/clear-history", methods=["POST"])
def clear_history_route():
    """
    Erase all transaction records while retaining the CSV file header.

    Useful for administrative resets while preserving schema structure.

    Returns:
        JSON response containing:
            ok (bool): Always True if operation executed.
            history (list): Cleared transaction history (header only).
    """
    reset_history(HISTORY_FILE)
    return jsonify({"ok": True, "history": read_history(HISTORY_FILE)}), 200
