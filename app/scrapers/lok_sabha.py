"""
Lok Sabha Election Data Scraper

Single scraper that extracts all election data (parties, constituencies, candidates, metadata)
from ECI Lok Sabha results page.
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List
import json, os
from bs4 import BeautifulSoup
from .base import get_with_retry, normalize_base_url, save_json
logger = logging.getLogger(__name__)


class LokSabhaScraper:
    """Scraper for Lok Sabha election data."""

    def __init__(self, url: str):
        """
        Initialize Lok Sabha scraper.

        Args:
            url: ECI Lok Sabha results page URL
                 (e.g., https://results.eci.gov.in/PcResultGenJune2024/index.htm)
        """
        self.base_url = normalize_base_url(url)
        self.year = None
        self.election_name = None
        self.folder_name = None

        # Data storage
        self.parties_data = []
        self.constituencies_data = []
        self.candidates_data = []
        self.metadata = {}

    def _generate_uuid(self) -> str:
        """Generate a unique UUID for a candidate."""
        return str(uuid.uuid4())

    @staticmethod
    def _append_json(filepath: Path, data: Any):
        """Append one or multiple records to a JSON array file efficiently."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if not filepath.exists():
            # If file doesn't exist, always store as a flat list
            if isinstance(data, list):
                json_data = data
            else:
                json_data = [data]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
        else:
            with open(filepath, "r+", encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []
                if isinstance(data, list):
                    existing.extend(data)
                else:
                    existing.append(data)
                f.seek(0)
                json.dump(existing, f, ensure_ascii=False, indent=2)


    def _get_party_id_by_name(self, party_name: str) -> str:
        """
        Convert party name to party ID by looking up in parties_data.
        
        Args:
            party_name: Full party name to search for
            
        Returns:
            Party ID if found, otherwise returns 'UNKNOWN'
        """
        if not party_name:
            return "UNKNOWN"

        # Normalize the input party name for comparison
        party_name_normalized = party_name.strip().lower()

        for party in self.parties_data:
            # Check against both full name and short name
            if (party["name"].strip().lower() == party_name_normalized or 
                party["short_name"].strip().lower() == party_name_normalized):
                return party["id"]

        logger.warning(f"Party not found: {party_name}")
        return "UNKNOWN"

    def _get_constituency_id_by_name(self, constituency_name: str, state_id: str = None) -> str:
        """
        Convert constituency name to constituency ID by looking up in constituencies_data.
        
        Args:
            constituency_name: Full constituency name to search for
            state_id: Optional state ID to narrow down the search
            
        Returns:
            Constituency ID if found, otherwise returns 'UNKNOWN'
        """
        if not constituency_name:
            return "UNKNOWN"

        # Normalize the input constituency name for comparison
        constituency_name_normalized = constituency_name.strip().lower()

        for constituency in self.constituencies_data:
            # If state_id is provided, filter by state
            if state_id and constituency.get("state_id") != state_id:
                continue

            if constituency["name"].strip().lower() == constituency_name_normalized:
                return constituency["id"]

        logger.warning(f"Constituency not found: {constituency_name}")
        return "UNKNOWN"

    def _get_party_by_id(self, party_id: str) -> Dict[str, Any]:
        """
        Get party details by ID.
        
        Args:
            party_id: Party ID to search for
            
        Returns:
            Party dictionary if found, otherwise returns empty dict
        """
        for party in self.parties_data:
            if party["id"] == party_id:
                return party

        return {}

    def _generate_party_page_link(self, party_id: str) -> str:
        """Generate a constituency page link from party id."""
        return f"{self.base_url}/partywisewinresultState-{party_id}.htm"

    def _generate_constituency_page_link(
        self, state_id: str, constituency_id: str
    ) -> str:
        """Generate a constituency page link from state and constituency code."""
        return f"{self.base_url}/candidateswise-{state_id}{constituency_id}.htm"
    
    @staticmethod
    def count_json_records(filepath):
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return len(data)
                except Exception:
                    return 0
            return 0
        
    def scrape(self) -> None:
        """Main scraping orchestrator - scrapes all data and saves to JSON files."""
        logger.info(f"Starting Lok Sabha scraping from {self.base_url}")
        base_path = Path("app/data")

        self._extract_metadata()
        # Create folder paths
        self.lok_sabha_dir = base_path / "lok_sabha" / self.folder_name
        self.elections_dir = base_path / "elections"

        # Extract year and metadata first

        # Prepare directories
        self.parties_file = self.lok_sabha_dir / "parties.json"
        self.constituencies_file = self.lok_sabha_dir / "constituencies.json"
        self.candidates_file = self.lok_sabha_dir / "candidates.json"

        # Scrape all data
        # Layer 1: Party-wise results
        logger.info("Scraping party-wise results...")
        parties_data = self._scrape_parties()
        self.parties_data = parties_data
        save_json(self.parties_data, self.parties_file)
        logger.info(f"✅ Found {len(self.parties_data)} parties.")

        for party in self.parties_data:
            logger.info(f"\n Scraping Party: {party['name']} ({party['id']})")
            party_id=party["id"]
            party_name=party["name"]
            # Layer 2: Fetch constituencies for this party
            constituencies = self._scrape_constituencies(party_id, party_name)
            print(f" all constituencies for {party_name} found are {constituencies}")
            if not constituencies:
                logger.warning(f"No constituencies found for {party_name}")
                continue


            # Squash all constituencies for this party
            for constituency in constituencies:
                self._append_json(self.constituencies_file, constituency)

            # Layer 3: For each constituency, scrape candidates
            for constituency in constituencies:
                allcandidates = []

                constituency_state_id = constituency["state_id"]
                constituency_id = constituency["id"]
                constituency_name = constituency["name"]
                candidates = self._scrape_candidates(
                    constituency_state_id, constituency_id, constituency_name
                )

                # Collect all candidates for this constituency
                allcandidates.extend(candidates)

                # Save all candidates of this constituency together
                if allcandidates:
                    for cand in allcandidates:
                        self._append_json(self.candidates_file, cand)

                logger.info(
                    f"{len(allcandidates)} candidates saved for {constituency_name}"
                )


        party_count = self.count_json_records(self.parties_file)
        constituency_count = self.count_json_records(self.constituencies_file)
        candidate_count = self.count_json_records(self.candidates_file)

        logger.info("Lok Sabha scraping completed successfully!")
        logger.info(f"- Number of Parties found: {party_count}")
        logger.info(f"- Number of Constituenties found: {constituency_count}")
        logger.info(f"- Number of Candidates found: {candidate_count}")

    def _extract_metadata(self) -> None:
        """Extract election metadata from the main page."""
        logger.info("Extracting election metadata...")

        # Try to extract year from URL as primary method
        year_match = re.search(r"20\d{2}", self.base_url)
        self.year = int(year_match.group(0)) if year_match else 2024

        self.election_name = f"Lok Sabha General Election {self.year}"
        self.folder_name = f"lok-sabha-{self.year}"

        logger.info(f"Detected: {self.election_name}")
        logger.info(f"Output folder: {self.folder_name}")

    def _scrape_parties(self) -> List[Dict[str, str]]:
        """Scrape party-wise results and compile party list with seat counts."""
        parties_data = self._discover_parties_details()

        if not parties_data:
            logger.warning("No parties discovered")
            return

        logger.info(f"Found {len(parties_data)} parties, scraping results...")

        return parties_data

    def _discover_parties_details(self) -> List[Dict[str, str]]:
        """Discover party links from main results page."""
        parties_data = []

        urls_to_try = [
            f"{self.base_url}/index.htm",
        ]

        for url in urls_to_try:
            response = get_with_retry(url, referer=self.base_url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Find the party results table
            table = soup.find("table", {"class": "table"})
            if not table:
                logger.warning("No party table found on main page")
                return parties_data

            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        full_name = cols[0].text.strip()
                        name = full_name.split(" - ")[0]
                        short_name = full_name.split(" - ")[1]
                        id = cols[1].find("a")["href"].split("-")[-1].split(".")[0]
                        parties_data.append(
                            {
                                "id": id,
                                "name": name,
                                "short_name": short_name,
                                "symbol": "",
                            }
                        )

        return parties_data

    def _scrape_constituencies(self, party_id:str, party_name:str) -> List[Dict[str, str]]:
        """Discover and scrape constituency data."""
        constituencies_data = self._discover_constituency_details(party_id,party_name)

        return constituencies_data

    def _discover_constituency_details(
        self, party_id: str, party_name: str
    ) -> List[Dict[str, str]]:
        """Auto-discover constituency details from main page."""
        logger.info("Discovering constituency details...")
        constituencies_data = []
        seen_constituencies = set()  # Track unique constituencies to avoid duplicates

        # Fetch Constituency Results page
        # for party in parties_data:
        #     party_id = party["id"]
        #     party_name = party["name"]

        url = self._generate_party_page_link(party_id)
        response = get_with_retry(url, referer=self.base_url)
        if not response:
            logger.warning(f"Could not fetch party results page for {party_name}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table"})
        if not table:
            logger.warning(f"No party table found on {party_name} results page")
            return []

        tbody = table.find("tbody")
        if tbody:
            rows = tbody.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 1:
                    a_tag = cols[1].find("a")
                    consituency_name = (
                            a_tag.text.strip().split("(")[0]
                            if a_tag
                            else cols[1].text.strip().split("(")[0]
                        )
                    link = (
                            a_tag["href"] if a_tag and a_tag.has_attr("href") else None
                        )

                    if link:
                        state_constituency_id = link.split("-")[-1].split(".")[0]
                        state_id = state_constituency_id[:3]
                        constituency_id = state_constituency_id[3:]

                        # Use full state+constituency code as unique key
                        unique_key = f"{state_id}{constituency_id}"

                        if unique_key not in seen_constituencies:
                            seen_constituencies.add(unique_key)
                            constituencies_data.append(
                                    {
                                        "id": constituency_id,
                                        "name": consituency_name,
                                        "state_id": state_id,
                                    }
                                )

        logger.info(f"Discovered {len(constituencies_data)} unique constituencies")
        return constituencies_data

    def _scrape_candidates(
        self, state_id: str, constituency_id: str, constituency_name: str,
    ) -> List[Dict[str, Any]]:
        """Scrape candidate data from constituency pages."""
        candidates_data = self._discover_candidate_details(state_id,constituency_id,constituency_name)

        return candidates_data

    def _discover_candidate_details(
        self, state_id: str, constituency_id: str, constituency_name: str
    ) -> List[Dict[str, Any]]:
        """Discover candidate details from constituency pages."""
        candidates_data = []


        url = self._generate_constituency_page_link(state_id, constituency_id)
        print("URL", url)
        response = get_with_retry(url, referer=self.base_url)
        if not response:
            logger.warning(
                    f"Could not fetch constituency page for {constituency_name}"
                )
            return []

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all candidate boxes
        candidate_boxes = soup.find_all("div", {"class": "cand-box"})
        if not candidate_boxes:
            logger.warning(
                    f"No candidate boxes found on {constituency_name} page"
                )
            return []

        # Parse each candidate
        for cand_box in candidate_boxes:
            try:
                # Extract image
                figure = cand_box.find("figure")
                candidate_image = None
                if figure:
                    img_tag = figure.find("img")
                    if img_tag and img_tag.has_attr("src"):
                        candidate_image = img_tag["src"]

                # Extract candidate info section
                cand_info = cand_box.find("div", {"class": "cand-info"})
                if not cand_info:
                    continue

                # Extract status (won/lost/trailing)
                status_div = cand_info.find("div", {"class": "status"})
                candidate_status = "UNKNOWN"
                if status_div:
                    # Status text is in a nested div with text-transform: capitalize
                    status_text_div = status_div.find("div", {"style": lambda x: x and "text-transform" in x})
                    if status_text_div:
                        candidate_status = status_text_div.text.strip().upper()

                # Extract name and party
                nme_prty = cand_info.find("div", {"class": "nme-prty"})
                if not nme_prty:
                    continue

                candidate_name_tag = nme_prty.find("h5")
                candidate_party_name_tag = nme_prty.find("h6")

                if not candidate_name_tag or not candidate_party_name_tag:
                    continue

                candidate_name = candidate_name_tag.text.strip()
                candidate_party_name = candidate_party_name_tag.text.strip()

                # Convert party name to party ID
                candidate_party_id = self._get_party_id_by_name(candidate_party_name)

                # Add candidate to data
                candidates_data.append(
                        {
                            "id": self._generate_uuid(),
                            "name": candidate_name,
                            "party_id": candidate_party_id,
                            "constituency_id": constituency_id,
                            "state_id": state_id,
                            "status": candidate_status,
                            "type": "MP",
                            "image_url": candidate_image,
                        }
                    )
            except Exception as e:
                logger.warning(
                        f"Error parsing candidate in {constituency_name}: {str(e)}"
                    )
                continue

        logger.info(f"Scraped {len(candidates_data)} candidates")
        return candidates_data

    def _save_all_data(self) -> None:
        """Save all scraped data to JSON files in proper folder structure."""
        base_path = Path("app/data")

        # Create folder paths
        lok_sabha_dir = base_path / "lok_sabha" / self.folder_name
        elections_dir = base_path / "elections"

        # Save parties
        save_json(self.parties_data, lok_sabha_dir / "parties.json")

        # Save constituencies
        save_json(self.constituencies_data, lok_sabha_dir / "constituencies.json")

        # Save candidates
        save_json(self.candidates_data, lok_sabha_dir / "candidates.json")

        self.metadata = {
            "election_id": self.folder_name,
            "name": self.election_name,
            "type": "LOK_SABHA",
            "year": self.year,
            "date": None,
            "total_constituencies": len(self.constituencies_data),
            "total_candidates": len(self.candidates_data),
            "total_parties": len(self.parties_data),
            "result_status": "DECLARED",
        }

        save_json([self.metadata], elections_dir / f"LS-{self.year}.json")

        logger.info(f"All data saved successfully to {lok_sabha_dir}")
