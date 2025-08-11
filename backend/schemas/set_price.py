"""
Schema: Set Price Request

Defines the expected payload for the API endpoint responsible for creating or
updating a participant's configured price.

Validation rules:
    • Name: 1–40 characters, letters (A–Z, case-insensitive), spaces, hyphen (-), apostrophe (').
    • Price: Must be a positive float value.
"""

from pydantic import BaseModel, Field
from typing import Annotated

# Common participant name type with length and pattern constraints
NameType = Annotated[
    str,
    Field(
        min_length=1,
        max_length=40,
        pattern=r"^[A-Za-z\s\-']+$",
        description="Participant name (1–40 chars: letters, spaces, hyphen (-), apostrophe ('))."
    )
]

class SetPriceRequest(BaseModel):
    """
    Request model for setting or updating the price assigned to a participant.

    Attributes:
        name (str):
            The participant's name. Must satisfy NameType validation constraints.
        price (float):
            The new price to assign to the participant. Must be a positive number.

    This model is used for request validation in the `/set-price` API endpoint
    before applying changes to the price and balance data stores.
    """
    name: NameType
    price: float = Field(
        ...,
        gt=0,
        description="Positive numeric value (> 0) representing the participant's price."
    )
