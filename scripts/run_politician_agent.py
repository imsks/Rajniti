import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.politician_agent import PoliticianAgent
from app.core import setup_logging

# To run script -> python scripts/run_politician_agent.py --id "e345d97b-f7c3-4974-b190-1662fcfb4a7a"


def main() -> None:
    """Parse CLI args and execute the requested politician agent action."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", help="Run only for a single Politician ID")
    parser.add_argument(
        "--type", choices=["MP", "MLA"], help="Run only for one election type"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit politicians processed (0 = no limit)",
    )
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--source",
        action="append",
        help="External source to sync before enrichment (repeatable), e.g. myneta",
    )
    parser.add_argument(
        "--skip-sources",
        action="store_true",
        help="Skip browser source sync (default runs myneta)",
    )
    parser.add_argument(
        "--skip-citations",
        action="store_true",
        help="Skip citation backfill after LLM enrichment (on by default)",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    agent = PoliticianAgent()
    result = agent.run(
        politician_id=args.id,
        election_type=args.type,
        force=args.force,
        limit=args.limit,
        source_names=args.source,
        skip_sources=args.skip_sources,
        skip_citations=args.skip_citations,
    )

    print(result)


if __name__ == "__main__":
    main()
