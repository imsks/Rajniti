"""
Party data model based on existing JSON structure
"""

from pydantic import BaseModel, Field


class Party(BaseModel):
    """Party model matching existing JSON structure"""

    id: str
    name: str
    short_name: str
    symbol: str = ""

    class Config:
        populate_by_name = True
