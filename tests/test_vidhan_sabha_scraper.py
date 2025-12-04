"""
Tests for the Vidhan Sabha scraper.
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# NOTE: DATABASE_URL must be set before importing from app package
# because the app.__init__ module initializes database connections.
# This is required even for testing the scraper in isolation.
# Future improvement: Refactor to make database imports lazy/optional.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

from app.scrapers.vidhan_sabha import VidhanSabhaScraper


# Sample HTML responses for mocking
MOCK_INDEX_HTML = """
<html>
<head><title>November 2025 Election Results</title></head>
<body>
    <table>
        <tr><th>Party</th><th>Symbol</th><th>Leading</th><th>Won</th></tr>
        <tr>
            <td><a href="#">Bharatiya Janata Party - Lotus</a></td>
            <td>1</td>
            <td>2</td>
            <td>48</td>
        </tr>
        <tr>
            <td><a href="#">Aam Aadmi Party - Broom</a></td>
            <td>0</td>
            <td>1</td>
            <td>22</td>
        </tr>
    </table>
    <a href="candidateswise-U051.htm">Constituency 1</a>
    <a href="candidateswise-U052.htm">Constituency 2</a>
</body>
</html>
"""

MOCK_CONSTITUENCY_HTML = """
<html>
<body>
    <div class="cand-box">
        <figure><img src="candidate1.jpg"></figure>
        <div class="cand-info">
            <div class="status won">
                <div style="text-transform: capitalize">Won</div>
                <div>50000 (+5000)</div>
            </div>
            <div class="nme-prty">
                <h5>Candidate Name 1</h5>
                <h6>Bharatiya Janata Party</h6>
            </div>
        </div>
    </div>
    <div class="cand-box">
        <figure><img src="candidate2.jpg"></figure>
        <div class="cand-info">
            <div class="status lost">
                <div style="text-transform: capitalize">Lost</div>
                <div>45000</div>
            </div>
            <div class="nme-prty">
                <h5>Candidate Name 2</h5>
                <h6>Aam Aadmi Party</h6>
            </div>
        </div>
    </div>
</body>
</html>
"""


@pytest.fixture
def mock_http_response():
    """Mock HTTP responses for testing."""
    with patch("app.scrapers.base.get_with_retry") as mock_get:

        def get_mock_response(url, *args, **kwargs):
            response = Mock()
            response.status_code = 200

            if "index.htm" in url:
                response.content = MOCK_INDEX_HTML.encode("utf-8")
            elif "candidateswise" in url:
                response.content = MOCK_CONSTITUENCY_HTML.encode("utf-8")
            else:
                return None

            return response

        mock_get.side_effect = get_mock_response
        yield mock_get


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory."""
    with patch("app.scrapers.base.Path") as mock_path:
        # Mock Path to use tmp_path
        def path_constructor(path_str):
            if path_str == "app/data":
                return tmp_path
            return Path(path_str)

        mock_path.side_effect = path_constructor
        yield tmp_path


def test_vidhan_sabha_scraper_initialization():
    """Test VidhanSabhaScraper initialization."""
    url = "https://results.eci.gov.in/ResultAcGenNov2025"
    scraper = VidhanSabhaScraper(url)

    assert scraper.base_url == url
    assert scraper.state_code is None
    assert scraper.state_name is None
    assert scraper.year is None
    assert isinstance(scraper.parties_data, list)
    assert isinstance(scraper.constituencies_data, list)
    assert isinstance(scraper.candidates_data, list)


def test_detect_state_info_from_url():
    """Test state detection from URL."""
    scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")

    with patch("app.scrapers.base.get_with_retry") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = (
            b"<html><head><title>Chhattisgarh 2025</title></head></html>"
        )
        mock_get.return_value = mock_response

        scraper._detect_state_info()

        assert scraper.year == 2025
        # State might be detected from URL or page content


def test_scrape_parties():
    """Test party scraping."""
    # Patch in vidhan_sabha module where get_with_retry is imported
    with patch("app.scrapers.vidhan_sabha.get_with_retry") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = MOCK_INDEX_HTML.encode("utf-8")
        mock_get.return_value = mock_response

        scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")
        scraper._scrape_parties()

        assert len(scraper.parties_data) > 0

        # Check party data structure
        party = scraper.parties_data[0]
        assert "party_name" in party
        assert "symbol" in party
        assert "total_seats" in party


def test_discover_constituency_links():
    """Test constituency link discovery."""
    with patch("app.scrapers.vidhan_sabha.get_with_retry") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = MOCK_INDEX_HTML.encode("utf-8")
        mock_get.return_value = mock_response

        scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")

        constituencies = scraper._discover_constituency_links()

        assert len(constituencies) > 0

        # Check constituency structure
        const = constituencies[0]
        assert "constituency_code" in const
        assert "name" in const
        assert "url" in const


def test_extract_candidates_from_page():
    """Test candidate extraction from constituency page."""
    from bs4 import BeautifulSoup

    scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")
    soup = BeautifulSoup(MOCK_CONSTITUENCY_HTML, "html.parser")

    candidates = scraper._extract_candidates_from_page(soup, "U051")

    assert len(candidates) == 2

    # Check winner
    winner = candidates[0]
    assert winner["Name"] == "Candidate Name 1"
    assert winner["Party"] == "Bharatiya Janata Party"
    assert winner["Status"] == "WON"
    assert winner["Votes"] == "50000"
    # Margin might have closing paren removed by clean_margin function
    assert "+5000" in winner["Margin"]
    assert winner["Constituency Code"] == "U051"

    # Check loser
    loser = candidates[1]
    assert loser["Status"] == "LOST"
    assert loser["Name"] == "Candidate Name 2"


def test_generate_uuid():
    """Test UUID generation."""
    scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")

    uuid1 = scraper._generate_uuid()
    uuid2 = scraper._generate_uuid()

    # UUIDs should be unique
    assert uuid1 != uuid2
    assert isinstance(uuid1, str)
    assert len(uuid1) > 0


def test_scraper_handles_empty_response():
    """Test scraper handles empty/failed responses gracefully."""
    with patch("app.scrapers.base.get_with_retry") as mock_get:
        mock_get.return_value = None  # Simulate failed request

        scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")
        scraper._scrape_parties()

        # Should not crash, just return empty data
        assert isinstance(scraper.parties_data, list)


def test_save_all_data():
    """Test data saving functionality."""
    # Need to patch save_json in the vidhan_sabha module
    with patch("app.scrapers.vidhan_sabha.save_json") as mock_save:
        scraper = VidhanSabhaScraper("https://results.eci.gov.in/ResultAcGenNov2025")
        scraper.state_code = "DL"
        scraper.state_name = "Delhi"
        scraper.year = 2025
        scraper.folder_name = "DL_2025_ASSEMBLY"
        scraper.election_name = "Delhi Assembly Election 2025"

        # Add some test data
        scraper.parties_data = [
            {"party_name": "Test Party", "symbol": "Test", "total_seats": 10}
        ]
        scraper.constituencies_data = [
            {"constituency_id": "1", "constituency_name": "Test", "state_id": "DL"}
        ]
        scraper.candidates_data = [{"Name": "Test Candidate", "Party": "Test Party"}]

        scraper._save_all_data()

        # Verify save_json was called 4 times (parties, constituencies, candidates, metadata)
        assert mock_save.call_count == 4


def test_full_scrape_workflow():
    """Test complete scraping workflow."""
    with patch("app.scrapers.vidhan_sabha.get_with_retry") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = MOCK_INDEX_HTML.encode("utf-8")
        mock_get.return_value = mock_response

        with patch("app.scrapers.vidhan_sabha.save_json"):
            scraper = VidhanSabhaScraper(
                "https://results.eci.gov.in/ResultAcGenNov2025"
            )

            # Mock state detection
            scraper.state_code = "TEST"
            scraper.state_name = "Test State"
            scraper.year = 2025
            scraper.folder_name = "TEST_2025_ASSEMBLY"
            scraper.election_name = "Test State Assembly Election 2025"

            # Run partial scrape (skip auto-detection to avoid network calls)
            scraper._scrape_parties()

            # Verify data was collected
            assert len(scraper.parties_data) > 0

            # Each party should have required fields
            for party in scraper.parties_data:
                assert "party_name" in party
                assert "total_seats" in party


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
