import os
from pathlib import Path
from typing import Optional

import chromadb
from dotenv import load_dotenv
from fastembed import TextEmbedding

load_dotenv()


class VectorDB:
    """ChromaDB wrapper (local persistent) for politician embeddings."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.db_path = Path(db_path or os.getenv("CHROMA_DB_PATH", "chroma_db"))
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "rajniti_politicians"
        )

        self.db_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        self.embedder = TextEmbedding()

    def health(self) -> bool:
        """Return True if the collection is reachable."""
        try:
            _ = self.collection.count()
            return True
        except Exception:
            return False

    def count(self) -> int:
        """Return number of records in the collection."""
        return int(self.collection.count())

    def get(self, ids=None, where=None, limit: int = 20):
        """Fetch records by ids or metadata filter."""
        kwargs = {"limit": limit}
        if ids is not None:
            kwargs["ids"] = ids
        if where is not None:
            kwargs["where"] = where
        return self.collection.get(**kwargs)

    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
        embeddings: Optional[list[list[float]]] = None,
    ) -> None:
        """Upsert records into the collection."""
        if not (len(ids) == len(documents) == len(metadatas)):
            raise ValueError("ids, documents, metadatas must have the same length")

        kwargs = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }
        if embeddings is not None:
            kwargs["embeddings"] = embeddings

        self.collection.upsert(**kwargs)

    def delete(self, *, ids: list[str]) -> None:
        """Delete records by ids."""
        self.collection.delete(ids=ids)

    def reset_collection(self) -> None:
        """Drop and recreate the collection (useful for weekly rebuild)."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Create local embeddings for a list of texts."""
        return [v.tolist() for v in self.embedder.embed(texts)]

    def query(
        self, *, query_text: str, n_results: int = 5, where: Optional[dict] = None
    ):
        """Semantic search over politician documents."""
        qvec = self.embed_texts([query_text])[0]
        kwargs = {"query_embeddings": [qvec], "n_results": n_results}
        if where is not None:
            kwargs["where"] = where
        return self.collection.query(**kwargs)


# If called as a script, run the main function
if __name__ == "__main__":
    vdb = VectorDB()
    print("Chroma path:", vdb.db_path.resolve())
    print("Collection ready:", vdb.collection.name)
    print("Health:", vdb.health())
    print("Count:", vdb.count())
    print("Get:", vdb.get())

    print(vdb.query(query_text="education of Modi", n_results=3))
