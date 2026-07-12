"""DTOs crossing the reps boundary."""

from __future__ import annotations

from pydantic import BaseModel


class Representative(BaseModel):
    id: str
    name: str
    house: str  # e.g. "MP" | "MLA"
    constituency: str
    party: str | None = None
