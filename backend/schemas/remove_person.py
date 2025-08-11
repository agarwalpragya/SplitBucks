"""
Schema: Remove Person Request

Defines the expected payload for the API endpoint responsible for removing a
participant from the system's prices and balances data stores.

Validation constraints:
    • Name is required (min length: 1 character, max length: 40 characters).
    • Allowed characters: letters (A–Z, case-insensitive), spaces, hyphen (-), and apostrophe (').
"""

from pydantic import BaseModel, Field
from typing import Annotated

# Annotated string type with enforced length and pattern constraints
NameType = Annotated[
    str,
    Field(
        min_length=1,
        max_length=40,
        pattern=r"^[A-Za-z\s\-']+$",
        description="Participant name. 1–40 chars: letters, spaces, hyphen (-), apostrophe (')."
    )
]

class RemovePersonRequest(BaseModel):
    """
    Request model for removing an existing participant.

    Attributes:
        name (str): The exact participant name to remove.
                    Must satisfy NameType validation constraints.

    This model is used for request validation in the `/remove-person` API endpoint
    before any deletion logic is executed.
    """
    name: NameType
