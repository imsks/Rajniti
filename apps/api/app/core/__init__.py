"""Shared infrastructure: settings, logging, exceptions.

`core` is unrestricted — any module may import from it.
"""

from app.core.config import Settings

__all__ = ["Settings"]
