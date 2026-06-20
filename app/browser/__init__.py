"""Browser-use extraction for Rajniti sources (lazy import — optional dep)."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.browser.scraper import BrowserExtractResult, ScrapeResult

T = TypeVar("T", bound=BaseModel)


def run_browser_extract(
    url: str,
    instructions: str,
    *,
    output_model: type[T],
    max_steps: int | None = None,
):
    from app.browser.scraper import run_browser_extract as _run

    return _run(url, instructions, output_model=output_model, max_steps=max_steps)


def run_scrape_agent(
    url: str,
    instructions: str | None = None,
    *,
    max_steps: int | None = None,
):
    from app.browser.scraper import run_scrape_agent as _run

    return _run(url, instructions, max_steps=max_steps)


__all__ = ["run_browser_extract", "run_scrape_agent"]
