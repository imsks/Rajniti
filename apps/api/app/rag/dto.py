"""DTOs crossing the rag boundary."""

from __future__ import annotations

from pydantic import BaseModel


class RagQuery(BaseModel):
    text: str
    top_k: int = 5


class RagChunk(BaseModel):
    source: str
    content: str
    score: float


class RagResult(BaseModel):
    query: str
    chunks: list[RagChunk] = []
    answer: str | None = None
