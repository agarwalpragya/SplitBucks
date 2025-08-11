"""
Remove Person API Endpoint.

This Flask blueprint exposes an administrative endpoint to remove an individual
from both the prices and balances data stores. This operation ensures that
subsequent calculations and histories no longer reference the removed individual.

Intended for administrative use only.
"""

from flask import Blueprint, request, jsonify
from storage import _ensure_defaults, PRICES_FILE, BALANCES_FILE, save_json

# Blueprint for person removal operations
remove_person_bp = Blueprint("remove_person", __name__)

@remove_person_bp.post("/api/remove-person")
def remove_person_endpoint():
    """
    Remove an individual's entries from prices and balances.

    Request Body (JSON):
        name (str): The exact name of the individual to remove.
                    Name comparisons are case-sensitive.

    Behavior:
        - Ensures current prices and balances are initialized.
        - Removes the requested individual from both stores if present.
        - Saves updated stores to disk using atomic writes.

    Returns:
        tuple: Flask JSON response and HTTP status code.
            200 on success (operation attempted):
                {
                    "ok": <bool>,               # True if individual existed and was removed
                    "prices": { ... },          # Updated price mappings
                    "balances": { ... }         # Updated balance mappings
                }
            400 if request is invalid:
                {
                    "error": "name required"
                }
    """
    # Safely parse request payload
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return jsonify({"error": "name required"}), 400

    # Ensure default data is loaded and converted to float for serialization
    prices_dec, balances_dec = _ensure_defaults()
    prices = {k: float(v) for k, v in prices_dec.items()}
    balances = {k: float(v) for k, v in balances_dec.items()}

    # Attempt removal from both stores
    removed = False
    if name in prices:
        del prices[name]
        removed = True
    if name in balances:
        del balances[name]
        removed = True

    # Commit updated data to persistent storage
    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    # Return operation result
    return jsonify({"ok": removed, "prices": prices, "balances": balances}), 200
