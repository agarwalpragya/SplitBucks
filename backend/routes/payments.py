from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from schemas.run_round import RunRoundRequest
from services.ledger_service import run_round

payments_bp = Blueprint("payments", __name__, url_prefix="/api")

@payments_bp.route("/run", methods=["POST"])
def run():
    try:
        data = RunRoundRequest.parse_raw(request.data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        result = run_round(data.people, data.tie)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(result), 200
