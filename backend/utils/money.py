from decimal import Decimal, ROUND_HALF_UP
from config import CENTS

def D(x) -> Decimal:
    return Decimal(str(x))

def money(x: Decimal) -> Decimal:
    return x.quantize(CENTS, rounding=ROUND_HALF_UP)
