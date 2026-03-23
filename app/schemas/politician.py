"""
Politician Data Model

Unified schema for storing MP and MLA data in a simplified structure.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from .types import (
    STATES,
    PoliticianType,
    QualificationEnum,
    RelationEnum,
    State,
    StatusEnum,
)


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


class Education(BaseModel):
    qualification: QualificationEnum
    institution: Optional[str] = None
    year_completed: Optional[int] = None


class ElectionRecord(BaseModel):
    year: int
    type: PoliticianType
    state: State
    constituency: str
    party: str
    status: StatusEnum

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


class Politician(BaseModel):
    id: str = Field(..., description="Unique ID")
    name: str
    # SEO-friendly politician slug derived from name (+ optional short id suffix).
    # This is generated in the service layer when loading/fetching data.
    slug: Optional[str] = None
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

    notes: Optional[str] = Field(None, description="Optional human notes or comments")

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
