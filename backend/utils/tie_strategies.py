"""
Payer Selection Utility

Determines the next participant to pay in a ledger round based on account
balances, candidate list, transaction history, and a configurable tie-breaking
strategy.

Supported tie-breaking strategies:
    • "alpha"        – Choose the alphabetically first name among ties.
    • "random"       – Choose randomly among ties using SystemRandom.
    • "round_robin"  – Cycle through tied names in a fixed repeating order,
                        based on most recent payer among ties.
    • "least_recent" – (Default) Choose the participant who paid least recently.
                        Those who have never paid are prioritized first.

If no tie-breaking strategy is provided, "least_recent" is used by default.

All timestamps in history are assumed to be ISO‑8601 strings (with 'Z' or
UTC offset), as returned by now_iso().
"""

import secrets
from datetime import datetime
from typing import List, Dict, Optional
from .time_utils import now_iso

# ---------------------------------------------------------------------
# Internal helper functions
# ---------------------------------------------------------------------
def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    """
    Parse an ISO-8601 timestamp string into a datetime object.

    Args:
        ts (str | None): Timestamp string, with optional trailing 'Z'.

    Returns:
        datetime | None: Parsed datetime (UTC-offset aware),
                         or None if parsing fails or input is falsy.
    """
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _last_paid_map(history: List[Dict]) -> Dict[str, Optional[datetime]]:
    """
    Generate a mapping of participant names to their most recent payment datetime.

    Args:
        history (list[dict]): Transaction history entries.

    Returns:
        dict[str, datetime | None]: For each payer, the datetime of their last payment.
    """
    last: Dict[str, Optional[datetime]] = {}
    for row in history or []:
        p = row.get("payer")
        t = _parse_iso(row.get("timestamp"))
        if not p or t is None:
            continue
        if (p not in last) or (t > last[p]):
            last[p] = t
    return last


def _most_recent_from_set(history: List[Dict], names: List[str]) -> Optional[str]:
    """
    Find the most recent payer from a given set of participant names.

    Args:
        history (list[dict]): Transaction history entries.
        names (list[str]): List of participant names to check.

    Returns:
        str | None: Most recently found payer from the set, or None if none found.
    """
    name_set = set(names)
    for row in reversed(history or []):
        p = row.get("payer")
        if p in name_set:
            return p
    return None

# ---------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------
def select_payer(
    balances: Dict[str, float],
    candidates: List[str],
    tie_strategy: str,
    history: List[Dict],
    rng=None
) -> str:
    """
    Select the next payer from the list of candidate participants.

    Args:
        balances (dict[str, float]): Mapping of participant names to their balances.
        candidates (list[str]): Names of participants eligible to pay this round.
        tie_strategy (str): Tie-breaking strategy. Supported values:
            - "alpha"
            - "random"
            - "round_robin"
            - "least_recent" (default)
        history (list[dict]): Transaction history for tie-breaking.
        rng (random.Random, optional): RNG instance (used for testing).

    Raises:
        ValueError: If no candidates are valid (not in balances).

    Returns:
        str: Name of the selected payer.
    """
    # Step 1: Filter candidates to those present in balances
    present = [c for c in candidates if c in balances]
    if not present:
        raise ValueError("No valid candidates")

    # Step 2: Identify participants with the lowest balance
    min_paid = min(balances[c] for c in present)
    ties = [c for c in present if balances[c] == min_paid]
    if len(ties) == 1:
        return ties[0]

    # Step 3: Determine tie-breaking strategy
    s = (tie_strategy or "least_recent").strip().lower()
    rng = rng or secrets.SystemRandom()

    if s == "alpha":
        return sorted(ties)[0]
    if s == "random":
        return rng.choice(ties)
    if s == "round_robin":
        ordered = sorted(ties)
        recent = _most_recent_from_set(history, ordered)
        if not recent:
            return ordered[0]
        i = ordered.index(recent)
        return ordered[(i + 1) % len(ordered)]

    # Step 4: Default strategy – least_recent
    last = _last_paid_map(history)

    def key(name: str):
        # Participants who never paid rank higher (never_rank=0)
        lp = last.get(name)
        never_rank = 0 if lp is None else 1
        return (never_rank, lp or datetime.min, name)

    ties.sort(key=key)
    return ties[0]
