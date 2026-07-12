"""RAG facade.

Retrieves relevant chunks from the embedded index and, when synthesis is
needed, delegates to the agents module (a legal downward dependency:
rag -> agents).
"""

from __future__ import annotations

from app.agents import AgentsService, AgentTask
from app.rag.dto import RagQuery, RagResult


class RagService:
    def __init__(self, agents: AgentsService | None = None) -> None:
        self._agents = agents or AgentsService()

    def query(self, query: RagQuery, *, synthesize: bool = False) -> RagResult:
        """Retrieve chunks for ``query``; optionally synthesize an answer.

        Placeholder retrieval. Real Chroma retrieval is wired in during
        migration.
        """
        result = RagResult(query=query.text, chunks=[])

        if synthesize:
            agent_result = self._agents.run(
                AgentTask(kind="rag_synthesis", prompt=query.text)
            )
            result.answer = agent_result.answer

        return result
