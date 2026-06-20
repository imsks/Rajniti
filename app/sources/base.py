"""Minimal types for source merge pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SourceResult:
    source_name: str
    data: Dict[str, Any]
    priority: int = 0
    issues: list[str] = field(default_factory=list)
