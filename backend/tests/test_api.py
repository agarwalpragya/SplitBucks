"""
Integration Tests – State and Run Endpoints

This module tests:
    • GET /api/state – retrieval of the current ledger state.
    • POST /api/run  – execution of a payment round.

Tests ensure endpoints:
    - Return a 200 HTTP status for valid requests.
    - Return JSON with expected keys and value types.
    - Behave consistently even with unusual input (e.g., unexpected tie strategy).
"""

def test_state_endpoint(client):
    """
    Verify that the /api/state endpoint:
        - Responds with HTTP 200.
        - Returns a JSON object containing the 'prices' key.
        - Contains 'prices' mapping as a dictionary.
    """
    resp = client.get("/api/state")
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, dict), "Response should be a JSON object"
    assert "prices" in data, "'prices' key must be present in /api/state response"
    assert isinstance(data["prices"], dict), "'prices' should be a dictionary"


def test_run_endpoint_with_unexpected_tie_strategy(client):
    """
    Verify that the /api/run endpoint:
        - Handles unexpected tie strategy values gracefully.
        - Responds with HTTP 200 (graceful degradation, not crash).
        - Response contains a 'payer' key.
        - Returns the expected keys for round execution.
    """
    resp = client.post("/api/run", json={"people": [], "tie": "alpha"})
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, dict), "Response should be a JSON object"
    assert "payer" in data, "'payer' key is missing in /api/run response"
    for expected_key in ["timestamp", "total_cost", "included", "tie", "balances", "prices", "history"]:
        assert expected_key in data, f"Expected key '{expected_key}' missing in response"
