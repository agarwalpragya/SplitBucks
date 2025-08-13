"""
Ledger Service – Payment Round Execution

Core business logic for executing a "round":
  • Load & normalize prices/balances
  • Compute total for selected participants
  • Select payer (tie strategies)
  • Update balances (zero-sum)
  • Append history row
  • Return a full snapshot (JSON-friendly floats)

Tests can override PRICES_FILE / BALANCES_FILE / HISTORY_FILE at runtime.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Dict, Tuple

# File IO helpers
from storage.json_store import load_json, save_json
from storage.history_store import append_history_row, read_history

# Money & utilities
from utils.money import D, money
from utils.tie_strategies import select_payer
from utils.time_utils import now_iso

# Default file locations (tests may override these module globals)
from config import (
    PRICES_FILE as _PRICES_FILE,
    BALANCES_FILE as _BALANCES_FILE,
    HISTORY_FILE as _HISTORY_FILE,
)

# Exposed, overrideable by tests:
PRICES_FILE: str = _PRICES_FILE
BALANCES_FILE: str = _BALANCES_FILE
HISTORY_FILE: str = _HISTORY_FILE


def normalize_prices(raw: Dict[str, float]) -> Dict[str, Decimal]:
    """Convert raw price mappings into normalized Decimal values (currency-quantized)."""
    return {name: money(D(value)) for name, value in raw.items()}


def normalize_balances(raw: Dict[str, float]) -> Dict[str, Decimal]:
    """Convert raw balance mappings into normalized Decimal values (currency-quantized)."""
    return {name: money(D(value)) for name, value in raw.items()}


def compute_total_cost(prices: Dict[str, Decimal], people: List[str]) -> Tuple[Decimal, List[str]]:
    """
    Sum prices for participants that exist in `prices`; filter out unknown names.
    Returns (total, included_names).
    """
    included = [p for p in people if p in prices]
    total = sum((prices[p] for p in included), start=Decimal("0"))
    return money(total), included


def run_round(people: List[str], tie_strategy: str) -> Dict:
    """
    Execute a payment round: determine payer, update balances, and record history.

    Args:
        people: participants to include; if empty/None, includes all with configured prices.
        tie_strategy: tie-breaking hint (unknown values should gracefully fallback).

    Returns:
        A dict snapshot with timestamp, payer, total_cost, included, tie, prices, balances, history.

    Raises:
        ValueError: if no provided people match configured prices.
    """
    # Load and normalize state
    prices_raw = load_json(PRICES_FILE, {})
    balances_raw = load_json(BALANCES_FILE, {})
    prices = normalize_prices(prices_raw)
    balances = normalize_balances(balances_raw)

    # Default to all participants if none provided
    if not people:
        people = list(prices.keys())

    # Compute total & validate included
    total_cost, included = compute_total_cost(prices, people)
    if not included:
        raise ValueError("No provided people match prices")

    # Choose payer (history-aware tie-breaking)
    # NOTE: first two args must be positional to match existing select_payer signature.
    payer = select_payer(
        balances,
        included,
        tie_strategy=tie_strategy,
        history=read_history(HISTORY_FILE),
    )

    # Apply zero-sum balance updates (hardened with .get(..., 0) for robustness)
    for participant in included:
        balances[participant] = money(
            balances.get(participant, Decimal("0")) - prices[participant]
        )
    balances[payer] = money(balances.get(payer, Decimal("0")) + total_cost)

    # Persist balances as floats (JSON-friendly)
    save_json(BALANCES_FILE, {k: float(v) for k, v in balances.items()})

    # Append history row
    timestamp = now_iso()
    append_history_row(HISTORY_FILE, timestamp, payer, total_cost, included)

    # Return snapshot (floats for JSON ergonomics)
    return {
        "timestamp": timestamp,
        "payer": payer,
        "total_cost": float(total_cost),
        "included": included,
        "tie": tie_strategy,
        "prices": {k: float(v) for k, v in prices.items()},
        "balances": {k: float(v) for k, v in balances.items()},
        "history": read_history(HISTORY_FILE),
    }


__all__ = [
    "PRICES_FILE",
    "BALANCES_FILE",
    "HISTORY_FILE",
    "normalize_prices",
    "normalize_balances",
    "compute_total_cost",
    "run_round",
]
