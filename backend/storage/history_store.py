"""
History Store – Transaction Log Management

This module manages the persistent CSV file that records all completed
payment rounds in the ledger system. It provides high‑level operations to:

    • Initialize the history file with the required header row.
    • Append new transaction records.
    • Read the complete transaction history into Python objects.
    • Reset the history while preserving the CSV header/schema.

History format (CSV columns):
    timestamp   – ISO‑8601 timestamp of the round execution.
    payer       – Name of the participant who paid in the round.
    total_cost  – Total monetary value of the round (two decimal places).
    people      – '|'‑delimited list of participants included in the round.
"""

import csv
import os
from decimal import Decimal
from typing import List, Dict
from utils.money import money

# Header row for the CSV history file – acts as schema definition
HEADER = ["timestamp", "payer", "total_cost", "people"]

def ensure_history(path: str) -> None:
    """
    Ensure the history CSV file exists with the correct header.

    Behavior:
        - If the file does not exist, its parent directory is created (if needed).
        - Writes a header row matching the `HEADER` constant.

    Args:
        path (str): Full path to the history CSV file.
    """
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

def append_history_row(
    path: str,
    timestamp: str,
    payer: str,
    total_cost: Decimal,
    people: List[str]
) -> None:
    """
    Append a new transaction record to the history CSV.

    Args:
        path (str): Path to the history file.
        timestamp (str): ISO-8601 formatted timestamp of round execution.
        payer (str): Name of the participant who paid.
        total_cost (Decimal): Total cost of the round.
        people (list[str]): Names of participants involved in the round,
                            will be stored as a '|'‑separated string.

    Behavior:
        - Ensures the history file exists before writing.
        - Formats total_cost to two decimal places.
        - Joins participant names into a single pipe-delimited string.
    """
    ensure_history(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            timestamp,
            payer,
            f"{money(total_cost):.2f}",
            "|".join(people)
        ])

def read_history(path: str) -> List[Dict]:
    """
    Read the full transaction history from the CSV file.

    Args:
        path (str): Path to the history file.

    Returns:
        list[dict]: List of transaction records, each containing:
            - timestamp (str)
            - payer (str)
            - total_cost (float): 0.0 if missing
            - people (list[str]): Empty list if missing
        Returns an empty list if the file does not exist.
    """
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

def reset_history(path: str) -> None:
    """
    Clear all transaction records in the history file, preserving the header.

    Args:
        path (str): Path to the history file.

    Behavior:
        - Creates the parent directory if it doesn't exist.
        - Overwrites the file with only the header row.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(HEADER)
