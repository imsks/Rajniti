#!/usr/bin/env python3
"""
Enrich candidates.json with detailed fields + sync to ChromaDB.

This is the JSON-first version of the candidate enrichment pipeline:
- No database required
- Writes enriched fields into `app/data/**/<election_id>/candidates.json`
- Upserts each candidate into vector DB immediately (so runtime search never calls LLM)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.json_candidate_agent import JsonCandidateAgent  # noqa: E402


def validate_environment(provider: str) -> bool:
    provider_lower = (provider or "").lower()
    if provider_lower == "perplexity":
        required_vars = ["PERPLEXITY_API_KEY"]
    elif provider_lower == "openai":
        required_vars = ["OPENAI_API_KEY"]
    else:
        logging.error("Unknown provider: %s", provider)
        return False

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(
            "Missing required env vars for %s: %s",
            provider,
            ", ".join(missing_vars),
        )
        return False

    return True


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Enrich candidates.json and sync to vector DB"
    )
    parser.add_argument(
        "--election-id",
        type=str,
        default="lok-sabha-2024",
        help="Election dataset directory name under app/data/** (default: lok-sabha-2024)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["perplexity", "openai"],
        help="LLM provider (default: from LLM_PROVIDER env var or 'openai')",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="How many candidates to enrich per run (default: 10)",
    )
    parser.add_argument(
        "--flush-every",
        type=int,
        default=1,
        help="Write candidates.json after N updated candidates (default: 1)",
    )
    parser.add_argument(
        "--delay-between-candidates",
        type=float,
        default=0.5,
        help="Delay between candidates (default: 0.5s)",
    )
    parser.add_argument(
        "--delay-between-requests",
        type=float,
        default=0.5,
        help="Delay between LLM requests (default: 0.5s)",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Disable in-memory response cache",
    )
    parser.add_argument(
        "--cache-ttl-hours",
        type=int,
        default=24,
        help="Cache TTL (hours) (default: 24)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write candidates.json (still calls LLM unless you stop early)",
    )
    parser.add_argument(
        "--disable-vector-db",
        action="store_true",
        help="Disable vector DB upserts",
    )

    args = parser.parse_args()

    provider = args.provider or os.getenv("LLM_PROVIDER", "openai")
    if not validate_environment(provider):
        sys.exit(1)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "candidate_json_enrichment.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
    )

    logging.info("🚀 JSON Candidate Enrichment")
    logging.info("=" * 60)
    logging.info("Election: %s", args.election_id)
    logging.info("Provider: %s", provider)
    logging.info("Batch size: %s", args.batch_size)
    logging.info("Flush every: %s", args.flush_every)
    logging.info("Dry run: %s", args.dry_run)
    logging.info("Vector DB: %s", "disabled" if args.disable_vector_db else "enabled")
    logging.info("=" * 60)

    agent = JsonCandidateAgent(
        election_id=args.election_id,
        llm_provider=provider,
        enable_cache=not args.disable_cache,
        cache_ttl_hours=args.cache_ttl_hours,
        enable_vector_db=not args.disable_vector_db,
    )

    stats = agent.run(
        batch_size=args.batch_size,
        flush_every=args.flush_every,
        delay_between_candidates=args.delay_between_candidates,
        delay_between_requests=args.delay_between_requests,
        dry_run=args.dry_run,
    )

    logging.info("Done. Stats: %s", stats)


if __name__ == "__main__":
    main()

