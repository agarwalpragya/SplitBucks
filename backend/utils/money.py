"""
Money Utilities – Decimal Precision and Rounding

Provides helpers for currency-safe arithmetic in the ledger system:

Functions:
    • D(x): Safely convert a value to Decimal.
    • money(x): Quantize Decimal values to the configured CENTS precision
                using financial rounding (ROUND_HALF_UP).

All monetary calculations in the system should use these functions to ensure:
    - Consistent precision across services.
    - Avoidance of float rounding errors by converting inputs via string.
    - Proper accounting rounding rules are applied.

CENTS is defined in config.py (Decimal('0.01') for 2dp or similar).
"""

from decimal import Decimal, ROUND_HALF_UP
from config import CENTS


def D(x) -> Decimal:
    """
    Safely convert a value into a Decimal.

    Args:
        x (Any): The input value (numeric, string, or Decimal) to convert.

    Returns:
        Decimal: Decimal representation of the value, created from its string
                 form to avoid binary float precision issues.

    Example:
        >>> D(1.1)
        Decimal('1.1')
    """
    return Decimal(str(x))


def money(x: Decimal) -> Decimal:
    """
    Quantize a Decimal value to the configured CENTS precision.

    Behavior:
        - Uses ROUND_HALF_UP for standard accounting/financial rounding.
        - Expected to be used after all arithmetic to standardize values.

    Args:
        x (Decimal): Input decimal value to round/quantize.

    Returns:
        Decimal: Rounded value to CENTS precision.

    Example:
        >>> from config import CENTS  # Decimal('0.01')
        >>> money(Decimal('2.345'))
        Decimal('2.35')
    """
    return x.quantize(CENTS, rounding=ROUND_HALF_UP)
