#!/usr/bin/env python3
"""
Scrape winning MPs / MLAs from ECI election results.

Usage:
    # Auto-detect election type from URL
    python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025

    # Explicitly specify election type
    python scripts/scrape_election.py --url https://results.eci.gov.in/PcResultGenJune2024 --type MP

    # Vidhan Sabha
    python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025 --type MLA
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.scrapers.scraper import scrape_election

# ── URL-based auto-detection ─────────────────────────────────────────────────

_URL_PATTERNS: dict[str, str] = {
    r"PcResultGen|lok.?sabha|parliament": "MP",
    r"ResultAcGen|vidhan.?sabha|assembly": "MLA",
}


def _detect_type(url: str) -> Optional[str]:
    for pattern, etype in _URL_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return etype
    return None


# ── Entrypoint ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape winning MPs / MLAs from ECI and save to mp.json / mla.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", required=True, help="ECI election results page URL")
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

    # Resolve election type
    election_type: Optional[str] = args.type or _detect_type(args.url)
    if not election_type:
        logger.error(
            "Could not auto-detect election type from URL. "
            "Please pass --type MP or --type MLA."
        )
        sys.exit(1)

    logger.info("URL: %s", args.url)
    logger.info("Election type: %s", election_type)

    try:
        added = scrape_election(args.url, election_type)  # type: ignore[arg-type]
        logger.info("✅ %d new %ss saved to app/data/%s.json", added, election_type, election_type.lower())
    except KeyboardInterrupt:
        logger.warning("Interrupted — partial data has been saved.")
        sys.exit(130)
    except Exception as exc:
        logger.error("Scraping failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
