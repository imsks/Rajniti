"""MyNeta resolve route tests."""

from unittest.mock import patch

import pytest

from app.browser.scraper import ScrapeResult


@pytest.mark.unit
def test_myneta_resolve_success(client) -> None:
    mock_result = ScrapeResult(
        url="https://www.myneta.info/Bihar2025/",
        task="search",
        result=(
            '{"url":"https://www.myneta.info/Bihar2025/candidate.php?candidate_id=9",'
            '"candidate_id":"9","election_slug":"Bihar2025"}'
        ),
        steps_taken=4,
    )
    with patch("app.routes.scrape_routes.run_scrape_agent", return_value=mock_result):
        resp = client.post(
            "/api/v1/scrape/myneta/resolve",
            json={
                "name": "Test Candidate",
                "state": "Bihar",
                "constituency": "AC",
                "election_slug": "Bihar2025",
            },
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "candidate_id=9" in data["url"]


@pytest.mark.unit
def test_myneta_resolve_404_when_no_url(client) -> None:
    mock_result = ScrapeResult(
        url="https://www.myneta.info/Bihar2025/",
        task="search",
        result="could not find",
        steps_taken=3,
    )
    with patch("app.routes.scrape_routes.run_scrape_agent", return_value=mock_result):
        resp = client.post(
            "/api/v1/scrape/myneta/resolve",
            json={
                "name": "Nobody",
                "state": "Bihar",
                "constituency": "AC",
                "election_slug": "Bihar2025",
            },
        )

    assert resp.status_code == 404
    assert resp.get_json()["success"] is False


@pytest.mark.unit
def test_myneta_resolve_502_on_agent_failure(client) -> None:
    with patch(
        "app.routes.scrape_routes.run_scrape_agent",
        side_effect=RuntimeError("agent down"),
    ):
        resp = client.post(
            "/api/v1/scrape/myneta/resolve",
            json={
                "name": "Test",
                "state": "Bihar",
                "constituency": "AC",
                "election_slug": "Bihar2025",
            },
        )

    assert resp.status_code == 502
    assert "agent down" in resp.get_json()["error"]
