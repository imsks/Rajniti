"""Flat browser-use output schema for MyNeta (no $defs / $ref — extract-tool compatible)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from app.schemas.politician import CrimeRecord, Education, FinancialDisclosure

if TYPE_CHECKING:
    from app.sources.myneta import MyNetaAgentResult


class MyNetaBrowserExtract(BaseModel):
    """Browser-use structured output — dict/list fields only for compatible JSON Schema."""

    financial_disclosure: dict[str, Any]
    education: list[dict[str, Any]] = Field(default_factory=list)
    criminal_records: list[dict[str, Any]] = Field(default_factory=list)


def to_agent_result(extracted: MyNetaBrowserExtract) -> MyNetaAgentResult:
    """Validate flat browser payload against the full politician schema."""
    from app.sources.myneta import MyNetaAgentResult

    payload = extracted.model_dump(mode="python")
    if not payload.get("education"):
        payload["education"] = None
    if not payload.get("criminal_records"):
        payload["criminal_records"] = None
    return MyNetaAgentResult(
        financial_disclosure=FinancialDisclosure.model_validate(payload["financial_disclosure"]),
        education=(
            [Education.model_validate(item) for item in payload["education"]]
            if payload.get("education")
            else None
        ),
        criminal_records=(
            [CrimeRecord.model_validate(item) for item in payload["criminal_records"]]
            if payload.get("criminal_records")
            else None
        ),
    )
