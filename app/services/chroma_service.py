"""
ChromaDB Service for Vector Database Operations

This service provides a simple interface for interacting with ChromaDB.
Currently provides basic setup and connection management.
Schema implementation will be added later.
"""

import os
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings


class ChromaService:
    """ChromaDB service for vector database operations"""

    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """
        Initialize ChromaDB service.

        Args:
            db_path: Path to ChromaDB storage directory. Defaults to env var or './chroma_db'
            collection_name: Name of the collection. Defaults to env var or 'rajniti_embeddings'
        """
        self.db_path = db_path or os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "rajniti_embeddings"
        )
        self._client = None
        self._collection = None

    def _ensure_db_path(self) -> None:
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path)
        db_dir.mkdir(parents=True, exist_ok=True)

    def get_client(self) -> chromadb.Client:
        """
        Get or create ChromaDB client.

        Returns:
            ChromaDB client instance
        """
        if self._client is None:
            self._ensure_db_path()
            self._client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
        return self._client

    def get_collection(self, name: Optional[str] = None) -> chromadb.Collection:
        """
        Get or create a collection.

        Args:
            name: Collection name. If None, uses the default collection name.

        Returns:
            ChromaDB collection instance
        """
        collection_name = name or self.collection_name
        client = self.get_client()

        # Get or create collection
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            # Collection doesn't exist, create it
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Rajniti election data embeddings"},
            )

        return collection

    def health_check(self) -> dict:
        """
        Perform a health check on the ChromaDB service.

        Returns:
            Dict with health status and metadata
        """
        try:
            client = self.get_client()
            collections = client.list_collections()

            return {
                "status": "healthy",
                "db_path": self.db_path,
                "collections": [col.name for col in collections],
                "default_collection": self.collection_name,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "db_path": self.db_path,
            }

    def reset(self) -> bool:
        """
        Reset the ChromaDB client (useful for testing).
        WARNING: This will delete all data!

        Returns:
            True if reset successful, False otherwise
        """
        try:
            if self._client:
                self._client.reset()
                self._client = None
                self._collection = None
            return True
        except Exception as e:
            print(f"Error resetting ChromaDB: {e}")
            return False

    def close(self) -> None:
        """Close the ChromaDB client connection"""
        if self._client:
            # ChromaDB doesn't require explicit closing, but we clear references
            self._client = None
            self._collection = None
