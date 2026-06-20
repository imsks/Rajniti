"""Scrape route tests."""

from unittest.mock import patch

import pytest

from app.browser.scraper import ScrapeResult


@pytest.mark.unit
def test_scrape_success(client) -> None:
    mock_result = ScrapeResult(
        url="https://example.com",
        task="Go to https://example.com",
        result="Example Domain",
        steps_taken=2,
    )
    with patch("app.routes.scrape_routes.run_scrape_agent", return_value=mock_result):
        resp = client.post(
            "/api/v1/scrape",
            json={"url": "https://example.com", "instructions": "Return the title"},
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["result"] == "Example Domain"
    assert data["steps_taken"] == 2


@pytest.mark.unit
def test_scrape_missing_url(client) -> None:
    resp = client.post("/api/v1/scrape", json={"instructions": "noop"})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


@pytest.mark.unit
def test_scrape_agent_failure(client) -> None:
    with patch(
        "app.routes.scrape_routes.run_scrape_agent",
        side_effect=RuntimeError("browser failed"),
    ):
        resp = client.post(
            "/api/v1/scrape",
            json={"url": "https://example.com"},
        )

    assert resp.status_code == 502
    assert "browser failed" in resp.get_json()["error"]
