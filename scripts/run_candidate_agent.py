#!/usr/bin/env python3
"""
CLI script to run the Candidate Data Population Agent.

This script:
- Reads candidates from JSON files
- Fetches detailed information using LLM (Perplexity, OpenAI)
- Writes enriched data back to JSON files
- Syncs to ChromaDB for vector search

Usage:
    python3 scripts/run_candidate_agent.py --election-id lok-sabha-2024 [--provider openai] [--batch-size 10]

Environment Variables:
    LLM_PROVIDER: LLM provider ('perplexity', 'openai')
    PERPLEXITY_API_KEY: Perplexity API key (if using perplexity)
    OPENAI_API_KEY: OpenAI API key (if using openai)
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.services.candidate_agent import CandidateAgent

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "candidate_agent.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
)
logger = logging.getLogger(__name__)


def validate_environment(provider: str):
    """Validate required environment variables are set."""
    provider_lower = provider.lower()

    if provider_lower == "perplexity":
        required_vars = ["PERPLEXITY_API_KEY"]
    elif provider_lower == "openai":
        required_vars = ["OPENAI_API_KEY"]
    else:
        logger.error(f"Unknown provider: {provider}")
        return False

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables for {provider}: {', '.join(missing_vars)}"
        )
        logger.error("Please set them in your .env file or environment")
        return False

    return True


class MockLLMService:
    """
    Deterministic offline LLM service used by --mock-llm.

    This is intentionally simple: it returns valid JSON in the expected shape
    so you can observe the agent pipeline (JSON extraction + Pydantic validation
    + candidate dict updates) without any external API keys.
    """

    def search_india(self, query: str, region=None, city=None):  # noqa: ANN001
        # Minimal, schema-valid payload (types matter; content is placeholder).
        return {
            "answer": (
                '{'
                '"education":[{"year":"2000","college":"Demo University","stream":"Arts","other_details":"N/A"}],'
                '"political":[{"party":"Demo Party","constituency":"Demo Constituency","election_year":"2019","position":"MP","result":"LOST"}],'
                '"family":[{"name":"Demo Relative","profession":"Service","relation":"Father","age":"60"}],'
                '"assets":[{"type":"CASH","amount":1000.0,"description":"Demo","owned_by":"SELF"}],'
                '"liabilities":[{"type":"LOAN","amount":500.0,"description":"Demo","owned_by":"SELF"}],'
                '"crime_cases":[{"fir_no":"0","police_station":"Demo PS","sections_applied":["IPC 420"],"charges_framed":false,"description":"Demo"}]'
                '}'
            ),
            "error": None,
        }


def main():
    """Main function to run the candidate data population agent."""
    parser = argparse.ArgumentParser(
        description="Run the Candidate Data Population Agent"
    )
    parser.add_argument(
        "--election-id",
        type=str,
        default="lok-sabha-2024",
        help="Election ID to process (default: lok-sabha-2024)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["perplexity", "openai"],
        help="LLM provider to use (default: from LLM_PROVIDER env var or 'perplexity')",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of candidates to process in one run (default: 10)",
    )
    parser.add_argument(
        "--delay-between-candidates",
        type=float,
        default=2.0,
        help="Delay in seconds between processing candidates (default: 2.0)",
    )
    parser.add_argument(
        "--delay-between-requests",
        type=float,
        default=1.0,
        help="Delay in seconds between API requests (default: 1.0)",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Disable response caching",
    )
    parser.add_argument(
        "--cache-ttl-hours",
        type=int,
        default=24,
        help="Cache TTL in hours (default: 24)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List candidates needing data (no LLM calls, no file updates)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Process candidates but do not write JSON files (LLM calls may occur)",
    )
    parser.add_argument(
        "--disable-vector-db",
        action="store_true",
        help="Disable automatic sync to vector database",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use a deterministic offline mock LLM (no API keys required)",
    )

    args = parser.parse_args()

    # Determine provider
    provider = args.provider or os.getenv("LLM_PROVIDER", "perplexity")

    # Validate environment (skip for dry-run/list mode or mocked LLM runs)
    if not args.dry_run and not args.mock_llm:
        if not validate_environment(provider):
            sys.exit(1)

    logger.info("🚀 Candidate Data Population Agent")
    logger.info("=" * 60)
    logger.info(f"Election ID: {args.election_id}")
    logger.info(f"Provider: {provider}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Delay between candidates: {args.delay_between_candidates}s")
    logger.info(f"Delay between requests: {args.delay_between_requests}s")
    logger.info(f"Caching: {'Disabled' if args.disable_cache else f'Enabled (TTL: {args.cache_ttl_hours}h)'}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Preview: {args.preview}")
    logger.info(f"Vector DB sync: {'Disabled' if args.disable_vector_db else 'Enabled'}")
    logger.info(f"Mock LLM: {args.mock_llm}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("💡 Data Source: JSON files (no database required)")
    logger.info("💡 Output: JSON files + ChromaDB (if enabled)")
    logger.info("")

    try:
        # Preview/dry-run should not mutate vector db by default
        effective_enable_vector_db = not args.disable_vector_db and not (
            args.dry_run or args.preview
        )

        injected_search = MockLLMService() if args.mock_llm else None

        # Initialize agent
        agent = CandidateAgent(
            llm_provider=provider,
            enable_cache=not args.disable_cache,
            cache_ttl_hours=args.cache_ttl_hours,
            enable_vector_db=effective_enable_vector_db,
            search_service=injected_search,
        )

        if args.dry_run:
            logger.info("DRY RUN MODE - No file updates will be made")
            logger.info("")
            candidates = agent.find_candidates_needing_data(
                args.election_id, limit=args.batch_size
            )
            logger.info(f"Found {len(candidates)} candidates needing data:")
            for idx, candidate in enumerate(candidates, 1):
                logger.info(f"{idx}. {candidate['name']} (ID: {candidate['id']})")
            logger.info("")
        elif args.preview:
            logger.info("PREVIEW MODE - No file updates will be made")
            logger.info("")
            candidates = agent.find_candidates_needing_data(
                args.election_id, limit=args.batch_size
            )
            if not candidates:
                logger.info("✅ No candidates found needing data population")
                return

            for idx, candidate in enumerate(candidates, 1):
                logger.info(f"\nPreviewing {idx}/{len(candidates)}")
                # Work on a copy so we never mutate loaded structures in preview mode
                candidate_copy = json.loads(json.dumps(candidate))
                agent.populate_candidate_data(
                    candidate_copy,
                    args.election_id,
                    delay_between_requests=args.delay_between_requests,
                )
        else:
            stats = agent.run(
                election_id=args.election_id,
                batch_size=args.batch_size,
                delay_between_candidates=args.delay_between_candidates,
                delay_between_requests=args.delay_between_requests,
            )

            logger.info("✅ Agent run completed successfully")
            logger.info("")
            logger.info("💡 Cost Savings:")
            logger.info(
                f"   - Traditional agent: {stats['total_processed'] * 6} API calls"
            )
            logger.info(
                f"   - Optimized agent: ~{stats['total_processed']} API calls"
            )
            if stats['total_processed'] > 0:
                savings = stats['total_processed'] * 5 / (stats['total_processed'] * 6) * 100
                logger.info(
                    f"   - Savings: ~{stats['total_processed'] * 5} API calls ({savings:.1f}% reduction)"
                )
            logger.info("")
            logger.info("To process more candidates, run this script again.")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Agent interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n❌ Agent failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
