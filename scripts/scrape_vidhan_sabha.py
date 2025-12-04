#!/usr/bin/env python3
"""
Script to scrape Vidhan Sabha (State Assembly) election data from ECI website.

Usage:
    python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenNov2025
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# NOTE: DATABASE_URL must be set before importing from app package
# because the app.__init__ module initializes database connections.
# This is a workaround to use the scraper independently of the main app.
# Future improvement: Refactor to make database imports lazy/optional.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://dummy:dummy@localhost/dummy"

from app.scrapers.vidhan_sabha import VidhanSabhaScraper  # noqa: E402


def setup_logging():
    """Configure logging for the scraper."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main():
    """Main entry point for Vidhan Sabha scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Vidhan Sabha election data from ECI website"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="ECI Vidhan Sabha results page URL (e.g., https://results.eci.gov.in/ResultAcGenNov2025)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Vidhan Sabha Election Data Scraper")
    logger.info("=" * 80)
    logger.info(f"Source URL: {args.url}")
    logger.info("")

    try:
        # Initialize and run scraper
        scraper = VidhanSabhaScraper(args.url)
        scraper.scrape()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Scraping completed successfully!")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
