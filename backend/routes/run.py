from flask import Blueprint, request, jsonify
from decimal import Decimal
from storage import (
    _ensure_defaults, compute_total_cost, select_payer, HISTORY_FILE, read_history,
    BALANCES_FILE, save_json, money, now_iso, append_history_row
)

bp_run = Blueprint("run", __name__)

@bp_run.post("/api/run")
def api_run():
    payload = request.get_json(silent=True) or {}
    people = payload.get("people") or []
    tie = (payload.get("tie") or "least_recent").strip().lower()

    prices_dec, balances_dec = _ensure_defaults()

    if not people:
        people = list(prices_dec.keys())

    total_dec, included = compute_total_cost(prices_dec, people)
    if not included:
        return jsonify({"error": "No provided people match prices"}), 400

    payer = select_payer(
        balances_dec, included, tie_strategy=tie, history=read_history(HISTORY_FILE)
    )

    for p in included:
        balances_dec[p] = money(balances_dec.get(p, Decimal("0")) - prices_dec[p])
    balances_dec[payer] = money(balances_dec[payer] + total_dec)

    save_json(BALANCES_FILE, {k: float(v) for k, v in balances_dec.items()})
    ts = now_iso()
    append_history_row(HISTORY_FILE, ts, payer, total_dec, included)

    return jsonify({
        "timestamp": ts,
        "payer": payer,
        "total_cost": float(total_dec),
        "included": included,
        "tie": tie,
        "prices": {k: float(v) for k, v in prices_dec.items()},
        "balances": {k: float(v) for k, v in balances_dec.items()},
        "history": read_history(HISTORY_FILE),
    })
