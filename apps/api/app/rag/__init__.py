"""RAG module — retrieval over the embedded Chroma index.

Public facade. Import only from this package root, e.g.
`from app.rag import RagService, RagQuery, RagResult`.
"""

from app.rag.dto import RagQuery, RagResult
from app.rag.service import RagService

__all__ = ["RagService", "RagQuery", "RagResult"]
