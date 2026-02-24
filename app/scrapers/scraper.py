"""
Election Scraper — orchestrator module.

Wires together HTTP, parsers, schema validation, and storage to scrape
winning MPs / MLAs from the ECI website and persist them one-by-one.

Usage:
    from app.scrapers.scraper import scrape_election
    scrape_election(url="https://results.eci.gov.in/PcResultGenJune2024", election_type="MP")
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

from app.constants import STATE_NAMES
from app.schemas.politician import ElectionRecord, PoliticalBackground, Politician

from .http import fetch_page, normalize_base_url
from .parsers import (
    ElectionType,
    ParsedConstituency,
    ParsedParty,
    ParsedWinner,
    build_constituency_page_url,
    build_party_page_url,
    detect_state_from_index_html,
    detect_state_from_text,
    extract_year_from_url,
    parse_constituencies,
    parse_parties,
    parse_winner,
)
from .storage import append_politician, get_output_path, load_existing_ids

logger = logging.getLogger(__name__)


# ── Pure helpers ─────────────────────────────────────────────────────────────


def _state_name(state_id: str) -> str:
    """Resolve a state_id to its human-readable name."""
    return STATE_NAMES.get(state_id, "Unknown State")


def _make_politician_id() -> str:
    return str(uuid.uuid5())


def _build_politician(
    *,
    election_type: ElectionType,
    year: int,
    state_id: str,
    constituency: ParsedConstituency,
    winner: ParsedWinner,
    parties: list[ParsedParty],
) -> Politician:
    """Assemble a validated Politician model from parsed fragments."""
    state = _state_name(state_id)
    pid = _make_politician_id(election_type, year, state_id, constituency.id)

    # Resolve party name — prefer the name from the winner's page, fall back
    # to the party list if the winner's party text was a short name.
    party_display = winner.party_name
    for p in parties:
        if (
            p.name.lower() == winner.party_name.lower()
            or p.short_name.lower() == winner.party_name.lower()
        ):
            party_display = p.name
            break

    return Politician(
        id=pid,
        name=winner.name,
        photo=winner.photo_url,
        state=state,
        constituency=constituency.name,
        type=election_type,
        political_background=PoliticalBackground(
            elections=[
                ElectionRecord(
                    year=year,
                    type=election_type,
                    state=state,
                    constituency=constituency.name,
                    party=party_display,
                    status="WON",
                )
            ],
        ),
    )


# ── Main entry point ────────────────────────────────────────────────────────


def scrape_election(
    url: str,
    election_type: ElectionType,
    *,
    data_dir: Optional[Path] = None,
) -> int:
    """
    Scrape winning candidates and persist them to ``mp.json`` or ``mla.json``.

    Each winner is validated via the ``Politician`` Pydantic model and saved
    immediately after scraping, so partial progress is never lost.

    Args:
        url: ECI results page URL (index page)
        election_type: ``"MP"`` (Lok Sabha) or ``"MLA"`` (Vidhan Sabha)
        data_dir: Override the output directory (default ``app/data``)

    Returns:
        Number of **new** politicians added during this run.
    """
    base_url = normalize_base_url(url)
    year = extract_year_from_url(base_url)
    output_path = get_output_path(election_type, data_dir)
    existing_ids = load_existing_ids(output_path)

    logger.info("=" * 70)
    logger.info("Scraping %s elections from %s", election_type, base_url)
    logger.info(
        "Year: %d | Output: %s | Existing: %d", year, output_path, len(existing_ids)
    )
    logger.info("=" * 70)

    # ── Step 1: Fetch index page ─────────────────────────────────────────
    index_html = fetch_page(f"{base_url}/index.htm", referer=base_url)
    if not index_html:
        logger.error("Failed to fetch index page. Aborting.")
        return 0

    # ── Step 2: Detect state (MLA only) ──────────────────────────────────
    if election_type == "MLA":
        state_info = detect_state_from_text(base_url) or detect_state_from_index_html(
            index_html
        )
        if state_info:
            logger.info("Detected state: %s (%s)", state_info[1], state_info[0])
        else:
            logger.warning("Could not detect state from URL or page.")

    # ── Step 3: Parse parties ────────────────────────────────────────────
    parties = parse_parties(index_html, election_type)
    if not parties:
        logger.error("No parties found. Aborting.")
        return 0
    logger.info("Found %d parties", len(parties))

    # ── Step 4: For each party → constituencies → winner ─────────────────
    added = 0
    for party in parties:
        party_url = build_party_page_url(base_url, party.id, election_type)
        party_html = fetch_page(party_url, referer=base_url)
        if not party_html:
            logger.warning("Could not fetch party page for %s", party.name)
            continue

        constituencies = parse_constituencies(party_html)
        logger.info(
            "Party: %s (%s) — %d constituencies",
            party.name,
            party.id,
            len(constituencies),
        )

        for constituency in constituencies:
            # Build a deterministic ID to skip early if already stored
            pid = _make_politician_id(
                election_type, year, constituency.state_id, constituency.id
            )
            if pid in existing_ids:
                logger.debug("Already stored: %s — skipping fetch", pid)
                continue

            const_url = build_constituency_page_url(
                base_url,
                constituency.state_id,
                constituency.id,
            )
            const_html = fetch_page(const_url, referer=base_url)
            if not const_html:
                logger.warning("  ✗ Failed to fetch %s", constituency.name)
                continue

            winner = parse_winner(const_html, base_url)
            if not winner:
                logger.warning("  ✗ No winner found for %s", constituency.name)
                continue

            # Validate via Pydantic
            try:
                politician = _build_politician(
                    election_type=election_type,
                    year=year,
                    state_id=constituency.state_id,
                    constituency=constituency,
                    winner=winner,
                    parties=parties,
                )
            except Exception as exc:
                logger.error("  ✗ Validation failed for %s: %s", constituency.name, exc)
                continue

            # Persist immediately (one-by-one, dedup by id)
            pol_dict = politician.model_dump(mode="json", exclude_none=True)
            was_added = append_politician(pol_dict, output_path, existing_ids)

            if was_added:
                added += 1
                logger.info("  ✓ Saved: %s ← %s", constituency.name, winner.name)

    logger.info("=" * 70)
    logger.info(
        "✅ Done! Added %d new %ss (total on disk: %d)",
        added,
        election_type,
        len(existing_ids),
    )
    logger.info("=" * 70)
    return added
