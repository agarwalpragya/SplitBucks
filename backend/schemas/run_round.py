"""
Schema: Run Round Request

Defines the expected payload for the API endpoint responsible for executing
a payment round.

Validation and business rules:
    • Allows specifying a subset of participants to include in the round.
    • Participant names must meet NameType constraints:
        - 1–40 characters
        - Allowed: letters (A–Z, case-insensitive), spaces, hyphen (-), apostrophe (')
    • Optional tie-breaking strategy supported values:
        - "least_recent"     → Select the participant who paid least recently.
        - "random"           → Select randomly among tied participants.
        - "highest_balance"  → Select the participant with the highest current balance.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Annotated, Literal

# Annotated string type with enforced length and allowed character pattern
NameType = Annotated[
    str,
    Field(
        min_length=1,
        max_length=40,
        pattern=r"^[A-Za-z\s\-']+$",
        description="Participant name (1–40 chars: letters, spaces, hyphen (-), apostrophe ('))."
    )
]

class RunRoundRequest(BaseModel):
    """
    Request model for executing a payment round.

    Attributes:
        people (list[NameType], optional):
            List of participant names to include in the round.
            If omitted or empty, all known participants will be included.

        tie (Literal, optional):
            Strategy for breaking ties when multiple participants are equally eligible to pay.
            Supported values:
                • "least_recent" - Select the participant who paid least recently (default).
                • "random" - Select randomly among tied participants.
                • "highest_balance" - Select the participant with the highest balance.

    This model is used for request validation in the `/run` API endpoint before
    executing the core round logic in the service layer.
    """
    people: Optional[List[NameType]] = Field(
        default_factory=list,
        description="List of participants to include in this round; empty list includes all."
    )
    tie: Optional[Literal["least_recent", "random", "highest_balance"]] = Field(
        default="least_recent",
        description=(
            "Tie-breaking strategy: "
            "'least_recent' (default) = who paid least recently, "
            "'random' = choose randomly, "
            "'highest_balance' = choose highest balance."
        )
    )
