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
    parser.add_argument("--type", choices=["MP", "MLA"], help="Run only for one election type")
    parser.add_argument("--limit", type=int, default=0, help="Limit politicians processed (0 = no limit)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    setup_logging(args.log_level)

    agent = PoliticianAgent()
    result = agent.run(politician_id=args.id, election_type=args.type, force=args.force, limit=args.limit)

    print(result)


if __name__ == "__main__":
    main()