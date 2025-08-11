from flask import Blueprint, request, jsonify
from storage import _ensure_defaults, BALANCES_FILE, save_json, HISTORY_FILE, read_history, reset_history

bp_reset_balances = Blueprint("reset_balances", __name__)

@bp_reset_balances.post("/api/reset-balances")
def api_reset_balances():
    payload = request.get_json(silent=True) or {}
    clear_history = bool(payload.get("clear_history"))

    prices_dec, _ = _ensure_defaults()
    zeroed = {k: 0.0 for k in prices_dec.keys()}
    save_json(BALANCES_FILE, zeroed)

    if clear_history:
        reset_history(HISTORY_FILE)

    return jsonify({
        "ok": True,
        "prices": {k: float(v) for k, v in prices_dec.items()},
        "balances": zeroed,
        "history": read_history(HISTORY_FILE),
    })
