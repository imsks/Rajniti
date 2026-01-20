#!/usr/bin/env python3
"""
CLI script to sync candidate data from JSON files to ChromaDB vector database.

This script syncs candidate information from JSON files (not database)
to ChromaDB for semantic search capabilities.

Usage:
    # Full sync for an election
    python scripts/sync_candidates_to_vector_db.py --election-id lok-sabha-2024

    # Sync with batch size
    python scripts/sync_candidates_to_vector_db.py --election-id lok-sabha-2024 --batch-size 50

    # Sync only winners
    python scripts/sync_candidates_to_vector_db.py --election-id lok-sabha-2024 --winners-only

    # Sync specific state
    python scripts/sync_candidates_to_vector_db.py --election-id lok-sabha-2024 --state DL

Environment Variables:
    CHROMA_DB_PATH: Path to ChromaDB storage (optional, defaults to chroma_db)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.services.vector_db_pipeline import VectorDBPipeline

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "vector_db_sync.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
)
logger = logging.getLogger(__name__)


def main():
    """Main function to sync candidates to vector database."""
    parser = argparse.ArgumentParser(
        description="Sync candidate data from JSON to ChromaDB vector database"
    )
    parser.add_argument(
        "--election-id",
        type=str,
        required=True,
        help="Election ID to sync (e.g., lok-sabha-2024)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of candidates to process in one batch (default: 100)",
    )
    parser.add_argument(
        "--winners-only",
        action="store_true",
        help="Sync only winning candidates",
    )
    parser.add_argument(
        "--state",
        type=str,
        help="Sync only candidates from specific state (e.g., DL, MH)",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["MP", "MLA"],
        help="Sync only specific candidate type (MP or MLA)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (show what would be synced without syncing)",
    )

    args = parser.parse_args()

    logger.info("🚀 Candidate to Vector DB Sync (JSON-based)")
    logger.info("=" * 60)
    logger.info(f"Election ID: {args.election_id}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Winners only: {args.winners_only}")
    logger.info(f"State filter: {args.state or 'All'}")
    logger.info(f"Type filter: {args.type or 'All'}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"ChromaDB path: {os.getenv('CHROMA_DB_PATH', 'chroma_db')}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("💡 Data Source: JSON files (no database required)")
    logger.info("")

    try:
        # Initialize pipeline
        pipeline = VectorDBPipeline()

        # Build filter criteria
        filter_criteria = {}
        if args.winners_only:
            filter_criteria["status"] = "WON"
        if args.state:
            filter_criteria["state_id"] = args.state
        if args.type:
            filter_criteria["type"] = args.type

        if args.dry_run:
            logger.info("DRY RUN MODE - No data will be synced")
            logger.info("")

            # Count candidates that would be synced
            candidates = pipeline._load_candidates(args.election_id)

            if filter_criteria.get("status"):
                candidates = [c for c in candidates if c.get("status") == filter_criteria["status"]]
            if filter_criteria.get("state_id"):
                candidates = [c for c in candidates if c.get("state_id") == filter_criteria["state_id"]]
            if filter_criteria.get("type"):
                candidates = [c for c in candidates if c.get("type") == filter_criteria["type"]]

            logger.info(f"Would sync {len(candidates)} candidates based on filters")
            logger.info("")

            # Show sample candidates
            for i, candidate in enumerate(candidates[:5]):
                logger.info(f"  {i+1}. {candidate.get('name')} ({candidate.get('party_id')}) - {candidate.get('status')}")
            if len(candidates) > 5:
                logger.info(f"  ... and {len(candidates) - 5} more")
        else:
            stats = pipeline.sync_all_candidates(
                election_id=args.election_id,
                batch_size=args.batch_size,
                filter_criteria=filter_criteria if filter_criteria else None,
            )

            logger.info("")
            logger.info("✅ Sync completed successfully")
            logger.info("=" * 60)
            logger.info(f"Total candidates processed: {stats['total']}")
            logger.info(f"Successfully synced: {stats['synced']}")
            logger.info(f"Failed: {stats['failed']}")
            logger.info(f"Batches: {stats['batches']}")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Vector database is now ready for semantic search!")

            # Show current vector DB stats
            try:
                total_in_db = pipeline.vector_db.count_candidates()
                logger.info(f"Total candidates in vector database: {total_in_db}")
            except Exception:
                pass

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Sync interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n❌ Sync failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
