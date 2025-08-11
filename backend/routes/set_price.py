from flask import Blueprint, request, jsonify
from storage import (
    _ensure_defaults, PRICES_FILE, BALANCES_FILE, save_json,
    validate_person_name, parse_price_to_decimal
)

bp_set_price = Blueprint("set_price", __name__)

@bp_set_price.post("/api/set-price")
def api_set_price():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    price_raw = payload.get("price")

    if not validate_person_name(name):
        return jsonify({"error": "Invalid name. Use 1–40 letters, spaces, - or ' only."}), 400

    price_dec = parse_price_to_decimal(price_raw)
    if price_dec is None or price_dec <= 0:
        return jsonify({"error": "Invalid price. Must be a positive number."}), 400

    prices_dec, balances_dec = _ensure_defaults()
    prices = {k: float(v) for k, v in prices_dec.items()}
    balances = {k: float(v) for k, v in balances_dec.items()}

    prices[name] = float(price_dec)
    balances.setdefault(name, 0.0)
    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    return jsonify({"ok": True, "prices": prices, "balances": balances})
