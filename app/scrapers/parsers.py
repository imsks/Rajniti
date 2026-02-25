"""
Pure HTML parsers for ECI election results pages.

Every function here is a pure function:
  Input:  raw HTML bytes (+ minimal config)
  Output: typed dataclass / None

No network calls, no file I/O, no mutable state → easy to unit-test.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Literal, Optional

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

ElectionType = Literal["MP", "MLA"]


# ── Intermediate data types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class ParsedParty:
    """A party row scraped from the main index page."""

    id: str
    name: str
    short_name: str


@dataclass(frozen=True)
class ParsedConstituency:
    """A constituency won by a party, scraped from the party-wise page."""

    id: str
    name: str
    state_id: str


@dataclass(frozen=True)
class ParsedWinner:
    """The winning candidate from a constituency page."""

    name: str
    party_name: str
    photo_url: Optional[str]


# ── URL builders (pure) ─────────────────────────────────────────────────────


def build_party_page_url(
    base_url: str, party_id: str, election_type: ElectionType
) -> str:
    """Build the URL for a party's won-constituencies page."""
    if election_type == "MP":
        return f"{base_url}/partywisewinresultState-{party_id}.htm"
    return f"{base_url}/partywisewinresult-{party_id}.htm"


def build_constituency_page_url(
    base_url: str, state_id: str, constituency_id: str
) -> str:
    """Build the URL for a constituency's candidate page."""
    return f"{base_url}/candidateswise-{state_id}{constituency_id}.htm"


# ── Year / state extraction (pure) ──────────────────────────────────────────


def extract_year_from_url(url: str, default: int = 2024) -> int:
    """Pull the first 4-digit year from a URL string."""
    match = re.search(r"20\d{2}", url)
    return int(match.group(0)) if match else default


_STATE_PATTERNS: dict[str, tuple[str, str]] = {
    r"delhi|dl": ("DL", "Delhi"),
    r"maharashtra|mh": ("MH", "Maharashtra"),
    r"karnataka|ka": ("KA", "Karnataka"),
    r"gujarat|gj": ("GJ", "Gujarat"),
    r"rajasthan|rj": ("RJ", "Rajasthan"),
    r"punjab|pb": ("PB", "Punjab"),
    r"haryana|hr": ("HR", "Haryana"),
    r"uttarpradesh|up": ("UP", "Uttar Pradesh"),
    r"bihar|br": ("BR", "Bihar"),
    r"westbengal|wb": ("WB", "West Bengal"),
    r"tamilnadu|tn": ("TN", "Tamil Nadu"),
    r"telangana|tg": ("TG", "Telangana"),
    r"andhrapradesh|ap": ("AP", "Andhra Pradesh"),
    r"madhyapradesh|mp": ("MP", "Madhya Pradesh"),
    r"odisha|or": ("OR", "Odisha"),
    r"kerala|kl": ("KL", "Kerala"),
    r"jharkhand|jh": ("JH", "Jharkhand"),
    r"assam|as": ("AS", "Assam"),
    r"chhattisgarh|cg": ("CG", "Chhattisgarh"),
}


def detect_state_from_text(text: str) -> Optional[tuple[str, str]]:
    """
    Return ``(state_code, state_name)`` if a known state is found in *text*,
    else ``None``.
    """
    lowered = text.lower()
    for pattern, info in _STATE_PATTERNS.items():
        if re.search(pattern, lowered):
            return info
    return None


def detect_state_from_index_html(html: bytes) -> Optional[tuple[str, str]]:
    """Try to detect the state from the index page's title area."""
    soup = BeautifulSoup(html, "html.parser")
    main_tag = soup.find("main")
    if not main_tag:
        return None
    title_div = main_tag.find("div", {"class": "page-title"})
    if not title_div:
        return None
    return detect_state_from_text(title_div.get_text())


# ── Party parser ─────────────────────────────────────────────────────────────


def _parse_mp_party_row(cols: list[Tag]) -> Optional[ParsedParty]:
    """Parse a party row from a Lok Sabha index page."""
    full_name = cols[0].get_text(strip=True)
    name, short_name = (full_name.split(" - ", 1) + [""])[:2]

    link = cols[1].find("a")
    if not link or not link.get("href"):
        return None

    party_id = link["href"].split("-")[-1].split(".")[0]
    if not party_id or not name.strip():
        return None
    return ParsedParty(id=party_id, name=name.strip(), short_name=short_name.strip())


def _parse_mla_party_row(cols: list[Tag]) -> Optional[ParsedParty]:
    """Parse a party row from a Vidhan Sabha index page."""
    tag = cols[0].find("a")
    full_name = tag.get_text(strip=True) if tag else cols[0].get_text(strip=True)
    name, short_name = (full_name.split(" - ", 1) + [""])[:2]

    link = cols[1].find("a")
    party_id: Optional[str] = None
    if link and link.get("href"):
        match = re.search(r"partywisewinresult-?(.+?)\.htm", link["href"])
        if match:
            party_id = match.group(1)

    if not party_id or not name.strip():
        return None
    return ParsedParty(id=party_id, name=name.strip(), short_name=short_name.strip())


def parse_parties(html: bytes, election_type: ElectionType) -> List[ParsedParty]:
    """
    Parse party list from the main index page.

    Returns a list of ``ParsedParty`` (one per party that has a valid id).
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table"}) or soup.find("table")
    if not table:
        return []

    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

    parser = _parse_mp_party_row if election_type == "MP" else _parse_mla_party_row
    parties: List[ParsedParty] = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        try:
            party = parser(cols)
            if party:
                parties.append(party)
        except Exception as exc:
            logger.debug("Skipping party row: %s", exc)
    return parties


# ── Constituency parser ──────────────────────────────────────────────────────


def parse_constituencies(html: bytes) -> List[ParsedConstituency]:
    """
    Parse won constituencies from a party-wise results page.

    Works identically for MP and MLA pages (same table structure).
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table"})
    if not table:
        return []

    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else []

    seen: set[str] = set()
    results: List[ParsedConstituency] = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        try:
            a_tag = cols[1].find("a")
            if not a_tag or not a_tag.get("href"):
                continue

            name = a_tag.get_text(strip=True).split("(")[0].strip()
            code = a_tag["href"].split("-")[-1].split(".")[0]
            state_id = code[:3]
            constituency_id = code[3:]
            key = f"{state_id}{constituency_id}"

            if key not in seen:
                seen.add(key)
                results.append(
                    ParsedConstituency(
                        id=constituency_id,
                        name=name,
                        state_id=state_id,
                    )
                )
        except Exception as exc:
            logger.debug("Skipping constituency row: %s", exc)
    return results


# ── Candidate / winner parser ────────────────────────────────────────────────


def _extract_status(cand_info: Tag) -> Optional[str]:
    """Extract status string (WON / LOST / …) from a cand-info block."""
    status_div = cand_info.find("div", {"class": "status"})
    if not status_div:
        return None

    # Strategy 1: div with text-transform (Lok Sabha)
    styled = status_div.find(
        "div", {"style": lambda x: x and "text-transform" in str(x)}
    )
    if styled:
        return styled.get_text(strip=True).upper()

    # Strategy 2: first child div (Vidhan Sabha)
    children = status_div.find_all("div", recursive=False)
    if children:
        return children[0].get_text(strip=True).upper()

    return None


def _extract_name_party(cand_info: Tag) -> Optional[tuple[str, str]]:
    """Return (candidate_name, party_name) or None."""
    nme_prty = cand_info.find("div", {"class": "nme-prty"})
    if not nme_prty:
        return None
    h5 = nme_prty.find("h5")
    h6 = nme_prty.find("h6")
    if not h5 or not h6:
        return None
    return h5.get_text(strip=True), h6.get_text(strip=True)


def _extract_photo(cand_box: Tag, base_url: str) -> Optional[str]:
    """Extract photo URL from a candidate box, resolving relative paths."""
    figure = cand_box.find("figure")
    if not figure:
        return None
    img = figure.find("img")
    if not img or not img.get("src"):
        return None
    src = img["src"].strip()
    if src and not src.startswith("http"):
        src = f"{base_url}/{src.lstrip('/')}"
    return src


def parse_winner(html: bytes, base_url: str) -> Optional[ParsedWinner]:
    """
    Parse the **winning** candidate from a constituency page.

    Returns ``None`` if no WON candidate is found.
    """
    soup = BeautifulSoup(html, "html.parser")
    for cand_box in soup.find_all("div", {"class": "cand-box"}):
        cand_info = cand_box.find("div", {"class": "cand-info"})
        if not cand_info:
            continue

        status = _extract_status(cand_info)
        if status != "WON":
            continue

        name_party = _extract_name_party(cand_info)
        if not name_party:
            continue

        name, party_name = name_party
        photo = _extract_photo(cand_box, base_url)
        return ParsedWinner(name=name, party_name=party_name, photo_url=photo)

    return None
