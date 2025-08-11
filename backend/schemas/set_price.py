from pydantic import BaseModel, Field
from typing import Annotated

NameType = Annotated[
    str,
    Field(min_length=1, max_length=40, pattern=r"^[A-Za-z\s\-']+$")
]

class SetPriceRequest(BaseModel):
    name: NameType
    price: float
