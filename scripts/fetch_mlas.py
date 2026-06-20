from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.agents.state_mla_fetcher import StateMLAFetcher
from app.core import setup_logging

# Many LLM calls for large states; default 15s per request is too low (504 / truncation).
os.environ.setdefault("FREE_TIER_LLM_TIMEOUT_SECS", "180")


def main(
    state: str | None = None,
    force: bool = False,
    dry_run: bool = False,
    log_level: str = "DEBUG",
):
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    fetcher = StateMLAFetcher()

    if state:
        result = fetcher.run(state=state, force=force, dry_run=dry_run)
    else:
        logger.info("No --state passed, running for all states")
        if dry_run:
            # Dry run for all states
            results = []
            for s in fetcher.states:
                results.append(fetcher.run(state=s, force=force, dry_run=True))
            result = {"states": len(results), "dry_run": True}
        else:
            result = fetcher.run_all(force=force)

    logger.info("Result: %s", result)
    print(result)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description=(
            "Fetch MLAs via LLM (deprecated — prefer scrape_election.py + scrape_politician_sources.py)"
        )
    )
    p.add_argument("--state", default=None, help="State name (omit to run all states)")
    p.add_argument(
        "--force", action="store_true", help="Ignore cache/duplicates and overwrite"
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Report gaps without making LLM calls",
    )
    p.add_argument(
        "--log-level", default="DEBUG", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    args = p.parse_args()
    main(state=args.state, force=args.force, dry_run=args.dry_run, log_level=args.log_level)
