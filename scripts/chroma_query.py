import argparse
from pathlib import Path
import sys

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core import setup_logging
from app.core.vector_db import VectorDB


def main(query: str, n: int):
    vdb = VectorDB()
    print("Chroma path:", vdb.db_path.resolve())
    print("Collection:", vdb.collection_name)
    print("Count:", vdb.count())

    res = vdb.query(query_text=query, n_results=n)

    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    for i, pid in enumerate(ids):
        print("\n---")
        print("rank:", i + 1)
        print("id:", pid)
        print("distance:", dists[i] if i < len(dists) else None)
        print("meta:", metas[i] if i < len(metas) else None)
        snippet = (docs[i] if i < len(docs) else "")[:400]
        print("doc:", snippet)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--q", required=True, help="query text")
    p.add_argument("--n", type=int, default=5, help="top N results")
    p.add_argument("--log-level", default="ERROR", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = p.parse_args()

    setup_logging(args.log_level)
    main(query=args.q, n=args.n)

