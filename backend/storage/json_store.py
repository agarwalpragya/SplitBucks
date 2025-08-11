import os
import json
import tempfile
import random
from decimal import Decimal
from datetime import datetime
from typing import Optional

from .history_store import ensure_history, read_history
from .money_utils import money

# ---------- JSON helpers ----------
def load_json(path: str, default):
    """Load JSON or return default if file does not exist."""
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    """Atomically write JSON to disk for safety."""
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

# ---------- Data file paths ----------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PRICES_FILE = os.path.join(DATA_DIR, "prices.json")
BALANCES_FILE = os.path.join(DATA_DIR, "balances.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.csv")

# ---------- Normalization ----------
def normalize_prices(raw):
    """Convert raw dict of prices to {name: Decimal} with 2dp."""
    return {k: money(v) for k, v in raw.items()}

def normalize_balances(raw):
    """Convert raw dict of balances to {name: Decimal} with 2dp."""
    return {k: money(v) for k, v in raw.items()}

# ---------- Ensure defaults ----------
def _ensure_defaults():
    """Ensure prices, balances, and history files exist & are seeded."""
    raw_prices = load_json(PRICES_FILE, {})
    raw_balances = load_json(BALANCES_FILE, {})
    ensure_history(HISTORY_FILE)

    # Default prices if none exist
    if not raw_prices:
        raw_prices = {"Bob": 4.50, "Jim": 3.00, "Sara": 5.00}

    prices_dec = normalize_prices(raw_prices)
    balances_dec = normalize_balances(raw_balances)

    # Ensure each person has a balance entry
    for name in prices_dec.keys():
        balances_dec.setdefault(name, Decimal("0.00"))

    # Save JSON back to files
    save_json(PRICES_FILE, {k: float(v) for k, v in prices_dec.items()})
    save_json(BALANCES_FILE, {k: float(v) for k, v in balances_dec.items()})

    return prices_dec, balances_dec

# ---------- Computation helpers ----------
def compute_total_cost(prices: dict[str, Decimal], people: list[str]):
    """Calculate the total cost for a given list of people."""
    included = [p for p in people if p in prices]
    total = sum(prices[p] for p in included) if included else Decimal("0.00")
    return money(total), included

def select_payer(balances: dict[str, Decimal], people: list[str],
                 tie_strategy="least_recent", history=None):
    """Pick who should pay next based on lowest balance and tie-break strategy."""
    lowest_balance = min(balances.get(p, Decimal("0.00")) for p in people)
    tied = [p for p in people if balances.get(p, Decimal("0.00")) == lowest_balance]

    if len(tied) == 1:
        return tied[0]
    if tie_strategy == "random":
        return random.choice(tied)

    # tie_strategy == "least_recent"
    if history:
        last_times = {p: None for p in tied}
        for row in reversed(history):
            if row["payer"] in tied and last_times[row["payer"]] is None:
                last_times[row["payer"]] = row["timestamp"]
        # Oldest timestamp (or None) wins
        sorted_tied = sorted(tied, key=lambda p: last_times[p] or "")
        return sorted_tied[0]

    return tied[0]

# ---------- Misc helpers ----------
def now_iso():
    """Return current UTC datetime in ISO format without microseconds."""
    return datetime.utcnow().replace(microsecond=0).isoformat()

def validate_person_name(name: str) -> bool:
    """Validate person name (only letters, spaces, hyphens, apostrophes)."""
    import re
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s\-']{0,39}", name))

def parse_price_to_decimal(price) -> Optional[Decimal]:
    """Parse a value into a Decimal price > 0, else None."""
    try:
        dec = Decimal(str(price))
    except Exception:
        return None
    return dec.quantize(Decimal("0.01")) if dec > 0 else None
