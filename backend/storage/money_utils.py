"""
Money Utility – Decimal Rounding

Provides a helper to safely convert numeric inputs into a Decimal with
two decimal places, using ROUND_HALF_UP for financial rounding.

This function is designed for consistent currency handling in the ledger
system and should be used whenever storing or manipulating monetary values.
"""

from decimal import Decimal, ROUND_HALF_UP

def money(value) -> Decimal:
    """
    Convert a value to a Decimal rounded to two decimal places.

    Behavior:
        - Accepts numeric values, numeric strings, or Decimals.
        - Uses `ROUND_HALF_UP` for consistent financial rounding rules.
        - Returns `Decimal('0.00')` if the input is None or cannot be parsed.

    Args:
        value (Any):
            Input value to convert (e.g., Decimal, int, float, str, None).

    Returns:
        Decimal: Monetary value rounded to two decimal places.
    """
    if value is None:
        return Decimal("0.00")
    try:
        d = Decimal(str(value))
    except Exception:
        return Decimal("0.00")
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
