"""Tests for Wikipedia bundle helpers, REST path encoding, and citation guard."""

from unittest.mock import MagicMock, patch

from app.tools.wikipedia_tool import (
    WikipediaTool,
    _encode_title_for_rest_path,
    _filter_external_links,
    summary_matches_wikipedia_extract,
)


def test_encode_title_for_rest_path_spaces_and_dots() -> None:
    assert _encode_title_for_rest_path("C. M. Ramesh") == "C._M._Ramesh"


def test_encode_slash_in_title_percent_encodes() -> None:
    out = _encode_title_for_rest_path("Foo/Bar")
    assert "/" not in out
    assert "%2F" in out


def test_filter_external_links_dedupe_and_drop_wiki() -> None:
    raw = [
        "https://en.wikipedia.org/wiki/X",
        "https://timesofindia.indiatimes.com/a",
        "https://timesofindia.indiatimes.com/a",
        "https://www.wikimedia.org/page",
        "mailto:nobody@example.com",
    ]
    assert _filter_external_links(raw, limit=10) == [
        "https://timesofindia.indiatimes.com/a",
    ]


def test_summary_matches_wikipedia_extract() -> None:
    assert summary_matches_wikipedia_extract(
        "Chintakunta Munuswamy Ramesh is a leader.",
        "Chintakunta Munuswamy Ramesh is an Indian politician from BJP.",
    )
    assert not summary_matches_wikipedia_extract("", "Some extract")
    assert not summary_matches_wikipedia_extract(
        "Unrelated bio text here", "Different person entirely with other tokens"
    )


def _json_response(data: dict, status: int = 200):
    r = MagicMock()
    r.status_code = status
    r.raise_for_status = MagicMock()

    def _json():
        return data

    r.json = _json
    return r


@patch("app.tools.wikipedia_tool.httpx.get")
def test_summary_payload_404(mock_get) -> None:
    r = MagicMock()
    r.status_code = 404
    mock_get.return_value = r
    tool = WikipediaTool()
    assert tool.summary_payload("Missing_Page") is None


@patch("app.tools.wikipedia_tool.httpx.get")
def test_politician_wikipedia_bundle(mock_get) -> None:
    mock_get.side_effect = [
        _json_response({"query": {"search": [{"title": "C. M. Ramesh", "snippet": ""}]}}),
        _json_response(
            {
                "extract": "Chintakunta Munuswamy Ramesh is an Indian politician.",
                "content_urls": {
                    "desktop": {"page": "https://en.wikipedia.org/wiki/C._M._Ramesh"}
                },
            }
        ),
        _json_response(
            {
                "parse": {
                    "externallinks": [
                        "https://en.wikipedia.org/wiki/Something",
                        "https://www.thehindu.com/news/national/article.xhtml",
                    ]
                }
            }
        ),
    ]
    tool = WikipediaTool()
    b = tool.politician_wikipedia_bundle("C.M.RAMESH", "Andhra Pradesh")
    assert b is not None
    assert b["article_url"] == "https://en.wikipedia.org/wiki/C._M._Ramesh"
    assert "Indian politician" in b["extract"]
    assert b["external_links"] == [
        "https://www.thehindu.com/news/national/article.xhtml"
    ]
    assert mock_get.call_count == 3


@patch("app.tools.wikipedia_tool.httpx.get")
def test_summary_returns_extract_from_payload(mock_get) -> None:
    mock_get.return_value = _json_response({"extract": "Short bio."})
    tool = WikipediaTool()
    assert tool.summary("Any") == "Short bio."


def test_prune_keeps_matching_wikipedia_summary_citation() -> None:
    tool = WikipediaTool()
    politician = {
        "name": "X",
        "state": "",
        "political_background": {
            "summary": "Chintakunta Munuswamy Ramesh is a leader.",
            "elections": [],
        },
    }
    updates = {
        "political_background": {
            **(politician["political_background"]),
            "summary_citation": {"link": "https://EN.WIKIPEDIA.org/wiki/Test", "source": "OTHERS"},
        },
    }
    bundle = {"extract": "Chintakunta Munuswamy Ramesh is an Indian politician from BJP."}

    with patch.object(WikipediaTool, "politician_wikipedia_bundle", return_value=bundle):
        out, extra = tool.prune_misaligned_wikipedia_summary_citation(politician, updates)

    assert not extra
    assert out["political_background"].get("summary_citation")


def test_prune_drops_misaligned_wikipedia_summary_citation() -> None:
    tool = WikipediaTool()
    politician = {
        "name": "Jane Q Public",
        "state": "",
        "political_background": {
            "summary": "Completely different subject line about orbital mechanics.",
            "elections": [],
        },
    }
    updates = {
        "political_background": {
            **(politician["political_background"]),
            "summary_citation": {"link": "https://en.wikipedia.org/wiki/Jane_Q_Public", "source": "OTHERS"},
        },
    }
    bundle = {"extract": "Jane Q Public is a noted Indian politician from Kerala."}

    with patch.object(WikipediaTool, "politician_wikipedia_bundle", return_value=bundle):
        out, extra = tool.prune_misaligned_wikipedia_summary_citation(politician, updates)

    assert extra
    assert out["political_background"].get("summary_citation") is None
