"""
Election data scrapers for ECI (Election Commission of India) results.

Public API:
    scrape_election(url, election_type)  — scrape and save winning MPs / MLAs
"""

from .scraper import scrape_election

__all__ = [
    "scrape_election",
]
