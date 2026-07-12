"""DTOs crossing the promises boundary."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class PromiseStatus(StrEnum):
    made = "made"
    in_progress = "in_progress"
    kept = "kept"
    broken = "broken"


class Promise(BaseModel):
    id: str
    representative_id: str
    text: str
    status: PromiseStatus = PromiseStatus.made
    sources: list[str] = []
