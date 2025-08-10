from flask import Blueprint, jsonify
from storage.json_store import load_json
from storage.history_store import read_history
from services.ledger_service import normalize_prices, normalize_balances
from config import PRICES_FILE, BALANCES_FILE, HISTORY_FILE

state_bp = Blueprint("state", __name__, url_prefix="/api")

@state_bp.route("/state", methods=["GET"])
def get_state():
    prices = normalize_prices(load_json(PRICES_FILE, {}))
    balances = normalize_balances(load_json(BALANCES_FILE, {}))
    return jsonify({
        "prices": {k: float(v) for k, v in prices.items()},
        "balances": {k: float(v) for k, v in balances.items()},
        "history": read_history(HISTORY_FILE)
    })
