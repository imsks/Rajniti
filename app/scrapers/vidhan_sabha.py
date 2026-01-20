"""
Vidhan Sabha Election Data Scraper

Single scraper that extracts all Vidhan Sabha (State Assembly) election data
(parties, constituencies, candidates, metadata) from ECI results page.
"""

import logging
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List
import json, os
from typing import Any, Dict, List
from bs4 import BeautifulSoup

from .base import (
    clean_margin,
    clean_votes,
    get_with_retry,
    normalize_base_url,
    save_json,
)

logger = logging.getLogger(__name__)


class VidhanSabhaScraper:
    """Scraper for Vidhan Sabha (State Assembly) election data."""

    def __init__(self, url: str):
        """
        Initialize Vidhan Sabha scraper.

        Args:
            url: ECI Vidhan Sabha results page URL
                 (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
        """
        self.base_url = normalize_base_url(url)
        self.state_code = None
        self.state_name = None
        self.state_id = None
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
    
    def _generate_party_page_link(self, party_id: str) -> str:
        """Generate a constituency page link from party id."""
        return f"{self.base_url}/partywisewinresult-{party_id}.htm"
    
    def _generate_constituency_page_link(
        self, state_id: str, constituency_id: str
    ) -> str:
        """Generate a constituency page link from state and constituency code."""
        return f"{self.base_url}/candidateswise-{state_id}{constituency_id}.htm"
    
    @staticmethod
    def _append_json(filepath: Path, data):
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
                    
    def scrape(self) -> None:
        """Main scraping orchestrator - scrapes all data and saves to JSON files."""
        logger.info(f"Starting Vidhan Sabha scraping from {self.base_url}")
        self._detect_state_info()
        base_path = Path("app/data")
        self.vidhan_sabha_dir = base_path / "vidhan_sabha" / self.folder_name
        self.elections_dir = base_path / "elections"

        # Extract year and metadata first

        # Prepare directories
        self.parties_file = self.vidhan_sabha_dir / "parties.json"
        self.constituencies_file = self.vidhan_sabha_dir / "constituencies.json"
        self.candidates_file = self.vidhan_sabha_dir / "candidates.json"
        # Detect state and extract metadata first

        # Scrape all data
        # Layer 1: Party-wise results
        logger.info("Scraping party-wise results...")
        parties_data = self._scrape_parties()
        self.parties_data = parties_data
        save_json(self.parties_data, self.parties_file)
        logger.info(f"🌟 Found {str(len(self.parties_data))} parties.")
        
        for party in self.parties_data:
            logger.info(f"\n Scraping Party: {party['name']} ({party['id']})")
            party_id=party["id"]
            party_name=party["name"]
            # Layer 2: Fetch constituencies for this party
            constituencies = self._scrape_constituencies(party_id,self.state_id, party_name)
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

        logger.info("Vidhan Sabha scraping completed successfully!")
        logger.info(f"- Number of Parties found: {party_count}")
        logger.info(f"- Number of Constituenties found: {constituency_count}")
        logger.info(f"- Number of Candidates found: {candidate_count}")

    def _detect_state_info(self) -> None:
        """Auto-detect state code, state name, and year from URL and page content."""
        logger.info("Detecting state and election information...")

        # State patterns for detection
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

        # Try to extract from URL first
        # url_lower = self.base_url.lower()
        # for pattern, (code, name) in state_patterns.items():
        #     if re.search(pattern, url_lower):
        #         self.state_code = code
        #         self.state_name = name
        #         logger.info(f"Detected from URL: {name} ({code})")
        #         break

        # Extract year from URL
        year_match = re.search(r"20\d{2}", self.base_url)
        if year_match:
            self.year = int(year_match.group(0))

        # Fetch page to get more info if needed
        if not self.state_code or not self.year:
            response = get_with_retry(
                f"{self.base_url}/index.htm", referer=self.base_url
            )
            if response:
                soup = BeautifulSoup(response.content, "html.parser")

                # Look in title or headings
                main_tag=soup.find("main").find("div", {"class": "page-title"})
                title = main_tag.find("h2")
                
                if title:
                    title_text = title.get_text()

                    # Try to extract state from title if not found yet
                    if not self.state_code:
                        for pattern, (code, name) in state_patterns.items():
                            if re.search(pattern, title_text, re.IGNORECASE):
                                self.state_code = code
                                self.state_name = name
                                logger.info(
                                    f"Detected from page title: {name} ({code})"
                                )
                                break

                    # Extract year from title if not found yet
                    if not self.year:
                        year_match = re.search(r"20\d{2}", main_tag.find("h1").get_text())
                        if year_match:
                            self.year = int(year_match.group(0))

        # Defaults if still not found
        if not self.state_code:
            logger.warning("Could not detect state code, using 'XX'")
            self.state_code = "XX"
            self.state_name = "Unknown State"

        if not self.year:
            logger.warning("Could not detect year, using 2024")
            self.year = 2024

        # Set folder name and election name
        self.folder_name = f"{self.state_code}_{self.year}_ASSEMBLY"
        self.election_name = f"{self.state_name} Assembly Election {self.year}"

        logger.info(f"Election: {self.election_name}")
        logger.info(f"Output folder: {self.folder_name}")
    
    def _scrape_parties(self) -> List[Dict[str, str]]:
        """Scrape party-wise results and compile party list with seat counts."""
        parties_data = self._discover_parties_details()
        print("partyyy dtaaa::",parties_data)
        if not parties_data:
            logger.warning("No parties discovered")
            return

        logger.info(f"Found {len(parties_data)} parties, scraping results...")

        return parties_data    

    def _discover_parties_details(self) -> List[Dict[str, str]]:
        """Scrape party-wise results from main results page."""
        parties_data = []
        url = f"{self.base_url}/index.htm"
        response = get_with_retry(url, referer=self.base_url)

        if not response:
            logger.error("Failed to fetch party results page")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the party results table
        table = soup.find("table")
        if not table:
            logger.warning("No party table found on main page")
            return

        # Parse party data
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                # Extract party name and symbol
                party_tag = cols[0].find("a")
                full_name = (
                    party_tag.text.strip() if party_tag else cols[0].text.strip()
                )
                constituency_id = cols[1].find("a")["href"].split("-")[-1].split(".")[0]
                party_id=constituency_id[:-3]
                state_id=constituency_id[-3:]
                
                if self.state_id is None:
                    self.state_id = state_id
                # Split party name and symbol (usually "Party Name - Symbol")
                if " - " in full_name:
                    party_name, symbol = full_name.split(" - ", 1)
                else:
                    party_name = full_name
                    symbol = ""

                # Extract seats won
                try:
                    total_seats = int(cols[3].text.strip())
                except (ValueError, IndexError):
                    total_seats = 0

                if party_name:  # Skip empty rows
                    parties_data.append(
                        {
                            "id":party_id,
                            "name": party_name.strip(),
                            "short_name": symbol.strip(),
                            "symbol": "",
                        }
                    )

        # Sort by seats (descending)
        # self.parties_data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))
        logger.info(f"Scraped {len(self.parties_data)} parties")
        return parties_data

    def _scrape_constituencies(self, party_id:str,state_id:str, party_name:str) -> List[Dict[str, str]]:
        """Discover and scrape constituency data."""
        constituencies_data = self._discover_constituency_details(party_id,state_id,party_name)
        return constituencies_data

    def _discover_constituency_details(self,party_id:str,state_id:str,party_name:str) -> List[Dict[str, str]]:
        """Auto-discover constituency links from main page or by sequential probing."""
        constituencies_data = []
        seen_constituencies = set()  # Track unique constituencies to avoid duplicates

        # Try to find constituency links on main page
        url = self._generate_party_page_link(f"{party_id}{state_id}")
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
                        print("uniquuu ids::",state_constituency_id)
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

    def _sequential_constituency_discovery(self) -> List[Dict[str, str]]:
        """
        Fallback: Try sequential constituency codes.
        Stops after 10 consecutive failures.
        """
        constituencies = []
        consecutive_failures = 0
        max_failures = 10
        i = 1

        logger.info("Attempting sequential constituency discovery...")

        while consecutive_failures < max_failures and i <= 300:
            # Try common patterns: U051, U052, etc.
            const_code = f"U05{i}"
            url = f"{self.base_url}/candidateswise-{const_code}.htm"

            response = get_with_retry(url, retries=1, referer=self.base_url)

            if response and response.status_code == 200:
                constituencies.append(
                    {
                        "constituency_code": const_code,
                        "name": f"Constituency {i}",
                        "url": url,
                    }
                )
                consecutive_failures = 0
                if i % 10 == 0:
                    logger.info(f"  Found {i} constituencies so far...")
            else:
                consecutive_failures += 1

            i += 1
            time.sleep(0.2)  # Be polite

        logger.info(f"Sequential discovery found {len(constituencies)} constituencies")
        return constituencies

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
        print(f"all candidates for consitutency {constituency_name}::",candidate_boxes)
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
                total_votes = 0
                margin = 0
                
                if status_div:
                    # Get all divs inside status_div
                    status_divs = status_div.find_all("div", recursive=False)
                    
                    # Status text is in the first div with text-transform: capitalize
                    if len(status_divs) > 0:
                        candidate_status = status_divs[0].text.strip().upper()
                    
                    # Votes and margin are in the second div
                    if len(status_divs) > 1:
                        votes_div = status_divs[1]
                        try:
                            vote_text = votes_div.get_text(strip=True)
                            
                            vote_parts = vote_text.split("(")
                            if len(vote_parts) > 0:
                                total_votes = int(vote_parts[0].strip())
                            
                            margin_span = votes_div.find("span")
                            if margin_span:
                                margin_text = margin_span.get_text(strip=True)
                                raw_margin = margin_text.replace("(", "").replace(")", "").replace("+", "").replace("-", "").replace(" ", "")
                                if raw_margin.isdigit():
                                    margin = int(raw_margin)
                        except (ValueError, AttributeError) as e:
                            logger.warning(f"Error parsing votes/margin for candidate: {e}")
                            total_votes = 0
                            margin = 0
                    
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
                        "total_votes": total_votes,
                        "margin": margin
                    }
                )
            except Exception as e:
                logger.warning(
                    f"Error parsing candidate in {constituency_name}: {str(e)}"
                )
                continue

        logger.info(f"Scraped {len(candidates_data)} candidates from {constituency_name}")
        return candidates_data

    def _extract_candidates_from_page(
        self, soup: BeautifulSoup, constituency_code: str
    ) -> List[Dict]:
        """Extract candidate data from constituency page."""
        candidates = []

        # Look for candidate boxes (common ECI format)
        cand_boxes = soup.find_all("div", class_="cand-box")

        for cand_box in cand_boxes:
            # Status (won/lost)
            status_div = cand_box.find("div", class_="status")
            status_class = status_div.get("class", []) if status_div else []

            status = None
            if "won" in status_class:
                status = "WON"
            elif "lost" in status_class:
                status = "LOST"

            # Votes and margin
            votes, margin = None, None
            if status_div:
                status_divs = status_div.find_all("div")
                if len(status_divs) > 1:
                    vtext = status_divs[1].get_text(strip=True)
                    parts = vtext.split()
                    if parts:
                        votes = clean_votes(parts[0])
                        if len(parts) > 1:
                            margin = clean_margin(parts[1])

            # Name and party
            nme_prty = cand_box.find("div", class_="nme-prty")
            name = None
            party = None

            if nme_prty:
                h5 = nme_prty.find("h5")
                h6 = nme_prty.find("h6")
                name = h5.get_text(strip=True) if h5 else None
                party = h6.get_text(strip=True) if h6 else None

            # Image URL
            img_tag = cand_box.find("img")
            img_src = None
            if img_tag and "src" in img_tag.attrs:
                img_src = img_tag["src"].strip()
                if img_src and not img_src.startswith("http"):
                    img_src = f"{self.base_url}/{img_src}"

            candidates.append(
                {
                    "uuid": self._generate_uuid(),
                    "Constituency Code": constituency_code,
                    "Name": name,
                    "Party": party,
                    "Status": status,
                    "Votes": votes,
                    "Margin": margin,
                    "Image URL": img_src,
                }
            )

        return candidates

    def _save_all_data(self) -> None:
        """Save all scraped data to JSON files in proper folder structure."""
        base_path = Path("app/data")

        # Create folder paths
        vidhan_sabha_dir = base_path / "vidhan_sabha" / self.folder_name
        elections_dir = base_path / "elections"

        # Save parties
        save_json(self.parties_data, vidhan_sabha_dir / "parties.json")

        # Save constituencies
        save_json(self.constituencies_data, vidhan_sabha_dir / "constituencies.json")

        # Save candidates
        save_json(self.candidates_data, vidhan_sabha_dir / "candidates.json")

        # Build and save election metadata
        self.metadata = {
            "election_id": self.folder_name,
            "name": self.election_name,
            "type": "VIDHANSABHA",
            "year": self.year,
            "date": None,
            "state_id": self.state_code,
            "state_name": self.state_name,
            "total_constituencies": len(self.constituencies_data),
            "total_candidates": len(self.candidates_data),
            "total_parties": len(self.parties_data),
            "voter_turnout": None,
            "result_status": "DECLARED",
            "result_date": None,
            "runner_up_party": (
                self.parties_data[1]["party_name"]
                if len(self.parties_data) > 1
                else None
            ),
            "runner_up_seats": (
                self.parties_data[1]["total_seats"] if len(self.parties_data) > 1 else 0
            ),
        }

        save_json(
            [self.metadata], elections_dir / f"VS-{self.state_code}-{self.year}.json"
        )

        logger.info(f"All data saved successfully to {vidhan_sabha_dir}")
