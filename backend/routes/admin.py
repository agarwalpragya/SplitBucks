from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.set_price import SetPriceRequest
from schemas.remove_person import RemovePersonRequest

from storage.json_store import load_json, save_json_atomic
from storage.history_store import reset_history, read_history
from config import PRICES_FILE, BALANCES_FILE, HISTORY_FILE

admin_bp = Blueprint("admin", __name__, url_prefix="/api")

# --------------------
# Set Price
# --------------------
@admin_bp.route("/set-price", methods=["POST"])
def set_price():
    try:
        data = SetPriceRequest.parse_raw(request.data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})

    prices[data.name] = float(data.price)
    balances.setdefault(data.name, 0.0)

    save_json_atomic(PRICES_FILE, prices)
    save_json_atomic(BALANCES_FILE, balances)

    return jsonify({"ok": True, "prices": prices, "balances": balances}), 200


# --------------------
# Remove Person
# --------------------
@admin_bp.route("/remove-person", methods=["POST"])
def remove_person():
    try:
        data = RemovePersonRequest.parse_raw(request.data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})
    removed = False

    if data.name in prices:
        del prices[data.name]
        removed = True
    if data.name in balances:
        del balances[data.name]
        removed = True

    save_json_atomic(PRICES_FILE, prices)
    save_json_atomic(BALANCES_FILE, balances)

    return jsonify({"ok": removed, "prices": prices, "balances": balances}), 200


# --------------------
# Reset Balances
# --------------------
@admin_bp.route("/reset-balances", methods=["POST"])
def reset_balances():
    payload = request.get_json(silent=True) or {}
    clear_history = bool(payload.get("clear_history"))

    prices = load_json(PRICES_FILE, {})
    zeroed = {k: 0.0 for k in prices.keys()}
    save_json_atomic(BALANCES_FILE, zeroed)

    if clear_history:
        reset_history(HISTORY_FILE)

    return jsonify({
        "ok": True,
        "prices": prices,
        "balances": zeroed,
        "history": read_history(HISTORY_FILE),
    }), 200


# --------------------
# Clear History
# --------------------
@admin_bp.route("/clear-history", methods=["POST"])
def clear_history():
    reset_history(HISTORY_FILE)
    return jsonify({"ok": True, "history": read_history(HISTORY_FILE)}), 200
