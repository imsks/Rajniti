#!/usr/bin/env python3
"""
Scrape winning MPs / MLAs from ECI election results.

Usage:
    # Defaults — Bihar Vidhan Sabha 2025 (no args needed)
    python scripts/scrape_election.py

    # By election type (uses built-in default URL for MP / MLA)
    python scripts/scrape_election.py --type MLA
    python scripts/scrape_election.py --type MP

    # Custom ECI results page
    python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025
    python scripts/scrape_election.py --url https://results.eci.gov.in/PcResultGenJune2024 --type MP
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.scrapers.defaults import (
    DEFAULT_ELECTION_TYPE,
    DEFAULT_ELECTION_URLS,
    resolve_scrape_target,
)
from app.scrapers.scraper import scrape_election


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape winning MPs / MLAs from ECI and save to mp.json / mla.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Defaults:\n"
            f"  no args     → {DEFAULT_ELECTION_TYPE} @ {DEFAULT_ELECTION_URLS[DEFAULT_ELECTION_TYPE]}\n"
            f"  --type MLA  → {DEFAULT_ELECTION_URLS['MLA']}\n"
            f"  --type MP   → {DEFAULT_ELECTION_URLS['MP']}\n"
        ),
    )
    parser.add_argument(
        "--url",
        default=None,
        help="ECI election results index URL (optional if --type is set)",
    )
    parser.add_argument(
        "--type",
        choices=["MP", "MLA"],
        default=None,
        help="Election type (auto-detected from URL if omitted)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(name)-30s  %(levelname)-7s  %(message)s",
    )
    logger = logging.getLogger("scrape_election")

    try:
        url, election_type = resolve_scrape_target(args.url, args.type)
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    if not args.url and not args.type:
        logger.info("Using default: %s @ %s", election_type, url)
    elif not args.url:
        logger.info("Using default URL for %s: %s", election_type, url)

    logger.info("URL: %s", url)
    logger.info("Election type: %s", election_type)

    try:
        added = scrape_election(url, election_type)  # type: ignore[arg-type]
        logger.info(
            "✅ %d new %ss saved to app/data/%s.json",
            added,
            election_type,
            election_type.lower(),
        )
    except KeyboardInterrupt:
        logger.warning("Interrupted — partial data has been saved.")
        sys.exit(130)
    except Exception as exc:
        logger.error("Scraping failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
