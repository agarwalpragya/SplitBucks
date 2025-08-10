def test_state_endpoint(client):
    resp = client.get("/api/state")
    assert resp.status_code == 200
    assert "prices" in resp.get_json()

def test_run_endpoint(client):
    resp = client.post("/api/run", json={"people": [], "tie": "alpha"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "payer" in data
