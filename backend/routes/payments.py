"""
Payments API – Run Round Endpoint.

This blueprint handles execution of a "round" of payments, determining the payer
and updating balances accordingly via the ledger service.

Primary responsibilities:
    • Parse and validate incoming round execution requests.
    • Delegate round processing to the ledger service.
    • Return results in a consistent API schema for client consumption.

Restricted to authorized clients in production.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from schemas.run_round import RunRoundRequest
from services.ledger_service import run_round

# Blueprint registration for payment-related operations
payments_bp = Blueprint("payments", __name__, url_prefix="/api")

@payments_bp.route("/run", methods=["POST"])
def run_round_endpoint():
    """
    Execute a payment round.

    Request Body (JSON, validated via RunRoundRequest):
        people (list[str]): List of participant names to include in the round.
        tie (str, optional): Strategy to resolve ties when selecting a payer.
                             Supported values:
                                 • "least_recent" (default)
                                 • "random"

    Behavior:
        - Validates input against schema.
        - Calculates and records the round outcome via `ledger_service.run_round`.
        - Handles validation and business rule exceptions gracefully.

    Returns:
        tuple: Flask JSON response and HTTP status code.
            200 on success:
                {
                    "payer": "<name>",
                    "total_cost": <float>,
                    "balances": { "<name>": <float>, ... },
                    "history": [...],
                    "tie": "<strategy>"
                }
            400 on validation or business logic error:
                {
                    "error": "<description>"
                }
    """
    try:
        # Parse and validate request JSON against schema
        payload = RunRoundRequest.parse_obj(request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422

    try:
        # Execute business logic to determine payer and update ledger
        result = run_round(payload.people, payload.tie)
    except ValueError as e:
        # Business logic raised an error (e.g., invalid participants)
        return jsonify({"error": str(e)}), 400

    # Successful execution; return the result
    return jsonify(result), 200
