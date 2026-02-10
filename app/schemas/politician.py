"""
Politician Data Model

Unified schema for storing MP and MLA data in a simplified structure.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal
from datetime import date


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
    relation: str  # e.g., "Father", "Spouse", "Sibling"
    photo: Optional[HttpUrl] = None
    social_media: Optional[SocialMedia] = None


class Education(BaseModel):
    qualification: str  # e.g., "BA in Political Science"
    institution: Optional[str] = None
    year_completed: Optional[int] = None


class ElectionRecord(BaseModel):
    year: int
    type: str  # "MP" or "MLA"
    state: str
    constituency: str
    party: str
    status: str  # "WON" or "LOST"


class PoliticalBackground(BaseModel):
    elections: List[ElectionRecord]
    summary: Optional[str] = None  # AI generated summary (optional)


class Politician(BaseModel):
    id: str = Field(..., description="Unique ID like 'mp_2024_s01_5' or 'mla_2025_cg_123'")
    name: str
    photo: Optional[HttpUrl] = None
    state: str
    constituency: str
    type: Literal["MP", "MLA"] = Field(...)
    
    education: Optional[Education] = None
    family_background: Optional[List[FamilyMember]] = None
    
    social_media: Optional[SocialMedia] = None
    contact: Optional[Contact] = None

    political_background: PoliticalBackground

    notes: Optional[str] = Field(None, description="Optional human notes or comments")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "mp_2024_s01_5",
                "name": "C.M.RAMESH",
                "photo": "https://results.eci.gov.in/uploads4/candprofile/2024/PC/E24/S01/RAMES-2024-7564.jpg",
                "state": "Andhra Pradesh",
                "constituency": "Anakapalle",
                "type": "MP",
                "political_background": {
                    "elections": [
                        {
                            "year": 2024,
                            "type": "MP",
                            "state": "Andhra Pradesh",
                            "constituency": "Anakapalle",
                            "party": "Bharatiya Janata Party",
                            "status": "WON"
                        }
                    ],
                    "summary": None
                }
            }
        }
