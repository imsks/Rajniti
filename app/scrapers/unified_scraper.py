"""
Unified Election Scraper

A single scraper that works for both Lok Sabha (MP) and Vidhan Sabha (MLA) elections.
Only scrapes WON candidates and stores them in simplified mp.json or mla.json format.
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal
import json
from bs4 import BeautifulSoup

from .base import get_with_retry, normalize_base_url, save_json
from app.schemas.politician import Politician, ElectionRecord, PoliticalBackground
from app.services.json_data_service import STATE_NAMES

logger = logging.getLogger(__name__)


class UnifiedScraper:
    """
    Unified scraper for both MP and MLA elections.
    
    Only scrapes candidates who WON their elections.
    Stores data in simplified format: data/mp.json or data/mla.json
    """

    def __init__(self, url: str, election_type: Literal["MP", "MLA"]):
        """
        Initialize unified scraper.

        Args:
            url: ECI election results page URL
            election_type: "MP" for Lok Sabha or "MLA" for Vidhan Sabha
        """
        if election_type not in ["MP", "MLA"]:
            raise ValueError("election_type must be 'MP' or 'MLA'")
        
        self.base_url = normalize_base_url(url)
        self.election_type = election_type
        self.year = None
        self.state_code = None
        self.state_name = None
        
        # Data storage
        self.parties_data = []
        self.won_politicians = []

    def _generate_politician_id(self, state_id: str, constituency_id: str, year: int) -> str:
        """Generate unique politician ID."""
        type_lower = self.election_type.lower()
        # Normalize state_id (handle both S01 and CG formats)
        state_normalized = state_id.lower().replace("s", "").replace("u", "")
        return f"{type_lower}_{year}_{state_normalized}_{constituency_id}"

    def _get_state_name(self, state_id: str) -> str:
        """Get state name from state ID."""
        return STATE_NAMES.get(state_id, "Unknown State")

    def _get_party_name_by_id(self, party_id: str) -> str:
        """Get party name by ID."""
        for party in self.parties_data:
            if party.get("id") == party_id:
                return party.get("name", "Unknown Party")
        return "Unknown Party"

    def _generate_party_page_link(self, party_id: str) -> str:
        """Generate party page link based on election type."""
        if self.election_type == "MP":
            return f"{self.base_url}/partywisewinresultState-{party_id}.htm"
        else:
            return f"{self.base_url}/partywisewinresult-{party_id}.htm"

    def _generate_constituency_page_link(self, state_id: str, constituency_id: str) -> str:
        """Generate constituency page link."""
        return f"{self.base_url}/candidateswise-{state_id}{constituency_id}.htm"

    def _extract_metadata(self) -> None:
        """Extract election metadata from URL and page."""
        logger.info("Extracting election metadata...")
        
        # Extract year from URL
        year_match = re.search(r"20\d{2}", self.base_url)
        self.year = int(year_match.group(0)) if year_match else 2024
        
        # For MLA, try to detect state
        if self.election_type == "MLA":
            state_patterns = {
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
            
            url_lower = self.base_url.lower()
            for pattern, (code, name) in state_patterns.items():
                if re.search(pattern, url_lower):
                    self.state_code = code
                    self.state_name = name
                    break
            
            # If not found in URL, try fetching page
            if not self.state_code:
                response = get_with_retry(f"{self.base_url}/index.htm", referer=self.base_url)
                if response:
                    soup = BeautifulSoup(response.content, "html.parser")
                    main_tag = soup.find("main")
                    if main_tag:
                        title = main_tag.find("div", {"class": "page-title"})
                        if title:
                            title_text = title.get_text()
                            for pattern, (code, name) in state_patterns.items():
                                if re.search(pattern, title_text, re.IGNORECASE):
                                    self.state_code = code
                                    self.state_name = name
                                    break

        logger.info(f"Election Type: {self.election_type}")
        logger.info(f"Year: {self.year}")
        if self.election_type == "MLA":
            logger.info(f"State: {self.state_name} ({self.state_code})")

    def _scrape_parties(self) -> List[Dict[str, str]]:
        """Scrape party list from main page."""
        parties_data = []
        url = f"{self.base_url}/index.htm"
        response = get_with_retry(url, referer=self.base_url)
        
        if not response:
            logger.error("Failed to fetch main page")
            return parties_data

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table"}) or soup.find("table")
        
        if not table:
            logger.warning("No party table found")
            return parties_data

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]  # Skip header if no tbody

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            try:
                if self.election_type == "MP":
                    # MP format: "Party Name - Short Name" in first column
                    full_name = cols[0].text.strip()
                    if " - " in full_name:
                        name, short_name = full_name.split(" - ", 1)
                    else:
                        name = full_name
                        short_name = ""
                    
                    # Party ID from link in second column
                    link = cols[1].find("a")
                    if link and link.has_attr("href"):
                        href = link.get("href", "")
                        party_id = href.split("-")[-1].split(".")[0]
                    else:
                        continue
                else:
                    # MLA format
                    party_tag = cols[0].find("a")
                    full_name = party_tag.text.strip() if party_tag else cols[0].text.strip()
                    
                    if " - " in full_name:
                        name, short_name = full_name.split(" - ", 1)
                    else:
                        name = full_name
                        short_name = ""
                    
                    link = cols[1].find("a")
                    party_id = None
                    if link and link.has_attr("href"):
                        href = link.get("href", "")
                        match = re.search(r"partywisewinresult-?(.+?)\.htm", href)
                        if match:
                            party_id = match.group(1)

                if party_id and name:
                    parties_data.append({
                        "id": party_id,
                        "name": name.strip(),
                        "short_name": short_name.strip(),
                        "symbol": ""
                    })
            except Exception as e:
                logger.warning(f"Error parsing party row: {e}")
                continue

        logger.info(f"Found {len(parties_data)} parties")
        return parties_data

    def _scrape_constituencies_for_party(self, party_id: str) -> List[Dict[str, str]]:
        """Scrape constituencies won by a party."""
        constituencies = []
        seen = set()

        url = self._generate_party_page_link(party_id)
        response = get_with_retry(url, referer=self.base_url)
        
        if not response:
            return constituencies

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table"})
        
        if not table:
            return constituencies

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            try:
                a_tag = cols[1].find("a")
                constituency_name = (
                    a_tag.text.strip().split("(")[0] if a_tag
                    else cols[1].text.strip().split("(")[0]
                )
                
                link = a_tag.get("href") if a_tag and a_tag.has_attr("href") else None
                
                if link:
                    state_constituency_id = link.split("-")[-1].split(".")[0]
                    state_id = state_constituency_id[:3]
                    constituency_id = state_constituency_id[3:]
                    
                    unique_key = f"{state_id}{constituency_id}"
                    if unique_key not in seen:
                        seen.add(unique_key)
                        constituencies.append({
                            "id": constituency_id,
                            "name": constituency_name,
                            "state_id": state_id
                        })
            except Exception as e:
                logger.warning(f"Error parsing constituency: {e}")
                continue

        return constituencies

    def _scrape_won_candidate(
        self, state_id: str, constituency_id: str, constituency_name: str
    ) -> Optional[Dict[str, Any]]:
        """Scrape the winning candidate from a constituency page."""
        url = self._generate_constituency_page_link(state_id, constituency_id)
        response = get_with_retry(url, referer=self.base_url)
        
        if not response:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        candidate_boxes = soup.find_all("div", {"class": "cand-box"})
        
        if not candidate_boxes:
            return None

        # Find the winning candidate
        for cand_box in candidate_boxes:
            try:
                cand_info = cand_box.find("div", {"class": "cand-info"})
                if not cand_info:
                    continue

                # Check status
                status_div = cand_info.find("div", {"class": "status"})
                if not status_div:
                    continue

                # Extract status
                status = "LOST"
                if self.election_type == "MP":
                    status_text_div = status_div.find("div", {"style": lambda x: x and "text-transform" in x})
                    if status_text_div:
                        status = status_text_div.text.strip().upper()
                else:
                    status_divs = status_div.find_all("div", recursive=False)
                    if len(status_divs) > 0:
                        status = status_divs[0].text.strip().upper()

                # Only process WON candidates
                if status != "WON":
                    continue

                # Extract name and party
                nme_prty = cand_info.find("div", {"class": "nme-prty"})
                if not nme_prty:
                    continue

                name_tag = nme_prty.find("h5")
                party_tag = nme_prty.find("h6")
                
                if not name_tag or not party_tag:
                    continue

                candidate_name = name_tag.text.strip()
                party_name = party_tag.text.strip()

                # Find party ID
                party_id = None
                for party in self.parties_data:
                    if (party.get("name", "").strip().lower() == party_name.strip().lower() or
                        party.get("short_name", "").strip().lower() == party_name.strip().lower()):
                        party_id = party.get("id")
                        break

                if not party_id:
                    party_id = "INDEPENDENT"

                # Extract photo
                figure = cand_box.find("figure")
                photo_url = None
                if figure:
                    img_tag = figure.find("img")
                    if img_tag and img_tag.has_attr("src"):
                        photo_url = img_tag["src"]
                        if not photo_url.startswith("http"):
                            photo_url = f"{self.base_url}/{photo_url.lstrip('/')}"

                # Get state name
                state_name = self._get_state_name(state_id)

                return {
                    "name": candidate_name,
                    "party_id": party_id,
                    "party_name": party_name,
                    "state_id": state_id,
                    "state_name": state_name,
                    "constituency_id": constituency_id,
                    "constituency_name": constituency_name,
                    "photo_url": photo_url,
                    "status": status
                }
            except Exception as e:
                logger.warning(f"Error parsing candidate: {e}")
                continue

        return None

    def scrape(self) -> None:
        """Main scraping method - only scrapes WON candidates."""
        logger.info(f"Starting {self.election_type} scraping from {self.base_url}")
        
        self._extract_metadata()
        
        # Scrape parties
        logger.info("Scraping parties...")
        self.parties_data = self._scrape_parties()
        
        if not self.parties_data:
            logger.error("No parties found. Cannot proceed.")
            return

        # For each party, get constituencies they won
        logger.info("Scraping constituencies and winning candidates...")
        for party in self.parties_data:
            party_id = party["id"]
            party_name = party["name"]
            logger.info(f"Processing party: {party_name} ({party_id})")
            
            constituencies = self._scrape_constituencies_for_party(party_id)
            logger.info(f"  Found {len(constituencies)} constituencies for {party_name}")
            
            # For each constituency, get the winning candidate
            for constituency in constituencies:
                state_id = constituency["state_id"]
                constituency_id = constituency["id"]
                constituency_name = constituency["name"]
                
                candidate = self._scrape_won_candidate(
                    state_id, constituency_id, constituency_name
                )
                
                if candidate:
                    # Create politician object
                    politician_id = self._generate_politician_id(
                        state_id, constituency_id, self.year
                    )
                    
                    # Build election record
                    election_record = ElectionRecord(
                        year=self.year,
                        type=self.election_type,
                        state=candidate["state_name"],
                        constituency=candidate["constituency_name"],
                        party=candidate["party_name"],
                        status="WON"
                    )
                    
                    politician = Politician(
                        id=politician_id,
                        name=candidate["name"],
                        photo=candidate.get("photo_url"),
                        state=candidate["state_name"],
                        constituency=candidate["constituency_name"],
                        type=self.election_type,
                        political_background=PoliticalBackground(
                            elections=[election_record],
                            summary=None
                        ),
                        education=None,
                        family_background=None,
                        social_media=None,
                        contact=None,
                        notes=None
                    )
                    
                    self.won_politicians.append(politician)
                    logger.info(f"  ✓ Added: {candidate['name']} ({constituency_name})")

        logger.info(f"\n✅ Scraping complete! Found {len(self.won_politicians)} winning {self.election_type}s")

    def save(self, output_dir: Path = None) -> None:
        """Save scraped politicians to JSON file."""
        if output_dir is None:
            output_dir = Path("app/data")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine output file
        if self.election_type == "MP":
            output_file = output_dir / "mp.json"
        else:
            output_file = output_dir / "mla.json"
        
        # Convert to dict and save
        politicians_data = [p.model_dump(exclude_none=True) for p in self.won_politicians]
        
        # If file exists, merge with existing data (avoid duplicates)
        if output_file.exists():
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    existing_ids = {p.get("id") for p in existing}
                    # Only add new politicians
                    new_politicians = [
                        p for p in politicians_data
                        if p.get("id") not in existing_ids
                    ]
                    politicians_data = existing + new_politicians
                    logger.info(f"Merged with existing data. Added {len(new_politicians)} new politicians.")
            except json.JSONDecodeError:
                logger.warning("Existing file is invalid JSON. Overwriting.")
        
        save_json(politicians_data, output_file)
        logger.info(f"✅ Saved {len(politicians_data)} {self.election_type}s to {output_file}")
