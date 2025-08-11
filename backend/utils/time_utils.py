"""
Time Utilities – ISO 8601 UTC Timestamps

Provides a helper to consistently generate the current UTC timestamp
in ISO‑8601 format for use in API responses and history logging.
"""

from datetime import datetime, timezone

def now_iso() -> str:
    """
    Get the current UTC time as an ISO‑8601 formatted string.

    Behavior:
        - Always returns UTC time with timezone offset included.
        - Uses ISO 8601 formatting (e.g., '2025-08-11T01:23:45+00:00').
        - Microseconds are omitted for cleaner log output.

    Returns:
        str: Current UTC time in ISO‑8601 format.

    Example:
        >>> now_iso()
        '2025-08-11T01:23:45+00:00'
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
