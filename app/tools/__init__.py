"""
Agent tools — web search, scraping, and Wikipedia lookup.

All tools are designed for **graceful degradation**: if a dependency is
missing or a network call fails the tool returns an empty result instead
of raising.  This lets agents keep working with LLM-only when tools are
unavailable.
"""

from .web_scraper import WebScraperTool
from .web_search import WebSearchTool
from .wikipedia_tool import WikipediaTool

__all__ = ["WebSearchTool", "WebScraperTool", "WikipediaTool"]
