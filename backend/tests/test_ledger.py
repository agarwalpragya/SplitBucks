from decimal import Decimal
from services import ledger_service

def test_run_round_updates_balances(tmp_path):
    prices_file = tmp_path / "prices.json"
    balances_file = tmp_path / "balances.json"
    history_file = tmp_path / "history.csv"

    prices_file.write_text('{"A": 3.0, "B": 5.0}')
    balances_file.write_text('{"A": 0.0, "B": 0.0}')

    ledger_service.PRICES_FILE = str(prices_file)
    ledger_service.BALANCES_FILE = str(balances_file)
    ledger_service.HISTORY_FILE = str(history_file)

    result = ledger_service.run_round(["A", "B"], "alpha")
    assert "payer" in result
    assert all(isinstance(v, float) for v in result["balances"].values())
