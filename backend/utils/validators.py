"""
Validation Utilities – Participant Name and Price

Provides reusable validation functions for:
    • Ensuring participant names meet allowed character and length requirements.
    • Parsing and validating price values into safely‑rounded Decimals.

These are used across API endpoints such as:
    - /api/set-price
    - /api/remove-person
    - /api/run (via computation helpers)
"""

from decimal import Decimal
from typing import Optional
from .money import D, money

# Allowed name characters: letters, spaces, hyphen, apostrophe
ALLOWED_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")

def validate_person_name(name: str) -> bool:
    """
    Validate a participant name against business rules.

    Rules:
        - Must be a string.
        - Length between 1 and 40 characters (inclusive).
        - Allowed characters: letters (A–Z, a–z), spaces, hyphen (-), apostrophe (').

    Args:
        name (str): Name to validate.

    Returns:
        bool: True if the name is valid; False otherwise.

    Example:
        >>> validate_person_name("Sara O'Connor")
        True
        >>> validate_person_name("Bob123")
        False
    """
    if not isinstance(name, str):
        return False
    name = name.strip()
    if not (1 <= len(name) <= 40):
        return False
    return all(ch in ALLOWED_NAME_CHARS for ch in name)


def parse_price_to_decimal(val) -> Optional[Decimal]:
    """
    Parse a price value into a positive Decimal rounded to currency precision.

    Behavior:
        - Converts using `D()` to avoid float precision issues.
        - Rejects zero and negative values.
        - Returns quantized Decimal using `money()`.

    Args:
        val (Any): Price value as string, int, float, or Decimal.

    Returns:
        Decimal | None:
            Decimal rounded to 2 decimal places if valid (> 0).
            None if parsing fails or value is non-positive.

    Example:
        >>> parse_price_to_decimal("4.5")
        Decimal('4.50')
        >>> parse_price_to_decimal(-2)
        None
    """
    try:
        d = D(val)
        if d <= 0:
            return None
        return money(d)
    except Exception:
        return None
