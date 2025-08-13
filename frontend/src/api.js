/**
 * API client
 *
 * Routes:
 *   GET    /api/state
 *   GET    /api/next?people=...&tie=...
 *   POST   /api/run                       (executes a round)
 *   PUT    /api/users/:name/price         (idempotent upsert)
 *   DELETE /api/users/:name               (idempotent, 204)
 *   PUT    /api/balances                  (reset; optional { clear_history })
 *   DELETE /api/history                   (idempotent, 204)
 */
export const api = {
  // Get full app state (prices, balances, history)
  async state() {
    const r = await fetch('/api/state');
    if (!r.ok) throw new Error('state failed');
    return r.json();
  },

  // Get suggested next payer (optionally limit to people, tie strategy)
  async next(people, tie) {
    const params = new URLSearchParams();
    (people || []).forEach(p => params.append('people', p));
    if (tie) params.set('tie', tie);
    const r = await fetch('/api/next?' + params.toString());
    if (!r.ok) throw new Error('next failed');
    return r.json();
  },

  // Execute a round (mutates balances & history)
  async run(people, tie) {
    const r = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ people, tie })
    });
    if (!r.ok) throw new Error('run failed');
    return r.json();
  },

  // Create/update a user's price (idempotent)
  async setPrice(name, price) {
    const r = await fetch(`/api/users/${encodeURIComponent(name)}/price`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price })
    });
    if (!r.ok) throw new Error('set-price failed');
    return r.json();
  },

  // Reset all balances to zero; optionally clear history
  async resetBalances(clear_history = false) {
    const r = await fetch('/api/balances', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clear_history })
    });
    if (!r.ok) throw new Error('reset failed');
    return r.json();
  },

  // Clear history (idempotent 204) then refresh state
  async clearHistory() {
    const r = await fetch('/api/history', { method: 'DELETE' });
    if (!(r.status === 204 || r.ok)) throw new Error('clear-history failed');
    return this.state();
  },

  // Remove a user (idempotent 204) then refresh state
  async removePerson(name) {
    const r = await fetch(`/api/users/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    });
    if (!(r.status === 204 || r.ok)) throw new Error('remove failed');
    return this.state();
  }
};
