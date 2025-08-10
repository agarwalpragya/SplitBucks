import csv
from decimal import Decimal
import tempfile
from storage.history_store import append_history_row, read_history
from services.ledger_service import compute_total_cost
from utils.tie_strategies import select_payer
from utils.money import money

def test_compute_total_cost_normal():
    prices = {"A": Decimal("3.00"), "B": Decimal("7.00")}
    total, included = compute_total_cost(prices, ["A", "B"])
    assert total == Decimal("10.00")
    assert included == ["A", "B"]

def test_compute_total_cost_ignores_missing():
    prices = {"A": Decimal("3.00")}
    total, included = compute_total_cost(prices, ["A", "X"])
    assert total == Decimal("3.00")
    assert included == ["A"]

def test_select_payer_alpha():
    balances = {"Ann": Decimal("5.00"), "Bob": Decimal("5.00")}
    payer = select_payer(balances, ["Ann", "Bob"], "alpha", history=[])
    assert payer == "Ann"

def test_history_round_trip():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        history_file = tmp.name
    append_history_row(history_file, "2024-01-01T00:00:00+00:00", "Ann", Decimal("10.00"), ["Ann", "Bob"])
    hist = read_history(history_file)
    assert hist[0]["payer"] == "Ann"
    assert abs(hist[0]["total_cost"] - 10.0) < 0.001
    assert hist[0]["people"] == ["Ann", "Bob"]
