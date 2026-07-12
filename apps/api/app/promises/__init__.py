"""Promises module — promises made vs kept.

Public facade. Import only from this package root, e.g.
`from app.promises import PromisesService, Promise`.
"""

from app.promises.dto import Promise
from app.promises.service import PromisesService

__all__ = ["PromisesService", "Promise"]
