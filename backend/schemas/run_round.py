"""
Schema: Run Round Request

Defines the expected payload for the API endpoint responsible for executing
a payment round.

Behavior & validation:
    • `people` may be omitted/empty → the service will include all known participants.
    • Names are validated (1–40 chars; letters, spaces, hyphen, apostrophe), trimmed,
      and deduplicated case-insensitively while preserving order.
    • `tie` is accepted as any string, normalized to lowercase; unknown values are
      allowed so the service can gracefully fall back to 'least_recent'.
"""

from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, validator

# ---- Name constraints (applied after trimming) -------------------------
NamePattern = r"^[A-Za-z\s\-']+$"

NameType = Annotated[
    str,
    Field(
        min_length=1,
        max_length=40,
        pattern=NamePattern,
        description="Participant name (1–40 chars: letters, spaces, hyphen (-), apostrophe ('))."
    )
]

class RunRoundRequest(BaseModel):
    """
    Request model for executing a payment round.

    Attributes:
        people (list[NameType], optional):
            Participant names to include; empty or omitted means "include all".
        tie (str, optional):
            Tie-breaking hint; normalized to lowercase. Unknown values are allowed
            and handled by the service (default 'least_recent').
    """
    people: Optional[List[NameType]] = Field(
        default_factory=list,
        description="List of participants for this round; empty/omitted includes all."
    )
    tie: Optional[str] = Field(
        default="least_recent",
        description="Tie-breaking hint (e.g., 'least_recent', 'random'); unknown values are allowed."
    )

    # --------- Normalizers & validators ---------------------------------

    @validator("people", pre=True)
    def _default_people_to_list(cls, v):
        # None → []
        return [] if v is None else v

    @validator("people", each_item=True, pre=True)
    def _trim_each_name(cls, v):
        # Trim before pattern/length checks run
        return (v or "").strip()

    @validator("people")
    def _dedupe_case_insensitive_preserve_order(cls, v):
        seen = set()
        out = []
        for name in v:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                out.append(name)
        return out

    @validator("tie", pre=True, always=True)
    def _normalize_tie(cls, v):
        # Accept any string; lowercase it; default to 'least_recent'
        if v is None:
            return "least_recent"
        s = str(v).strip().lower()
        return s or "least_recent"
