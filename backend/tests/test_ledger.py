"""
Unit Tests – ledger_service.run_round

Verifies that:
    • The run_round() function updates balances correctly (zero-sum model).
    • All balances are returned as floats in API-compatible form.
    • A history record is appended.
    • Unknown tie strategies are handled gracefully.
"""

from services import ledger_service


def test_run_round_updates_balances_and_history(tmp_path):
    """
    GIVEN
        - Two participants ("A" and "B") with prices 3.0 and 5.0.
        - Initial balances of 0.0 each.
    WHEN
        - run_round() is called with both participants and a non-standard
          tie-breaking strategy string 'alpha'.
    THEN
        - The result dictionary contains a 'payer' key with a valid participant name.
        - The 'balances' values are floats (JSON friendly).
        - Participant balances reflect debits of their own price and a credit
          to the payer for the total (zero-sum).
        - The history contains exactly one new transaction record.
    """
    # Arrange: create isolated test JSON/CSV files
    prices_file = tmp_path / "prices.json"
    balances_file = tmp_path / "balances.json"
    history_file = tmp_path / "history.csv"

    prices_file.write_text('{"A": 3.0, "B": 5.0}')
    balances_file.write_text('{"A": 0.0, "B": 0.0}')

    # Point the service at the temp files
    ledger_service.PRICES_FILE = str(prices_file)
    ledger_service.BALANCES_FILE = str(balances_file)
    ledger_service.HISTORY_FILE = str(history_file)

    # Act: execute a round (unknown tie strategy should gracefully fall back)
    result = ledger_service.run_round(["A", "B"], "alpha")

    # Assert: basic structure
    assert "payer" in result, "Result must contain 'payer'"
    assert result["payer"] in ["A", "B"], "Payer must be one of the participants"

    # Balances must be floats
    assert all(isinstance(v, float) for v in result["balances"].values()), \
        "All balances should be serialized to floats"

    # Zero-sum ledger logic:
    # - Each included participant is debited by their own price
    # - Payer is credited with the total of all included prices
    prices = result["prices"]  # use what the service returned (floats)
    total_cost = sum(prices.values())
    payer = result["payer"]
    payer_balance = result["balances"][payer]

    # Because the payer is also debited their own price, their net = total - own_price
    expected_payer_balance = total_cost - prices[payer]
    assert abs(payer_balance - expected_payer_balance) < 1e-4, \
        "Payer's balance should equal total minus their own price (zero-sum)"

    # Zero-sum invariant across all balances
    assert abs(sum(result["balances"].values())) < 1e-4, \
        "Balances should sum to ~0 in a zero-sum ledger"

    # History should contain exactly one entry with matching fields
    assert len(result["history"]) == 1, "Exactly one history entry should exist"
    history_entry = result["history"][0]
    assert history_entry["payer"] == result["payer"]
    assert abs(history_entry["total_cost"] - total_cost) < 1e-4
    assert set(history_entry["people"]) == {"A", "B"}
