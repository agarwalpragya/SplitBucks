import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()  # Load .env if present

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

PRICES_FILE = os.getenv("PRICES_FILE", os.path.join(DATA_DIR, "prices.json"))
BALANCES_FILE = os.getenv("BALANCES_FILE", os.path.join(DATA_DIR, "balances.json"))
HISTORY_FILE = os.getenv("HISTORY_FILE", os.path.join(DATA_DIR, "history.csv"))

DEFAULT_PRICES = {
    "Bob": 4.50,
    "Jim": 3.00,
    "Sara": 5.00,
}
DEFAULT_BALANCES = {name: 0.0 for name in DEFAULT_PRICES}
CENTS = Decimal("0.01")

HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = int(os.getenv("FLASK_PORT", 5000))
DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
