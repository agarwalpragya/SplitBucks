from decimal import Decimal, ROUND_HALF_UP

def money(value):
    """
    Convert value to Decimal rounded to 2 decimal places.
    Safe for None or invalid input, returns Decimal('0.00') in those cases.
    """
    if value is None:
        return Decimal("0.00")
    try:
        d = Decimal(str(value))
    except Exception:
        return Decimal("0.00")
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
