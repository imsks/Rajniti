"""
Questions Service — semantic Q&A over politician data via ChromaDB.

Provides predefined questions and free-form search.
"""

import logging
from typing import Any, Dict, List

from app.schemas.questions import PREDEFINED_QUESTIONS

logger = logging.getLogger(__name__)


class QuestionsService:
    """Answer questions using semantic search over the politician vector DB."""

    def __init__(self) -> None:
        from app.services.vector_db_service import VectorDBService

        self.vdb = VectorDBService()
        logger.info("QuestionsService ready (docs: %d)", self.vdb.count())

    def get_predefined_questions(self) -> List[Dict[str, Any]]:
        return PREDEFINED_QUESTIONS.copy()

    def answer_question(
        self,
        question: str,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Semantic search and format the answer."""
        try:
            results = self.vdb.search(question, n_results=n_results)

            if not results:
                return {
                    "success": True,
                    "question": question,
                    "answer": "No relevant information found in the database.",
                    "politicians": [],
                    "total_results": 0,
                }

            politicians_info = []
            for r in results:
                meta = r.get("metadata", {})
                politicians_info.append(
                    {
                        "id": r.get("id", ""),
                        "name": meta.get("name", "Unknown"),
                        "type": meta.get("type", ""),
                        "state": meta.get("state", ""),
                        "constituency": meta.get("constituency", ""),
                        "party": meta.get("party", ""),
                        "relevance": (
                            round(1 - r.get("distance", 0), 3)
                            if r.get("distance") is not None
                            else None
                        ),
                        "snippet": (
                            (r.get("document", "")[:300] + "...")
                            if r.get("document")
                            else ""
                        ),
                    }
                )

            answer = self._summarize(question, results)

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "politicians": politicians_info,
                "total_results": len(politicians_info),
            }
        except Exception as e:
            logger.error("Error answering question: %s", e)
            return {
                "success": False,
                "question": question,
                "answer": f"Error: {e}",
                "politicians": [],
                "total_results": 0,
            }

    def answer_predefined_question(
        self,
        question_id: str,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Answer a predefined question by its ID."""
        q = next((q for q in PREDEFINED_QUESTIONS if q["id"] == question_id), None)
        if not q:
            return {"success": False, "error": f"Question '{question_id}' not found."}

        result = self.answer_question(q["question"], n_results=n_results)
        result["question_id"] = question_id
        result["category"] = q.get("category")
        return result

    @staticmethod
    def _summarize(question: str, results: List[Dict[str, Any]]) -> str:
        """Generate a brief answer from top results."""
        if not results:
            return "No relevant information found."

        lines = []
        for r in results[:3]:
            meta = r.get("metadata", {})
            name = meta.get("name", "Unknown")
            party = meta.get("party", "")
            state = meta.get("state", "")
            lines.append(f"{name} ({party}, {state})")

        return "Top matches: " + "; ".join(lines) + "."
