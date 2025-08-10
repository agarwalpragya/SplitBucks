import csv
import os
from decimal import Decimal
from typing import List, Dict
from utils.money import money

HEADER = ["timestamp", "payer", "total_cost", "people"]

def ensure_history(path: str):
    """Create history CSV file with header if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

def append_history_row(path: str, timestamp: str, payer: str, total_cost: Decimal, people: List[str]):
    """Append a single round to history."""
    ensure_history(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([timestamp, payer, f"{money(total_cost):.2f}", "|".join(people)])

def read_history(path: str) -> List[Dict]:
    """Read history CSV into list of dicts."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [
            {
                "timestamp": row["timestamp"],
                "payer": row["payer"],
                "total_cost": float(row["total_cost"]) if row["total_cost"] else 0.0,
                "people": row["people"].split("|") if row["people"] else [],
            }
            for row in csv.DictReader(f)
        ]

def reset_history(path: str):
    """Clear history but keep header."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(HEADER)
