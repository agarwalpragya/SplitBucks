"""
Next Payer API Endpoint.

This blueprint exposes a read-only endpoint that determines:
    • Which participant should pay next.
    • The total cost of the selected participants' items.
    • The tie-break strategy applied.

The decision is based on:
    • Configured individual prices.
    • Current account balances.
    • Historical payment records (for tie-breaking).
"""

from flask import Blueprint, request, jsonify
from storage import (
    _ensure_defaults,
    compute_total_cost,
    select_payer,
    HISTORY_FILE,
    read_history,
)

# Blueprint for next-payer calculations
next_bp = Blueprint("next", __name__)

@next_bp.get("/api/next")
def next_payer_endpoint():
    """
    Determine the next payer based on balances, prices, and historical data.

    Query Parameters:
        people (list[str], optional):
            A list of participant names to consider. Defaults to all known participants
            if not provided.
        tie (str, optional):
            Tie-breaking strategy when multiple participants have the same lowest balance.
            Supported values:
                • "least_recent" (default): Pick the one who paid least recently.
                • "random": Pick randomly from tied participants.

    Returns:
        tuple: Flask JSON response and HTTP status code
            On success (200):
                {
                    "payer": "<name>",          # The selected next payer
                    "total_cost": <float>,      # Sum of prices for included participants
                    "included": [<names>],      # List of valid participants considered
                    "tie": "<strategy>"         # Tie-breaking strategy used
                }
            On error (400):
                {
                    "error": "No provided people match prices"
                }
    """
    # Ensure that prices, balances, and history files exist and are initialized
    prices_dec, balances_dec = _ensure_defaults()

    # Use query parameters to determine which participants to include
    people = request.args.getlist("people") or list(prices_dec.keys())
    tie_strategy = (request.args.get("tie") or "least_recent").strip().lower()

    # Compute total cost and filter participants to only those with a configured price
    total_dec, included = compute_total_cost(prices_dec, people)
    if not included:
        return jsonify({"error": "No provided people match prices"}), 400

    # Select the participant who should pay next using balances and history
    payer = select_payer(
        balances_dec,
        included,
        tie_strategy=tie_strategy,
        history=read_history(HISTORY_FILE),
    )

    # Return decision and relevant calculation details
    return jsonify({
        "payer": payer,
        "total_cost": float(total_dec),
        "included": included,
        "tie": tie_strategy,
    }), 200
