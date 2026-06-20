"""Default ECI election URLs and CLI arg resolution."""

from __future__ import annotations

import re
from typing import Optional

DEFAULT_ELECTION_URLS: dict[str, str] = {
    "MLA": "https://results.eci.gov.in/ResultAcGenNov2025",
    "MP": "https://results.eci.gov.in/PcResultGenJune2024",
}
DEFAULT_ELECTION_TYPE = "MLA"

_URL_PATTERNS: dict[str, str] = {
    r"PcResultGen|lok.?sabha|parliament": "MP",
    r"ResultAcGen|vidhan.?sabha|assembly": "MLA",
}


def detect_election_type(url: str) -> Optional[str]:
    for pattern, etype in _URL_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return etype
    return None


def resolve_scrape_target(
    url: Optional[str],
    election_type: Optional[str],
) -> tuple[str, str]:
    """Resolve URL + type from CLI args, applying defaults when omitted."""
    resolved_url = url
    resolved_type = election_type

    if resolved_type and not resolved_url:
        resolved_url = DEFAULT_ELECTION_URLS.get(resolved_type)
        if not resolved_url:
            raise ValueError(f"No default URL for election type {resolved_type!r}")

    if not resolved_url and not resolved_type:
        resolved_type = DEFAULT_ELECTION_TYPE
        resolved_url = DEFAULT_ELECTION_URLS[DEFAULT_ELECTION_TYPE]

    if not resolved_type:
        resolved_type = detect_election_type(resolved_url or "")
    if not resolved_type:
        raise ValueError(
            "Could not auto-detect election type from URL. Pass --type MP or --type MLA."
        )

    if not resolved_url:
        raise ValueError("Pass --url or --type (MP / MLA uses a built-in default URL).")

    return resolved_url, resolved_type
