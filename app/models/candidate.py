"""
Candidate data models based on existing JSON structure
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateStatus(str, Enum):
    WON = "WON"
    LOST = "LOST"


class CandidateType(str, Enum):
    MP = "MP"


class EducationBackground(BaseModel):
    """Education background information"""

    graduation_year: Optional[int] = Field(None, description="Year of graduation")
    stream: Optional[str] = Field(None, description="Field of study/stream")
    college_or_school: Optional[str] = Field(
        None, description="Name of college or school"
    )


class PoliticalElectionHistory(BaseModel):
    """Single election history entry"""

    election_year: Optional[int] = Field(None, description="Year of election")
    election_type: Optional[str] = Field(
        None, description="Type of election (MLA, MP, etc.)"
    )
    constituency: Optional[str] = Field(None, description="Constituency contested from")
    party: Optional[str] = Field(None, description="Party represented")
    status: Optional[str] = Field(None, description="Result status (WON/LOST)")


class PoliticalBackground(BaseModel):
    """Political background and election history"""

    elections: Optional[List[PoliticalElectionHistory]] = Field(
        default_factory=list, description="List of elections contested"
    )


class FamilyMember(BaseModel):
    """Family member information"""

    name: Optional[str] = Field(None, description="Name of family member")
    profession: Optional[str] = Field(None, description="Profession of family member")


class FamilyBackground(BaseModel):
    """Family background information"""

    father: Optional[FamilyMember] = Field(None, description="Father's information")
    mother: Optional[FamilyMember] = Field(None, description="Mother's information")
    spouse: Optional[FamilyMember] = Field(None, description="Spouse's information")
    children: Optional[List[FamilyMember]] = Field(
        default_factory=list, description="Children's information"
    )


class BankDetails(BaseModel):
    """Bank account details"""

    bank_name: Optional[str] = Field(None, description="Name of the bank")
    account_number: Optional[str] = Field(
        None, description="Account number (if available)"
    )
    branch: Optional[str] = Field(None, description="Branch name")


class Assets(BaseModel):
    """Asset information"""

    commercial_assets: Optional[str] = Field(
        None, description="Description of commercial assets"
    )
    cash_assets: Optional[str] = Field(None, description="Description of cash assets")
    bank_details: Optional[List[BankDetails]] = Field(
        default_factory=list, description="Bank account details"
    )


class Candidate(BaseModel):
    """Lok Sabha candidate model with detailed information"""

    id: str
    name: str
    party_id: str
    constituency_id: str
    state_id: str
    image_url: Optional[str] = None
    status: CandidateStatus
    type: CandidateType = CandidateType.MP

    # New detailed fields (all optional)
    education_background: Optional[EducationBackground] = Field(
        None, description="Education background details"
    )
    political_background: Optional[PoliticalBackground] = Field(
        None, description="Political background and election history"
    )
    family_background: Optional[FamilyBackground] = Field(
        None, description="Family background information"
    )
    assets: Optional[Assets] = Field(None, description="Asset information")
