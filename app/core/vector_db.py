import os
from pathlib import Path
import chromadb

CHROMA_PATH = Path(os.getenv("CHROMA_DB_PATH", "vector_db"))
COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "politicians")

CHROMA_PATH.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection(name=COLLECTION)

print("Chroma path:", CHROMA_PATH.resolve())
print("Collection ready:", collection.name)