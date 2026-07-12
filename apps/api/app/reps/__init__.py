"""Reps module — representatives / politicians.

Public facade. Import only from this package root, e.g.
`from app.reps import RepsService, Representative`.
"""

from app.reps.dto import Representative
from app.reps.service import RepsService

__all__ = ["RepsService", "Representative"]
