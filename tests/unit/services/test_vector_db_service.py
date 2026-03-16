"""
Unit tests for VectorDBService.

Tests cover the service-layer wrapper around VectorDB, including
result normalisation, count delegation, and graceful error handling.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb and fastembed before any imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()
sys.modules["fastembed"] = MagicMock()

from app.services.vector_db_service import VectorDBService  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_vdb():
    """Return a Mock that stands in for app.core.vector_db.VectorDB."""
    vdb = Mock()
    vdb.collection_name = "rajniti_politicians"
    vdb.count.return_value = 42
    return vdb


@pytest.fixture
def service(mock_vdb):
    """VectorDBService instance with an injected mock VectorDB."""
    with patch("app.services.vector_db_service.VectorDBService.__init__") as init:
        init.return_value = None
        svc = VectorDBService.__new__(VectorDBService)
        svc._vdb = mock_vdb
        return svc


# ---------------------------------------------------------------------------
# count()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVectorDBServiceCount:
    def test_count_returns_value_from_vdb(self, service, mock_vdb):
        """count() should delegate to the underlying VectorDB."""
        assert service.count() == 42
        mock_vdb.count.assert_called_once()

    def test_count_returns_zero_when_empty(self, service, mock_vdb):
        mock_vdb.count.return_value = 0
        assert service.count() == 0


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVectorDBServiceSearch:
    """Tests for VectorDBService.search()."""

    def _make_raw(self, n: int = 2):
        """Build a fake ChromaDB query result with ``n`` items."""
        ids = [f"id-{i}" for i in range(n)]
        docs = [f"Document {i}" for i in range(n)]
        metas = [{"name": f"Politician {i}", "state": "DL"} for i in range(n)]
        dists = [0.1 * i for i in range(n)]
        return {
            "ids": [ids],
            "documents": [docs],
            "metadatas": [metas],
            "distances": [dists],
        }

    def test_search_returns_normalised_list(self, service, mock_vdb):
        """search() should return a flat list of result dicts."""
        mock_vdb.query.return_value = self._make_raw(2)

        results = service.search("test query", n_results=2)

        assert len(results) == 2
        first = results[0]
        assert first["id"] == "id-0"
        assert first["document"] == "Document 0"
        assert first["metadata"] == {"name": "Politician 0", "state": "DL"}
        assert first["distance"] == pytest.approx(0.0)

    def test_search_passes_query_and_n_results(self, service, mock_vdb):
        """search() must forward query text and n_results to VectorDB."""
        mock_vdb.query.return_value = self._make_raw(0)

        service.search("criminal records", n_results=10)

        mock_vdb.query.assert_called_once_with(
            query_text="criminal records", n_results=10, where=None
        )

    def test_search_passes_where_filter(self, service, mock_vdb):
        """search() must forward the optional where filter to VectorDB."""
        mock_vdb.query.return_value = self._make_raw(0)
        where = {"state": "Maharashtra"}

        service.search("party", n_results=5, where=where)

        mock_vdb.query.assert_called_once_with(
            query_text="party", n_results=5, where=where
        )

    def test_search_returns_empty_list_on_query_error(self, service, mock_vdb):
        """search() must swallow query exceptions and return []."""
        mock_vdb.query.side_effect = RuntimeError("embedding model error")

        results = service.search("broken query")

        assert results == []

    def test_search_handles_empty_results(self, service, mock_vdb):
        """search() with zero ChromaDB hits returns an empty list."""
        mock_vdb.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        results = service.search("rare query")

        assert results == []

    def test_search_handles_missing_keys_gracefully(self, service, mock_vdb):
        """search() should not crash if ChromaDB omits optional keys."""
        mock_vdb.query.return_value = {
            "ids": [["id-1"]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        results = service.search("partial result")

        assert len(results) == 1
        assert results[0]["id"] == "id-1"
        assert results[0]["document"] == ""
        assert results[0]["distance"] is None
