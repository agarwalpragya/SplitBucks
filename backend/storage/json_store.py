"""
Storage Utilities – JSON Data Management and Core Ledger Helpers

This module provides:
    • Safe persistence and retrieval of JSON-based data files.
    • Default file paths for prices, balances, and transaction history.
    • Normalization of monetary values to Decimal with two decimal places.
    • Automatic initialization of default data (prices, balances, history).
    • Core ledger computations:
        - Total cost calculation for a group of participants.
        - Determining the next payer using tie-breaking strategies.
    • Input validation helpers for participant names and prices.
    • Timestamp utility for standardized ISO-8601 formatting.

All file writes are atomic to prevent data corruption.
All currency values are internally managed as Decimal for precision.

Intended for use by service-layer business logic and API endpoints.
"""

import os
import json
import tempfile
import random
from decimal import Decimal
from datetime import datetime
from typing import Optional

from .history_store import ensure_history, read_history
from .money_utils import money

# ---------------------------------------------------------------------
# JSON File Persistence Helpers
# ---------------------------------------------------------------------
def load_json(path: str, default):
    """
    Load JSON data from disk.

    Args:
        path (str): Full path to the JSON file.
        default: Fallback return value if file does not exist.

    Returns:
        object: Parsed JSON data, or `default` if file not found.
    """
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data):
    """
    Save JSON data to disk atomically.

    Behavior:
        - Writes to a temporary file then replaces the target file
          to avoid corruption if the process is interrupted.
        - Creates parent directories if missing.

    Args:
        path (str): Full path to the JSON file.
        data: Python object to serialize as JSON.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_ = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=dir_, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

# ---------------------------------------------------------------------
# Data File Paths
# ---------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PRICES_FILE = os.path.join(DATA_DIR, "prices.json")
BALANCES_FILE = os.path.join(DATA_DIR, "balances.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.csv")

# ---------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------
def normalize_prices(raw):
    """
    Convert a raw dictionary of prices into Decimal values.

    Args:
        raw (dict[str, Any]): Mapping of participant names to numeric price values.

    Returns:
        dict[str, Decimal]: Mapping with values rounded to 2 decimal places.
    """
    return {k: money(v) for k, v in raw.items()}


def normalize_balances(raw):
    """
    Convert a raw dictionary of balances into Decimal values.

    Args:
        raw (dict[str, Any]): Mapping of participant names to numeric balance values.

    Returns:
        dict[str, Decimal]: Mapping with values rounded to 2 decimal places.
    """
    return {k: money(v) for k, v in raw.items()}

# ---------------------------------------------------------------------
# Ensure Default Data Exists
# ---------------------------------------------------------------------
def _ensure_defaults():
    """
    Ensure price, balance, and history files exist and are initialized.

    Behavior:
        - Loads stored prices and balances if present.
        - Seeds default prices if no price data exists.
        - Initializes missing balance entries for all priced participants.
        - Ensures history CSV file exists with header.
        - Persists normalized prices and balances back to disk.

    Returns:
        tuple:
            prices_dec (dict[str, Decimal]): Normalized prices mapping.
            balances_dec (dict[str, Decimal]): Normalized balances mapping.
    """
    raw_prices = load_json(PRICES_FILE, {})
    raw_balances = load_json(BALANCES_FILE, {})
    ensure_history(HISTORY_FILE)

    # Default prices if none exist
    if not raw_prices:
        raw_prices = {"Bob": 4.50, "Jim": 3.00, "Sara": 5.00}

    prices_dec = normalize_prices(raw_prices)
    balances_dec = normalize_balances(raw_balances)

    # Ensure each person has a corresponding balance entry
    for name in prices_dec:
        balances_dec.setdefault(name, Decimal("0.00"))

    # Save back the normalized data
    save_json(PRICES_FILE, {k: float(v) for k, v in prices_dec.items()})
    save_json(BALANCES_FILE, {k: float(v) for k, v in balances_dec.items()})

    return prices_dec, balances_dec

# ---------------------------------------------------------------------
# Computation Helpers
# ---------------------------------------------------------------------
def compute_total_cost(prices: dict[str, Decimal], people: list[str]):
    """
    Calculate the total price for a given subset of participants.

    Args:
        prices (dict[str, Decimal]): Mapping of names to prices.
        people (list[str]): Names to include in the calculation.

    Returns:
        tuple:
            total (Decimal): Total sum of included participants' prices.
            included (list[str]): Valid participant names found in `prices`.
    """
    included = [p for p in people if p in prices]
    total = sum(prices[p] for p in included) if included else Decimal("0.00")
    return money(total), included


def select_payer(
    balances: dict[str, Decimal],
    people: list[str],
    tie_strategy="least_recent",
    history=None
):
    """
    Select the next payer based on balances and tie-breaking rules.

    Args:
        balances (dict[str, Decimal]): Mapping of participant balances.
        people (list[str]): Names considered eligible to pay.
        tie_strategy (str): One of:
            - "least_recent": Participant who paid least recently (default).
            - "random": Randomly pick among ties.
        history (list[dict], optional): Transaction history used for tie-breaking.

    Returns:
        str: Name of the selected payer.
    """
    # Step 1: Find the set of participants with the lowest balance
    lowest_balance = min(balances.get(p, Decimal("0.00")) for p in people)
    tied = [p for p in people if balances.get(p, Decimal("0.00")) == lowest_balance]

    if len(tied) == 1:
        return tied[0]
    if tie_strategy == "random":
        return random.choice(tied)

    # Default: tie_strategy == "least_recent"
    if history:
        last_times = {p: None for p in tied}
        for row in reversed(history):
            if row["payer"] in tied and last_times[row["payer"]] is None:
                last_times[row["payer"]] = row["timestamp"]
        # Pick the participant with no recent payment or oldest timestamp
        sorted_tied = sorted(tied, key=lambda p: last_times[p] or "")
        return sorted_tied[0]

    return tied[0]  # fallback if no history

# ---------------------------------------------------------------------
# Miscellaneous Helpers
# ---------------------------------------------------------------------
def now_iso():
    """
    Get the current UTC timestamp in ISO-8601 format without microseconds.

    Returns:
        str: Timestamp string (e.g., '2025-08-10T23:45:00').
    """
    return datetime.utcnow().replace(microsecond=0).isoformat()


def validate_person_name(name: str) -> bool:
    """
    Validate a participant name against allowed naming conventions.

    Rules:
        - Must start with a letter.
        - May include letters, spaces, hyphens, and apostrophes.
        - Maximum length: 40 characters.

    Args:
        name (str): Name string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    import re
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s\-']{0,39}", name))


def parse_price_to_decimal(price) -> Optional[Decimal]:
    """
    Convert an input value to a positive Decimal price.

    Args:
        price (Any): Value to parse (string, int, float).

    Returns:
        Decimal: Value rounded to 2 decimal places if > 0.
        None: If parsing fails or value is not positive.
    """
    try:
        dec = Decimal(str(price))
    except Exception:
        return None
    return dec.quantize(Decimal("0.01")) if dec > 0 else None
