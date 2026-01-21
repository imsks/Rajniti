#!/usr/bin/env python3
"""
Sync candidates from JSON datasets to ChromaDB.

No database required. This is the recommended "first step" before you switch
user search to vector-only, so every candidate has a document in Chroma.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.vector_db_pipeline import VectorDBPipeline  # noqa: E402


def resolve_election_dir(base_data_dir: Path, election_id: str) -> Path:
    for candidates_file in base_data_dir.rglob("candidates.json"):
        if candidates_file.parent.name == election_id:
            return candidates_file.parent
    raise FileNotFoundError(f"Could not find dataset for election_id={election_id}")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Sync JSON candidates to ChromaDB")
    parser.add_argument(
        "--election-id",
        type=str,
        default="lok-sabha-2024",
        help="Election dataset directory name (default: lok-sabha-2024)",
    )
    parser.add_argument(
        "--winners-only",
        action="store_true",
        help="Sync only winning candidates",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of candidates synced (for testing)",
    )

    args = parser.parse_args()

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "vector_db_sync_json.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
    )

    base_data_dir = Path(__file__).resolve().parents[1] / "app" / "data"
    election_dir = resolve_election_dir(base_data_dir, args.election_id)
    candidates_path = election_dir / "candidates.json"

    with candidates_path.open("r", encoding="utf-8") as f:
        candidates = json.load(f)
    if not isinstance(candidates, list):
        raise ValueError("candidates.json must be a JSON array")

    if args.winners_only:
        candidates = [c for c in candidates if c.get("status") == "WON"]

    if args.limit is not None:
        candidates = candidates[: max(0, args.limit)]

    pipeline = VectorDBPipeline()

    total = len(candidates)
    synced = 0
    failed = 0
    for i, cand in enumerate(candidates, 1):
        ok = pipeline.sync_candidate_dict(cand)
        if ok:
            synced += 1
        else:
            failed += 1
        if i % 100 == 0 or i == total:
            logging.info("Progress: %s/%s (synced=%s failed=%s)", i, total, synced, failed)

    logging.info("Done. total=%s synced=%s failed=%s", total, synced, failed)


if __name__ == "__main__":
    main()

