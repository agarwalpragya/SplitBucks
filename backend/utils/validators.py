from decimal import Decimal
from typing import Optional
from .money import D, money

ALLOWED_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")

def validate_person_name(name: str) -> bool:
    if not isinstance(name, str):
        return False
    name = name.strip()
    if not (1 <= len(name) <= 40):
        return False
    return all(ch in ALLOWED_NAME_CHARS for ch in name)

def parse_price_to_decimal(val) -> Optional[Decimal]:
    try:
        d = D(val)
        if d <= 0:
            return None
        return money(d)
    except Exception:
        return None
