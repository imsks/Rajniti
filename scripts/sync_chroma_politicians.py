import argparse
import logging
from pathlib import Path
import sys
import time

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.vector_db import VectorDB
from app.core import setup_logging
from app.services.politician_service import PoliticianService

logger = logging.getLogger(__name__)


def politician_to_document(p: dict) -> str:
    parts = [
        f"Name: {p.get('name','')}",
        f"Type: {p.get('type','')}",
        f"State: {p.get('state','')}",
        f"Constituency: {p.get('constituency','')}",
    ]

    bg = p.get("political_background") or {}
    for e in bg.get("elections") or []:
        parts.append(
            f"Election: {e.get('year','')} {e.get('type','')} {e.get('party','')} "
            f"{e.get('constituency','')} {e.get('state','')} {e.get('status','')}"
        )

    for edu in p.get("education") or []:
        parts.append(
            f"Education: {edu.get('qualification','')} "
            f"{edu.get('institution','') or ''} {edu.get('year_completed','') or ''}"
        )

    for cr in p.get("criminal_records") or []:
        parts.append(
            f"Criminal: {cr.get('name','')} {cr.get('type','') or ''} {cr.get('year','') or ''}"
        )

    return ". ".join([x for x in parts if x and x.strip()])


def politician_to_metadata(p: dict) -> dict:
    elections = (p.get("political_background") or {}).get("elections") or []
    party = elections[0].get("party") if elections else ""

    return {
        "type": p.get("type", ""),
        "state": p.get("state", ""),
        "constituency": p.get("constituency", ""),
        "party": party or "",
        "has_education": bool(p.get("education") or []),
        "has_criminal_records": bool(p.get("criminal_records") or []),
    }


def _batched(seq: list, batch_size: int):
    for i in range(0, len(seq), batch_size):
        yield seq[i : i + batch_size]


def main(reset: bool, batch_size: int):
    vdb = VectorDB()
    service = PoliticianService()

    logger.info("Chroma path: %s", vdb.db_path.resolve())
    logger.info("Collection: %s", vdb.collection_name)

    if reset:
        logger.info("Resetting collection: %s", vdb.collection_name)
        vdb.reset_collection()

    politicians = service.get_all_politicians()
    logger.info("Loaded politicians: %d", len(politicians))

    ids, docs, metas = [], [], []
    skipped_no_id = 0
    for p in politicians:
        pid = p.get("id")
        if not pid:
            skipped_no_id += 1
            continue
        ids.append(pid)
        docs.append(politician_to_document(p))
        metas.append(politician_to_metadata(p))

    logger.info("Prepared records: %d (skipped missing id: %d)", len(ids), skipped_no_id)
    before = vdb.count()
    logger.info("Collection count before: %d", before)

    t0 = time.perf_counter()
    total = len(ids)
    upserted = 0

    for b_ids, b_docs, b_metas in zip(
        _batched(ids, batch_size),
        _batched(docs, batch_size),
        _batched(metas, batch_size),
    ):
        t_embed = time.perf_counter()
        embeddings = vdb.embed_texts(b_docs)
        logger.info(
            "Batch embed: %d docs (%.2fs)",
            len(b_ids),
            time.perf_counter() - t_embed,
        )

        t_upsert = time.perf_counter()
        vdb.upsert(ids=b_ids, documents=b_docs, metadatas=b_metas, embeddings=embeddings)
        upserted += len(b_ids)
        logger.info(
            "Batch upsert: %d/%d (%.2fs)",
            upserted,
            total,
            time.perf_counter() - t_upsert,
        )

    after = vdb.count()
    logger.info("Collection count after: %d", after)
    logger.info("Done in %.2fs", time.perf_counter() - t0)
    logger.info("Chroma path: %s", vdb.db_path.resolve())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--reset", action="store_true", help="Drop and recreate the collection before indexing")
    p.add_argument("--batch-size", type=int, default=200, help="Embedding/upsert batch size")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = p.parse_args()
    setup_logging(args.log_level)
    main(reset=args.reset, batch_size=args.batch_size)

