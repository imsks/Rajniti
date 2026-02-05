#!/usr/bin/env python3
"""
Generic script to scrape election data from ECI website.

Supports multiple election types (Lok Sabha, Vidhan Sabha, etc.) and saves
all data directly to JSON files following the JSON-first architecture.

Usage:
    # Auto-detect election type from URL
    python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025

    # Explicitly specify election type
    python scripts/scrape_election.py --url https://results.eci.gov.in/PcResultGenJune2024 --type lok-sabha

    # Vidhan Sabha example
    python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025 --type vidhan-sabha
"""

import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers.unified_scraper import UnifiedScraper


# Election type mapping - maps to MP/MLA for unified scraper
ELECTION_TYPE_MAP = {
    "lok-sabha": "MP",
    "vidhan-sabha": "MLA",
}

# URL patterns for auto-detection
ELECTION_URL_PATTERNS = {
    "lok-sabha": [
        r"PcResultGen",
        r"lok.?sabha",
        r"parliament",
    ],
    "vidhan-sabha": [
        r"ResultAcGen",
        r"vidhan.?sabha",
        r"assembly",
        r"state.?assembly",
    ],
}


def setup_logging():
    """Configure logging for the scraper."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def detect_election_type(url: str) -> Optional[str]:
    """
    Auto-detect election type from URL patterns.

    Args:
        url: ECI results page URL

    Returns:
        Election type string (e.g., 'lok-sabha', 'vidhan-sabha') or None
    """
    url_lower = url.lower()

    for election_type, patterns in ELECTION_URL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return election_type

    return None


def get_election_type_code(election_type: str) -> str:
    """
    Get the election type code (MP/MLA) for the unified scraper.

    Args:
        election_type: Election type string (e.g., 'lok-sabha', 'vidhan-sabha')

    Returns:
        Election type code ('MP' or 'MLA')

    Raises:
        ValueError: If election type is not supported
    """
    if election_type not in ELECTION_TYPE_MAP:
        supported = ", ".join(ELECTION_TYPE_MAP.keys())
        raise ValueError(
            f"Unsupported election type: {election_type}. "
            f"Supported types: {supported}"
        )

    return ELECTION_TYPE_MAP[election_type]


def main():
    """Main entry point for election scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape election data from ECI website and save to JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect election type
  %(prog)s --url https://results.eci.gov.in/ResultAcGenNov2025

  # Explicitly specify election type
  %(prog)s --url https://results.eci.gov.in/PcResultGenJune2024 --type lok-sabha

  # Vidhan Sabha
  %(prog)s --url https://results.eci.gov.in/ResultAcGenNov2025 --type vidhan-sabha
        """,
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="ECI election results page URL",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=list(ELECTION_TYPE_MAP.keys()),
        default=None,
        help="Election type (auto-detected from URL if not specified). "
        f"Options: {', '.join(ELECTION_TYPE_MAP.keys())}",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Election Data Scraper (JSON-First Architecture)")
    logger.info("=" * 80)
    logger.info(f"Source URL: {args.url}")

    # Determine election type
    election_type = args.type
    if not election_type:
        election_type = detect_election_type(args.url)
        if election_type:
            logger.info(f"Auto-detected election type: {election_type}")
        else:
            logger.error(
                "Could not auto-detect election type from URL. "
                f"Please specify --type. Supported types: {', '.join(ELECTION_TYPE_MAP.keys())}"
            )
            sys.exit(1)
    else:
        logger.info(f"Using election type: {election_type}")

    logger.info("")

    try:
        # Get the election type code (MP/MLA)
        type_code = get_election_type_code(election_type)
        logger.info(f"Using unified scraper for {type_code} elections")

        # Initialize and run unified scraper
        scraper = UnifiedScraper(args.url, type_code)
        scraper.scrape()
        scraper.save()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Scraping completed successfully!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📁 WON {type_code}s have been saved to app/data/{type_code.lower()}.json")
        logger.info("   Only winning candidates are stored in the simplified format.")

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Scraping interrupted by user")
        logger.info("💾 Partial data may have been saved to JSON files.")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}", exc_info=True)
        logger.info("💾 Partial data may have been saved to JSON files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
