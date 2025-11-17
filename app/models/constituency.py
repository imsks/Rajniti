"""
Constituency data model based on existing JSON structure
"""

from pydantic import BaseModel, Field


class Constituency(BaseModel):
    """Constituency model matching existing JSON structure"""

    id: str
    name: str
    state_id: str

    class Config:
        populate_by_name = True
