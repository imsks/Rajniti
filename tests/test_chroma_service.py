"""
Tests for ChromaDB Service

Tests the basic functionality of the ChromaDB service including
initialization, connection, collection management, and health checks.
"""

import os
import shutil
from pathlib import Path

import pytest

from app.services import ChromaService


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path for testing"""
    db_path = tmp_path / "test_chroma_db"
    yield str(db_path)
    # Cleanup after test
    if db_path.exists():
        shutil.rmtree(db_path, ignore_errors=True)


@pytest.fixture
def chroma_service(test_db_path):
    """Create a ChromaService instance for testing"""
    service = ChromaService(
        db_path=test_db_path,
        collection_name="test_collection",
    )
    yield service
    # Cleanup
    service.close()


class TestChromaServiceInitialization:
    """Test ChromaDB service initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default values"""
        service = ChromaService()
        assert service.db_path == os.getenv("CHROMA_DB_PATH", "./chroma_db")
        assert service.collection_name == os.getenv(
            "CHROMA_COLLECTION_NAME", "rajniti_embeddings"
        )

    def test_init_with_custom_values(self, test_db_path):
        """Test initialization with custom values"""
        service = ChromaService(
            db_path=test_db_path,
            collection_name="custom_collection",
        )
        assert service.db_path == test_db_path
        assert service.collection_name == "custom_collection"

    def test_init_with_env_vars(self, test_db_path, monkeypatch):
        """Test initialization with environment variables"""
        monkeypatch.setenv("CHROMA_DB_PATH", test_db_path)
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "env_collection")

        service = ChromaService()
        assert service.db_path == test_db_path
        assert service.collection_name == "env_collection"


class TestChromaServiceClient:
    """Test ChromaDB client operations"""

    def test_get_client(self, chroma_service, test_db_path):
        """Test getting ChromaDB client"""
        client = chroma_service.get_client()
        assert client is not None
        # Verify database path was created
        assert Path(test_db_path).exists()

    def test_get_client_singleton(self, chroma_service):
        """Test that get_client returns the same instance"""
        client1 = chroma_service.get_client()
        client2 = chroma_service.get_client()
        assert client1 is client2

    def test_ensure_db_path_creates_directory(self, test_db_path):
        """Test that database directory is created"""
        service = ChromaService(db_path=test_db_path)
        assert not Path(test_db_path).exists()

        service._ensure_db_path()
        assert Path(test_db_path).exists()


class TestChromaServiceCollection:
    """Test ChromaDB collection operations"""

    def test_get_collection_default(self, chroma_service):
        """Test getting default collection"""
        collection = chroma_service.get_collection()
        assert collection is not None
        assert collection.name == "test_collection"

    def test_get_collection_custom_name(self, chroma_service):
        """Test getting collection with custom name"""
        collection = chroma_service.get_collection(name="another_collection")
        assert collection is not None
        assert collection.name == "another_collection"

    def test_get_collection_creates_if_not_exists(self, chroma_service):
        """Test that collection is created if it doesn't exist"""
        collection_name = "new_collection"
        collection = chroma_service.get_collection(name=collection_name)
        assert collection is not None
        assert collection.name == collection_name

    def test_get_collection_metadata(self, chroma_service):
        """Test that collection has proper metadata"""
        collection = chroma_service.get_collection()
        metadata = collection.metadata
        assert metadata is not None
        assert "description" in metadata
        assert "Rajniti" in metadata["description"]


class TestChromaServiceHealthCheck:
    """Test health check functionality"""

    def test_health_check_healthy(self, chroma_service):
        """Test health check on healthy service"""
        # Initialize the client first
        chroma_service.get_client()

        health = chroma_service.health_check()
        assert health["status"] == "healthy"
        assert "db_path" in health
        assert "collections" in health
        assert "default_collection" in health
        assert isinstance(health["collections"], list)

    def test_health_check_with_collections(self, chroma_service):
        """Test health check includes collection information"""
        # Create a collection
        chroma_service.get_collection()

        health = chroma_service.health_check()
        assert health["status"] == "healthy"
        assert len(health["collections"]) > 0
        assert "test_collection" in health["collections"]

    def test_health_check_includes_db_path(self, chroma_service, test_db_path):
        """Test health check includes database path"""
        health = chroma_service.health_check()
        assert health["db_path"] == test_db_path


class TestChromaServiceReset:
    """Test reset functionality"""

    def test_reset_clears_client(self, chroma_service):
        """Test that reset clears the client"""
        # Initialize client
        chroma_service.get_client()
        assert chroma_service._client is not None

        # Reset
        result = chroma_service.reset()
        assert result is True
        assert chroma_service._client is None

    def test_reset_clears_collections(self, chroma_service):
        """Test that reset clears collections"""
        # Create a collection
        chroma_service.get_collection()

        # Reset
        chroma_service.reset()

        # Verify collections are cleared
        client = chroma_service.get_client()
        collections = client.list_collections()
        assert len(collections) == 0


class TestChromaServiceClose:
    """Test close functionality"""

    def test_close_clears_references(self, chroma_service):
        """Test that close clears internal references"""
        # Initialize client and collection
        chroma_service.get_client()
        chroma_service.get_collection()

        # Close
        chroma_service.close()

        assert chroma_service._client is None
        assert chroma_service._collection is None

    def test_close_is_safe_when_not_initialized(self, chroma_service):
        """Test that close is safe even if service not initialized"""
        # Should not raise any errors
        chroma_service.close()
        assert chroma_service._client is None


class TestChromaServiceIntegration:
    """Integration tests for ChromaDB service"""

    def test_full_lifecycle(self, test_db_path):
        """Test complete lifecycle of ChromaDB service"""
        # 1. Initialize
        service = ChromaService(
            db_path=test_db_path,
            collection_name="lifecycle_test",
        )

        # 2. Get client
        client = service.get_client()
        assert client is not None

        # 3. Create collection
        collection = service.get_collection()
        assert collection.name == "lifecycle_test"

        # 4. Health check
        health = service.health_check()
        assert health["status"] == "healthy"
        assert "lifecycle_test" in health["collections"]

        # 5. Close
        service.close()
        assert service._client is None

    def test_multiple_collections(self, chroma_service):
        """Test creating and managing multiple collections"""
        # Create multiple collections
        col1 = chroma_service.get_collection(name="collection_1")
        col2 = chroma_service.get_collection(name="collection_2")
        col3 = chroma_service.get_collection(name="collection_3")

        assert col1.name == "collection_1"
        assert col2.name == "collection_2"
        assert col3.name == "collection_3"

        # Verify all collections exist
        health = chroma_service.health_check()
        assert len(health["collections"]) >= 3
        assert "collection_1" in health["collections"]
        assert "collection_2" in health["collections"]
        assert "collection_3" in health["collections"]
