"""
Storage Layer – Public API Imports

This module centralizes the import and re‑export of commonly used
storage and ledger helper functions, constants, and utilities.

Responsibilities:
    • Define a clear API surface for other parts of the application
      (avoiding deep imports from storage submodules).
    • Group related JSON and history helper functions in one place.
    • Maintain consistent import style for maintainability.

Modules:
    json_store    – JSON file persistence, currency handling, validation, defaults.
    history_store – Transaction history CSV handling and maintenance.
"""

# ---------------------------------------------------------------------
# JSON store: defaults, persistence, and business rules
# ---------------------------------------------------------------------
from .json_store import (
    _ensure_defaults,           # Ensure baseline JSON files exist with defaults
    PRICES_FILE,                 # File path for prices JSON
    BALANCES_FILE,               # File path for balances JSON
    HISTORY_FILE,                # File path for history CSV
    normalize_prices,            # Parse & normalize prices to Decimal
    normalize_balances,          # Parse & normalize balances to Decimal
    compute_total_cost,          # Calculate total for selected participants
    select_payer,                # Determine next payer using tie-breaking rules
    now_iso,                     # Current UTC timestamp in ISO-8601
    money,                       # Round Decimal to currency precision
    validate_person_name,        # Enforce allowed naming conventions
    parse_price_to_decimal,      # Safe parsing and validation of price
    save_json,                   # Atomic JSON write
    load_json                    # JSON file read with defaults handling
)

# ---------------------------------------------------------------------
# History store: CSV-based transaction log management
# ---------------------------------------------------------------------
from .history_store import (
    ensure_history,              # Create history file with correct header if missing
    read_history,                 # Read all history entries
    append_history_row,           # Append a new row to the history log
    reset_history,                # Wipe history file while keeping header
)
