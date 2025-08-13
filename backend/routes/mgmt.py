"""
Management Routes (no admin separation)

Purpose:
    Expose simple, RESTful endpoints under /api for managing:
        • Users' prices
        • Users (create via set price, remove)
        • Account balances reset
        • History clearing

Design goals:
    - Keep controllers thin (validation + delegation to storage/utilities)
    - Use REST verbs and idempotent semantics where appropriate
    - Return stable, predictable response shapes
    - Keep money logic in services/storage; transport concerns here

Quick routing table:
    PUT    /api/users/<name>/price     → set_price()         (idempotent upsert; returns 200 + state)
    DELETE /api/users/<name>           → remove_user()       (idempotent; 204 No Content)
    PUT    /api/balances               → reset_balances()    (optional clear_history; returns 200 + state)
    DELETE /api/history                → clear_history()     (idempotent; 204 No Content)
"""

# ------------------------------- Imports --------------------------------
from decimal import Decimal
from typing import Optional

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, condecimal

from storage import (
    load_json,
    save_json,            # Atomic write to JSON storage (temp file → rename)
    reset_history,
    read_history,
    ensure_history,
    PRICES_FILE,
    BALANCES_FILE,
    HISTORY_FILE,
)

# ----------------------------- Blueprint --------------------------------
# Single blueprint under /api for all management operations.
mgmt_bp = Blueprint("mgmt", __name__, url_prefix="/api")

# ------------------------------- Schemas --------------------------------
# Minimal Pydantic request models to validate and coerce inputs at the edge.

PriceType = condecimal(gt=0, max_digits=12, decimal_places=2)

class PriceOnly(BaseModel):
    # Positive currency amount with two decimal places
    price: Decimal

    # Pydantic validator to enforce constraints
    @classmethod
    def __get_validators__(cls):
        yield from Decimal.__get_validators__()
        yield condecimal(gt=0, max_digits=12, decimal_places=2)

class ResetBalancesBody(BaseModel):
    # Optional flag to also clear history when resetting balances
    clear_history: Optional[bool] = False

# ------------------------------- Helpers --------------------------------
def _canon_key(name: str, *, prices: dict, balances: dict) -> Optional[str]:
    """
    Resolve a display name to the canonical stored key (case-insensitive).

    Returns:
        - Stored key with original casing if found, else None.
    """
    lookup = (name or "").strip().lower()
    key_map = {k.lower(): k for k in set(prices.keys()) | set(balances.keys())}
    return key_map.get(lookup)

def _ensure_user_entry(name: str, *, prices: dict, balances: dict) -> str:
    """
    Ensure a user exists across both maps, creating on first set-price.
    Returns canonical name to persist.
    """
    found = _canon_key(name, prices=prices, balances=balances)
    return found or name.strip()

# -------------------------------- Routes --------------------------------
@mgmt_bp.put("/users/<string:name>/price")
def set_price(name: str):
    """
    Idempotently create/update the configured price for a user.

    Path:
        <name> (str) – user's display name (case-insensitive match)

    Body (JSON):
        { "price": <decimal> } – required, > 0, two decimals

    Returns:
        200 JSON on success:
            {
              "ok": true,
              "name": "<canonical>",
              "price": <float>,
              "prices": { ... },
              "balances": { ... }
            }
        422 JSON on validation error.
    """
    # Validate request body
    try:
        body = PriceOnly.parse_obj(request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"ok": False, "errors": e.errors()}), 422

    # Load current state
    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})

    # Compute canonical storage key: reuse existing casing or create new
    canon = _ensure_user_entry(name, prices=prices, balances=balances)

    # Update price and guarantee a balance entry exists
    prices[canon] = float(Decimal(str(body.price)))
    balances.setdefault(canon, 0.0)

    # Persist (each save is atomic)
    save_json(PRICES_FILE, prices)
    save_json(BALANCES_FILE, balances)

    # Return updated state so the client can rehydrate
    return jsonify({"ok": True, "name": canon, "price": prices[canon],
                    "prices": prices, "balances": balances}), 200


@mgmt_bp.delete("/users/<string:name>")
def remove_user(name: str):
    """
    Idempotently remove a user from prices and balances.

    Behavior:
        - Case-insensitive match against stored keys
        - If user exists, delete from both maps and persist
        - Always returns 204 No Content (idempotent)

    Returns:
        204 No Content
    """
    prices = load_json(PRICES_FILE, {})
    balances = load_json(BALANCES_FILE, {})

    canon = _canon_key(name, prices=prices, balances=balances)
    if canon is not None:
        if canon in prices:
            del prices[canon]
        if canon in balances:
            del balances[canon]
        save_json(PRICES_FILE, prices)
        save_json(BALANCES_FILE, balances)

    # Idempotent even if user didn't exist
    return "", 204


@mgmt_bp.put("/balances")
def reset_balances():
    """
    Reset all balances to zero; optionally clear history.

    Body (JSON, optional):
        { "clear_history": true|false } (default false)

    Returns:
        200 JSON:
            {
              "ok": true,
              "prices": { ... },
              "balances": { ... },  # all zeros
              "history": [ ... ]    # empty if clear_history was true
            }
        422 JSON on validation error.
    """
    raw = request.get_json(silent=True) or {}
    try:
        body = ResetBalancesBody.parse_obj(raw)
    except ValidationError as e:
        return jsonify({"ok": False, "errors": e.errors()}), 422

    prices = load_json(PRICES_FILE, {})
    zero_balances = {name: 0.0 for name in prices.keys()}
    save_json(BALANCES_FILE, zero_balances)

    if body.clear_history:
        ensure_history(HISTORY_FILE)   # make sure header/schema exists
        reset_history(HISTORY_FILE)    # clear rows, keep header

    return jsonify({
        "ok": True,
        "prices": prices,
        "balances": zero_balances,
        "history": read_history(HISTORY_FILE),
    }), 200


@mgmt_bp.delete("/history")
def clear_history_route():
    """
    Idempotently clear all transaction rows while preserving CSV header.

    Returns:
        204 No Content (safe to call repeatedly)
    """
    ensure_history(HISTORY_FILE)   # create file + header if missing
    reset_history(HISTORY_FILE)    # remove rows, keep header
    return "", 204
