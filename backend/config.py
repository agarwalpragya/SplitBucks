"""
Application Configuration

This module centralizes configuration values for:
    • Data storage locations (prices, balances, history.
    • Default pricing and balance initialization.
    • Currency rounding precision.
    • Flask host/port/debug settings.

Environment variable overrides are supported via .env (loaded at import time),
allowing deployment‑specific settings without modifying source code.

Environment variables (optional):
    DATA_DIR       – Root directory for JSON/CSV data files.
    PRICES_FILE    – Full path to prices JSON file.
    BALANCES_FILE  – Full path to balances JSON file.
    HISTORY_FILE   – Full path to history CSV file.
    FLASK_HOST     – Host interface for Flask server (default "0.0.0.0").
    FLASK_PORT     – Port for Flask server (default 5000).
    FLASK_DEBUG    – "True" or "False" to enable/disable debug mode.
"""

import os
from decimal import Decimal
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Load environment variables from .env if present
# ---------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------
# Base paths and storage files
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Root directory for storing persistent data (JSON, CSV)
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

# Full file paths for key JSON/CSV storage files
PRICES_FILE = os.getenv("PRICES_FILE", os.path.join(DATA_DIR, "prices.json"))
BALANCES_FILE = os.getenv("BALANCES_FILE", os.path.join(DATA_DIR, "balances.json"))
HISTORY_FILE = os.getenv("HISTORY_FILE", os.path.join(DATA_DIR, "history.csv"))

# ---------------------------------------------------------------------
# Default pricing and balances
# ---------------------------------------------------------------------
DEFAULT_PRICES = {
    "Bob": 4.50,
    "Jim": 3.00,
    "Sara": 5.00,
}

# Default starting balances: zero for all default participants
DEFAULT_BALANCES = {name: 0.0 for name in DEFAULT_PRICES}

# Currency rounding precision (two decimal places)
CENTS = Decimal("0.01")

# ---------------------------------------------------------------------
# Flask application settings
# ---------------------------------------------------------------------
HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = int(os.getenv("FLASK_PORT", 5000))
DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
