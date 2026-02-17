import argparse
import logging
from pathlib import Path
import sys

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.state_mla_fetcher import StateMLAFetcher
from app.core import setup_logging

def main(state: str, force: bool, log_level: str):
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    fetcher = StateMLAFetcher()
    result = fetcher.run(state=state, force=force)
    logger.info("Result: %s", result)
    print(result)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Fetch MLAs for a state and append to mla.json")
    p.add_argument("--state", required=True, help="State name (must exist in states.json)")
    p.add_argument("--force", action="store_true", help="Ignore cache/duplicates and overwrite")
    p.add_argument("--log-level", default="DEBUG", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = p.parse_args()
    main(state=args.state, force=args.force, log_level=args.log_level)

