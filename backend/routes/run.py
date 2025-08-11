"""
Run Round API Endpoint.

This Flask blueprint executes a "round" of payments:
    • Calculates the total cost for selected participants.
    • Determines who should pay next based on balances and tie-breaking rules.
    • Updates persisted account balances accordingly.
    • Appends the transaction to the historical record.

This endpoint modifies persistent JSON and CSV files in the storage layer and
should be protected for administrative or authorized use only.
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal
from storage import (
    _ensure_defaults,
    compute_total_cost,
    select_payer,
    HISTORY_FILE,
    read_history,
    BALANCES_FILE,
    save_json,
    money,
    now_iso,
    append_history_row,
)

# Blueprint for executing payment rounds
run_round_bp = Blueprint("run", __name__)

@run_round_bp.post("/api/run")
def run_round_endpoint():
    """
    Execute a payment round and update balances/history.

    Request Body (JSON):
        people (list[str], optional):
            Names of participants to include in this round.
            Defaults to all known participants if not provided.
        tie (str, optional):
            Tie-breaking strategy if multiple participants have the lowest balance.
            Supported values:
                • "least_recent" (default) - Select the person who paid least recently.
                • "random" - Select randomly among tied participants.

    Behavior:
        - Ensures default prices and balances are loaded from storage.
        - Determines total cost for the included participants.
        - Selects the payer using balances and payment history.
        - Subtracts each participant’s cost from their balance, credits the payer.
        - Saves updated balances to disk.
        - Records the transaction in the history file with a timestamp.

    Returns:
        tuple: Flask JSON response, 200 on success:
            {
                "timestamp": <ISO-8601 string>,
                "payer": <str>,
                "total_cost": <float>,
                "included": [<names>],
                "tie": <str>,
                "prices": {<name>: <float>, ...},
                "balances": {<name>: <float>, ...},
                "history": [...]
            }
        400 on validation error:
            {
                "error": "<description>"
            }
    """
    # Parse request payload
    payload = request.get_json(silent=True) or {}
    people = payload.get("people") or []
    tie_strategy = (payload.get("tie") or "least_recent").strip().lower()

    # Ensure price and balance data are initialized
    prices_dec, balances_dec = _ensure_defaults()

    # Default to including all known participants if none specified
    if not people:
        people = list(prices_dec.keys())

    # Compute total cost for included participants
    total_dec, included = compute_total_cost(prices_dec, people)
    if not included:
        return jsonify({"error": "No provided people match prices"}), 400

    # Determine who should pay next
    payer = select_payer(
        balances_dec,
        included,
        tie_strategy=tie_strategy,
        history=read_history(HISTORY_FILE),
    )

    # Adjust balances: subtract individual costs, add payer's total earnings
    for participant in included:
        balances_dec[participant] = money(
            balances_dec.get(participant, Decimal("0")) - prices_dec[participant]
        )
    balances_dec[payer] = money(balances_dec[payer] + total_dec)

    # Persist updated balances
    save_json(BALANCES_FILE, {k: float(v) for k, v in balances_dec.items()})

    # Append transaction to history log
    timestamp = now_iso()
    append_history_row(HISTORY_FILE, timestamp, payer, total_dec, included)

    # Return updated state
    return jsonify({
        "timestamp": timestamp,
        "payer": payer,
        "total_cost": float(total_dec),
        "included": included,
        "tie": tie_strategy,
        "prices": {name: float(price) for name, price in prices_dec.items()},
        "balances": {name: float(balance) for name, balance in balances_dec.items()},
        "history": read_history(HISTORY_FILE),
    }), 200
