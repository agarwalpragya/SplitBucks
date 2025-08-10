from decimal import Decimal
from typing import List, Dict
from storage.json_store import load_json, save_json_atomic
from storage.history_store import append_history_row, read_history
from utils.money import D, money
from utils.tie_strategies import select_payer
from utils.time_utils import now_iso
from config import PRICES_FILE, BALANCES_FILE, HISTORY_FILE

def normalize_prices(raw: Dict[str, float]) -> Dict[str, Decimal]:
    return {k: money(D(v)) for k, v in raw.items()}

def normalize_balances(raw: Dict[str, float]) -> Dict[str, Decimal]:
    return {k: money(D(v)) for k, v in raw.items()}

def compute_total_cost(prices: Dict[str, Decimal], people: List[str]):
    included = [p for p in people if p in prices]
    total = sum((prices[p] for p in included), start=Decimal("0"))
    return money(total), included

def run_round(people: List[str], tie_strategy: str):
    prices = normalize_prices(load_json(PRICES_FILE, {}))
    balances = normalize_balances(load_json(BALANCES_FILE, {}))
    if not people:
        people = list(prices.keys())
    total_cost, included = compute_total_cost(prices, people)
    if not included:
        raise ValueError("No provided people match prices")
    payer = select_payer(balances, included, tie_strategy, read_history(HISTORY_FILE))
    for p in included:
        balances[p] = money(balances[p] - prices[p])
    balances[payer] = money(balances[payer] + total_cost)
    save_json_atomic(BALANCES_FILE, {k: float(v) for k, v in balances.items()})
    ts = now_iso()
    append_history_row(HISTORY_FILE, ts, payer, total_cost, included)
    return {
        "timestamp": ts,
        "payer": payer,
        "total_cost": float(total_cost),
        "included": included,
        "tie": tie_strategy,
        "prices": {k: float(v) for k, v in prices.items()},
        "balances": {k: float(v) for k, v in balances.items()},
        "history": read_history(HISTORY_FILE)
    }
