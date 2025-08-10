import secrets
from datetime import datetime
from typing import List, Dict, Optional
from .time_utils import now_iso

def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def _last_paid_map(history: List[Dict]) -> Dict[str, Optional[datetime]]:
    last = {}
    for row in history or []:
        p = row.get("payer")
        t = _parse_iso(row.get("timestamp"))
        if not p or t is None:
            continue
        if (p not in last) or (t > last[p]):
            last[p] = t
    return last

def _most_recent_from_set(history: List[Dict], names: List[str]) -> Optional[str]:
    name_set = set(names)
    for row in reversed(history or []):
        p = row.get("payer")
        if p in name_set:
            return p
    return None

def select_payer(balances: Dict[str, float], candidates: List[str], tie_strategy: str, history: List[Dict], rng=None) -> str:
    present = [c for c in candidates if c in balances]
    if not present:
        raise ValueError("No valid candidates")

    min_paid = min(balances[c] for c in present)
    ties = [c for c in present if balances[c] == min_paid]
    if len(ties) == 1:
        return ties[0]

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

    # default: least_recent
    last = _last_paid_map(history)
    def key(name: str):
        lp = last.get(name)
        never_rank = 0 if lp is None else 1
        return (never_rank, lp or datetime.min, name)
    ties.sort(key=key)
    return ties[0]
