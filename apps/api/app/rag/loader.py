"""Loads the embedded, prebuilt Chroma index.

In production the index is baked into the image at ``Settings.chroma_index_path``
(read-only). In dev it points at the local Chroma container. This loader is the
single seam for that difference so the rest of the module is agnostic.
"""

from __future__ import annotations

from pathlib import Path


class IndexHandle:
    """Opaque handle to a loaded vector index (stub)."""

    def __init__(self, path: Path) -> None:
        self.path = path


def load_index(index_path: str) -> IndexHandle:
    """Load the embedded index from ``index_path``.

    Placeholder. Real Chroma loading is wired in during migration.
    """
    return IndexHandle(Path(index_path))
