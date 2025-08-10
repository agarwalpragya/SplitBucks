from pydantic import BaseModel, Field
from typing import List, Optional

class RunRoundRequest(BaseModel):
    people: Optional[List[str]] = Field(default_factory=list)
    tie: Optional[str] = Field(default="least_recent")
