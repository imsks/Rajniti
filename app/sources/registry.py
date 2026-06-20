"""Source registry — load a source module only when explicitly requested."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import List, Optional

_SOURCES: dict[str, str] = {
    "myneta": "app.sources.myneta",
}


def list_sources(*, names: Optional[List[str]] = None) -> list[ModuleType]:
    if not names:
        return []
    modules: list[ModuleType] = []
    for name in names:
        path = _SOURCES.get(name)
        if path is None:
            available = ", ".join(sorted(_SOURCES))
            raise ValueError(f"Unknown source {name!r}. Available: {available}")
        modules.append(importlib.import_module(path))
    return modules
