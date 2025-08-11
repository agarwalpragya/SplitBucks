"""
Unit Tests – Core Ledger Utilities

Covers:
    • compute_total_cost – Summing participant prices and filtering missing users.
    • select_payer – Tie-breaking behavior, including handling of unsupported strategies.
    • History store round-trip – Appending and reading transaction records.
"""

import csv
from decimal import Decimal
import tempfile
from storage.history_store import append_history_row, read_history
from services.ledger_service import compute_total_cost
from utils.tie_strategies import select_payer
from utils.money import money

def test_compute_total_cost_with_all_participants():
    """
    GIVEN two participants with prices 3.00 and 7.00
    WHEN compute_total_cost is called with both names
    THEN total should be 10.00 and both names returned as included
    """
    prices = {"A": Decimal("3.00"), "B": Decimal("7.00")}
    total, included = compute_total_cost(prices, ["A", "B"])
    assert total == Decimal("10.00")
    assert included == ["A", "B"]

def test_compute_total_cost_ignores_missing_names():
    """
    GIVEN a participant price dict missing some requested names
    WHEN compute_total_cost is called with one valid and one invalid name
    THEN total should equal sum for valid participants and only those should be included
    """
    prices = {"A": Decimal("3.00")}
    total, included = compute_total_cost(prices, ["A", "X"])
    assert total == Decimal("3.00")
    assert included == ["A"]

def test_select_payer_with_unknown_strategy_defaults_to_first():
    """
    GIVEN two participants with the same balance
    WHEN select_payer is called with an unsupported tie strategy 'alpha'
    THEN the function should default to returning the first tied participant ('Ann')
    """
    balances = {"Ann": Decimal("5.00"), "Bob": Decimal("5.00")}
    payer = select_payer(balances, ["Ann", "Bob"], "alpha", history=[])
    assert payer == "Ann"

def test_history_append_and_read_round_trip(tmp_path):
    """
    GIVEN an empty CSV history file
    WHEN a row is appended and history is read back
    THEN the record should exactly match the written data (with float cost and correct participant list)
    """
    history_file = tmp_path / "history.csv"
    append_history_row(history_file, "2024-01-01T00:00:00+00:00", "Ann", Decimal("10.00"), ["Ann", "Bob"])

    hist = read_history(history_file)
    assert len(hist) == 1
    assert hist[0]["payer"] == "Ann"
    assert abs(hist[0]["total_cost"] - 10.0) < 0.001
    assert hist[0]["people"] == ["Ann", "Bob"]
