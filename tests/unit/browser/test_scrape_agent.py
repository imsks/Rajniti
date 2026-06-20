"""Plain-text browser scrape agent tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.browser.scraper import (
    PLAIN_SCRAPE_SYSTEM_HINT,
    ScrapeResult,
    build_scrape_task,
    run_scrape_agent,
)


def test_build_scrape_task_with_instructions() -> None:
    task = build_scrape_task("https://example.com", "Return the title.")
    assert "https://example.com" in task
    assert "Return the title." in task
    assert "plain-text" in task.lower()


def test_build_scrape_task_default() -> None:
    task = build_scrape_task("https://example.com")
    assert "page title" in task.lower()
    assert "headings" in task.lower()


def test_plain_scrape_system_hint_mentions_json() -> None:
    assert "raw JSON only" in PLAIN_SCRAPE_SYSTEM_HINT


@pytest.mark.unit
def test_run_scrape_agent_returns_result() -> None:
    mock_history = MagicMock()
    mock_history.final_result.return_value = "Example Domain"
    mock_history.__len__.return_value = 2

    mock_agent = MagicMock()
    mock_agent.run = AsyncMock(return_value=mock_history)

    with patch("app.browser.scraper.Agent", return_value=mock_agent):
        result = run_scrape_agent("https://example.com", "Return the title.", max_steps=5)

    assert isinstance(result, ScrapeResult)
    assert result.url == "https://example.com"
    assert result.result == "Example Domain"
    assert result.steps_taken == 2
    mock_agent.run.assert_awaited_once_with(max_steps=5)
