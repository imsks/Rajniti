#!/usr/bin/env python3
"""
Enrich politicians by fetching missing fields via LLM.

Updates mp.json / mla.json in-place with enriched data.

Usage:
    # Enrich 10 MPs that have missing fields
    python scripts/enrich_politicians.py --type MP --batch-size 10

    # Dry run — just list who needs enrichment
    python scripts/enrich_politicians.py --dry-run

    # Enrich all types, 5 at a time
    python scripts/enrich_politicians.py --batch-size 5
"""

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich politicians via LLM"
    )
    parser.add_argument(
        "--type",
        choices=["MP", "MLA"],
        default=None,
        help="Only enrich this type (default: both)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="How many politicians to process (default: 10)",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "perplexity"],
        default=None,
        help="LLM provider (default: from LLM_PROVIDER env var)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between LLM calls in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list politicians needing enrichment — no LLM calls",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Disable LLM response cache",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(name)-30s  %(levelname)-7s  %(message)s",
    )
    logger = logging.getLogger("enrich_politicians")

    from app.services.enrichment_agent import EnrichmentAgent

    agent = EnrichmentAgent(
        llm_provider=args.provider or os.getenv("LLM_PROVIDER"),
        enable_cache=not args.disable_cache,
    )

    if args.dry_run:
        logger.info("DRY RUN — listing politicians that need enrichment:")
        candidates = agent.find_politicians_needing_enrichment(
            election_type=args.type, limit=args.batch_size
        )
        for i, p in enumerate(candidates, 1):
            missing = agent.find_missing_fields(p)
            logger.info(
                "  %d. %s (%s) — missing: %s",
                i, p.get("name"), p.get("id"), ", ".join(missing),
            )
        logger.info("Total: %d", len(candidates))
        return

    stats = agent.run(
        election_type=args.type,
        batch_size=args.batch_size,
        delay=args.delay,
    )

    logger.info("=" * 50)
    logger.info("✅ Enrichment complete: %s", stats)


if __name__ == "__main__":
    main()
