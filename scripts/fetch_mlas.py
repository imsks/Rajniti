import argparse
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.state_mla_fetcher import StateMLAFetcher
from app.core import setup_logging


def main(state: "str" = None, force: bool = False, log_level: str = "DEBUG"):
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    fetcher = StateMLAFetcher()

    if state:
        result = fetcher.run(state=state, force=force)
    else:
        logger.info("No --state passed, running for all states")
        result = fetcher.run_all(force=force)

    logger.info("Result: %s", result)
    print(result)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Fetch MLAs and append to mla.json")
    p.add_argument("--state", default=None, help="State name (omit to run all states)")
    p.add_argument("--force", action="store_true", help="Ignore cache/duplicates and overwrite")
    p.add_argument("--log-level", default="DEBUG", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = p.parse_args()
    main(state=args.state, force=args.force, log_level=args.log_level)
