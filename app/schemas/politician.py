"""
Politician Data Model

Unified schema for storing MP and MLA data in a simplified structure.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from .types import (
    STATES,
    PoliticianType,
    QualificationEnum,
    RelationEnum,
    State,
    StatusEnum,
)


class CitationSource(str, Enum):
    """Provenance category for a cited URL."""

    ECI = "ECI"
    MYNETA = "MYNETA"
    GOV_WEBSITE = "GOV_WEBSITE"
    NEWS = "NEWS"
    OTHERS = "OTHERS"


class Citation(BaseModel):
    """A single source backing a detail field."""

    link: HttpUrl
    source: CitationSource


class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SocialMedia(BaseModel):
    twitter: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None


class FamilyMember(BaseModel):
    name: str
    relation: RelationEnum
    photo: Optional[HttpUrl] = None
    social_media: Optional[SocialMedia] = None
    citation: Optional[Citation] = None


class Education(BaseModel):
    qualification: QualificationEnum
    institution: Optional[str] = None
    year_completed: Optional[int] = None
    citation: Optional[Citation] = None


class ElectionRecord(BaseModel):
    year: int
    type: PoliticianType
    state: State
    constituency: str
    party: str
    status: StatusEnum
    citation: Optional[Citation] = None

    @validator("state", pre=True)
    def validate_state(cls, v):
        if isinstance(v, str):
            if v in STATES:
                return v
            # allow enum value names too (e.g., "ANDHRA_PRADESH")
            normalized = v.replace("_", " ").title()
            if normalized in STATES:
                return normalized
        return v


class PoliticalBackground(BaseModel):
    elections: List[ElectionRecord]
    summary: Optional[str] = None
    summary_citation: Optional[Citation] = None


class CrimeType(Enum):
    MURDER = "MURDER"
    RAPE = "RAPE"
    KIDNAPPING = "KIDNAPPING"
    THEFT = "THEFT"
    CORRUPTION = "CORRUPTION"
    ECONOMIC = "ECONOMIC"
    OTHERS = "OTHERS"


class CrimeRecord(BaseModel):
    """
    Record of a criminal case or allegation related to the politician.
    """

    name: str
    type: Optional[CrimeType] = None
    year: Optional[int] = None
    citation: Optional[Citation] = None


class Politician(BaseModel):
    id: str = Field(..., description="Unique ID")
    name: str
    # SEO-friendly politician slug derived from name (+ optional short id suffix).
    # This is generated in the service layer when loading/fetching data.
    slug: Optional[str] = None
    # ISO format timestamp when politician data was last updated
    updated_at: Optional[str] = None
    sourced_pct: Optional[float] = Field(
        None,
        description="Fraction of present checkable fields that carry citations (0-1).",
    )
    cited_fields_count: Optional[int] = Field(
        None,
        description="Number of present checkable fields with citations.",
    )
    checkable_fields_count: Optional[int] = Field(
        None,
        description="Number of present non-null fields eligible for citation coverage.",
    )
    categories_mostly_present: Optional[bool] = Field(
        None,
        description=(
            "True once all but at most one profile category (education, "
            "history, family, criminal, contact, and performance when "
            "applicable) has at least one checkable field."
        ),
    )
    photo: Optional[HttpUrl] = None
    state: State
    constituency: str
    type: PoliticianType = Field(...)

    education: Optional[List[Education]] = None
    family_background: Optional[List[FamilyMember]] = None
    criminal_records: Optional[List[CrimeRecord]] = None

    social_media: Optional[SocialMedia] = None
    contact: Optional[Contact] = None

    political_background: PoliticalBackground

    contact_citations: Optional[Dict[str, Citation]] = Field(
        None,
        description="Keys: email, phone, address — citations for contact fields",
    )
    social_media_citations: Optional[Dict[str, Citation]] = Field(
        None,
        description=("Keys: twitter, facebook, instagram, linkedin, youtube, website"),
    )
    performance_citations: Optional[Dict[str, Citation]] = Field(
        None,
        description="Keys: attendance, questions, debates — Lok Sabha / official stats",
    )
    citation_audit: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional audit metadata: issues, mismatches, last_run",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sasa",
                "name": "",
                "photo": "",
                "state": "",
                "constituency": "",
                "type": "",
                "political_background": {
                    "elections": [
                        {
                            "year": "",
                            "type": "MP",
                            "state": "",
                            "constituency": "",
                            "party": "",
                            "status": "",
                        }
                    ],
                    "summary": None,
                },
                "criminal_records": [{"name": "", "type": "", "year": ""}],
            }
        }


class CitationAuditLLMResult(BaseModel):
    """LLM output shape for citation backfill (CitationAgent) — citations only, aligned by index."""

    education_citations: Optional[List[Optional[Citation]]] = None
    elections_citations: Optional[List[Optional[Citation]]] = None
    family_citations: Optional[List[Optional[Citation]]] = None
    criminal_citations: Optional[List[Optional[Citation]]] = None
    summary_citation: Optional[Citation] = None
    contact_citations: Optional[Dict[str, Optional[Citation]]] = None
    social_media_citations: Optional[Dict[str, Optional[Citation]]] = None
    performance_citations: Optional[Dict[str, Optional[Citation]]] = None
    issues: Optional[List[str]] = None
