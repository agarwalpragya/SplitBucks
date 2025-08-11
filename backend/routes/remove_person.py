from flask import Blueprint, request, jsonify
from storage import _ensure_defaults, PRICES_FILE, BALANCES_FILE, save_json

bp_remove_person = Blueprint("remove_person", __name__)

@bp_remove_person.post("/api/remove-person")
def api_remove_person():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400

    prices_dec, balances_dec = _ensure_defaults()
    prices = {k: float(v) for k, v in prices_dec.items()}
    balances = {k: float(v) for k, v in balances_dec.items()}

    removed = False
    if name in prices:
        del prices[name]
        removed = True
    if name in balances:
        del balances[name]
        removed = True

    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)
    return jsonify({"ok": removed, "prices": prices, "balances": balances})
