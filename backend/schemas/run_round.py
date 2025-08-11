from pydantic import BaseModel, Field
from typing import List, Optional, Annotated, Literal

# Reuse your existing name validation regex pattern
NameType = Annotated[
    str,
    Field(min_length=1, max_length=40, pattern=r"^[A-Za-z\s\-']+$")
]

class RunRoundRequest(BaseModel):
    people: Optional[List[NameType]] = Field(default_factory=list)
    tie: Optional[Literal["least_recent", "random", "highest_balance"]] = Field(default="least_recent")
