"""
Election data model
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ElectionType(str, Enum):
    LOK_SABHA = "LOK_SABHA"


class Election(BaseModel):
    """Election model for organizing our data"""

    id: str  # e.g., "lok-sabha-2024"
    name: str
    type: ElectionType
    year: int
