#!/usr/bin/env python3
"""
Sync mp.json & mla.json → ChromaDB.

Rebuilds the vector database from scratch (or incrementally).
Each Politician becomes one searchable document.

Usage:
    # Full rebuild (wipe + re-insert all)
    python scripts/sync_vector_db.py --reset

    # Incremental (upsert only — safe to run repeatedly)
    python scripts/sync_vector_db.py

    # Only sync MPs
    python scripts/sync_vector_db.py --type MP
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.politician_service import PoliticianService
from app.services.vector_db_service import VectorDBService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync politicians from JSON → ChromaDB"
    )
    parser.add_argument(
        "--type",
        choices=["MP", "MLA"],
        default=None,
        help="Only sync this type (default: both)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe the collection before syncing",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(name)-30s  %(levelname)-7s  %(message)s",
    )
    logger = logging.getLogger("sync_vector_db")

    pol_service = PoliticianService()
    vdb = VectorDBService()

    if args.reset:
        logger.warning("Resetting collection — all documents will be deleted")
        vdb.reset()

    types = [args.type] if args.type else ["MP", "MLA"]
    total = 0

    for etype in types:
        politicians = pol_service.get_all(etype)  # type: ignore[arg-type]
        if not politicians:
            logger.info("No %ss found — skipping", etype)
            continue

        logger.info("Syncing %d %ss...", len(politicians), etype)
        count = vdb.upsert_batch(politicians)
        total += count
        logger.info("  ✓ Upserted %d %ss", count, etype)

    logger.info("=" * 50)
    logger.info("✅ Done! Total documents in ChromaDB: %d", vdb.count())


if __name__ == "__main__":
    main()
