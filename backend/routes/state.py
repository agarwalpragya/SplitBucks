from flask import Blueprint, jsonify
from storage import (
    _ensure_defaults,
    HISTORY_FILE,
    read_history,
)


bp_state = Blueprint("state", __name__)

@bp_state.get("/api/state")
def get_state():
    prices_dec, balances_dec = _ensure_defaults()
    return jsonify({
        "prices": {k: float(v) for k, v in prices_dec.items()},
        "balances": {k: float(v) for k, v in balances_dec.items()},
        "history": read_history(HISTORY_FILE),
    })
