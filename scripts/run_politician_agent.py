import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.politician_agent import PoliticianAgent


def main() -> None:
    """Parse CLI args and execute the requested politician agent action."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Politician ID")
    parser.add_argument("--field", default="education", choices=["education"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    agent = PoliticianAgent()

    if args.field == "education":
        result = agent.enrich_education(args.id, force=args.force)
    else:
        result = {"ok": False, "error": "unsupported_field"}

    print(result)


if __name__ == "__main__":
    main()