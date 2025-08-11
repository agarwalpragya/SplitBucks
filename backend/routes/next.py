from flask import Blueprint, request, jsonify
from storage import _ensure_defaults, compute_total_cost, select_payer, HISTORY_FILE, read_history

bp_next = Blueprint("next", __name__)

@bp_next.get("/api/next")
def api_next():
    prices_dec, balances_dec = _ensure_defaults()

    people = request.args.getlist("people") or list(prices_dec.keys())
    tie = (request.args.get("tie") or "least_recent").strip().lower()

    total_dec, included = compute_total_cost(prices_dec, people)
    if not included:
        return jsonify({"error": "No provided people match prices"}), 400

    payer = select_payer(
        balances_dec, included, tie_strategy=tie, history=read_history(HISTORY_FILE)
    )
    return jsonify({
        "payer": payer,
        "total_cost": float(total_dec),
        "included": included,
        "tie": tie
    })
