"""
Migration Script: Convert existing election data to new Politician format

This is a one-time migration script that:
1. Reads existing data from lok_sabha and vidhan_sabha folders
2. Filters only WON candidates
3. Transforms to new Politician model
4. Saves to data/mp.json and data/mla.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.schemas.politician import (
    Politician,
    ElectionRecord,
    PoliticalBackground,
)
from app.services.json_data_service import STATE_NAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_state_name(state_id: str) -> str:
    """Get state name from state ID."""
    return STATE_NAMES.get(state_id, "Unknown State")


def generate_politician_id(election_type: str, year: int, state_id: str, constituency_id: str) -> str:
    """Generate unique politician ID."""
    type_lower = election_type.lower()
    # Normalize state_id
    state_normalized = state_id.lower().replace("s", "").replace("u", "")
    return f"{type_lower}_{year}_{state_normalized}_{constituency_id}"


def load_json_file(filepath: Path) -> List[Dict]:
    """Load JSON file, return empty list if file doesn't exist or is invalid."""
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return []


def _stringify_values(obj):
    """
    Recursively convert non-primitive values to strings so JSON serialization
    doesn't fail (e.g., pydantic HttpUrl objects).
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [_stringify_values(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _stringify_values(v) for k, v in obj.items()}
    try:
        return str(obj)
    except Exception:
        return obj


def migrate_lok_sabha_data(base_data_dir: Path) -> List[Politician]:
    """Migrate Lok Sabha (MP) data to Politician format."""
    logger.info("=" * 60)
    logger.info("Migrating Lok Sabha (MP) data...")
    logger.info("=" * 60)
    
    politicians = []
    lok_sabha_dir = base_data_dir / "lok_sabha"
    
    if not lok_sabha_dir.exists():
        logger.warning(f"Lok Sabha directory not found: {lok_sabha_dir}")
        return politicians
    
    # Find all lok sabha election folders
    election_folders = [d for d in lok_sabha_dir.iterdir() if d.is_dir()]
    
    for election_dir in election_folders:
        logger.info(f"\nProcessing: {election_dir.name}")
        
        candidates_file = election_dir / "candidates.json"
        constituencies_file = election_dir / "constituencies.json"
        parties_file = election_dir / "parties.json"
        
        # Load data
        candidates = load_json_file(candidates_file)
        constituencies = load_json_file(constituencies_file)
        parties = load_json_file(parties_file)
        
        if not candidates:
            logger.warning(f"No candidates found in {election_dir.name}")
            continue
        
        # Create lookup dictionaries
        parties_by_id = {p.get("id"): p for p in parties}
        # Create constituency lookup by state_id + constituency_id
        constituencies_by_key = {}
        for const in constituencies:
            state_id = const.get("state_id", "")
            const_id = const.get("id", "")
            key = f"{state_id}_{const_id}"
            constituencies_by_key[key] = const
        
        # Extract year from folder name (e.g., "lok-sabha-2024" -> 2024)
        year_match = None
        if "2024" in election_dir.name:
            year = 2024
        elif "2025" in election_dir.name:
            year = 2025
        else:
            # Try to extract from folder name
            import re
            year_match = re.search(r"20\d{2}", election_dir.name)
            year = int(year_match.group(0)) if year_match else 2024
        
        logger.info(f"Processing {len(candidates)} candidates for year {year}")
        
        # Filter only WON candidates
        won_candidates = [c for c in candidates if c.get("status", "").upper() == "WON"]
        logger.info(f"Found {len(won_candidates)} winning candidates")
        
        # Process each winning candidate
        for candidate in won_candidates:
            try:
                state_id = candidate.get("state_id", "")
                constituency_id = candidate.get("constituency_id", "")

                # Look up constituency name
                constituency_key = f"{state_id}_{constituency_id}"
                constituency = constituencies_by_key.get(constituency_key, {})
                constituency_name = constituency.get(
                    "name", candidate.get("constituency_name", f"Constituency {constituency_id}")
                )
                
                # Get party info
                party_id = candidate.get("party_id", "INDEPENDENT")
                party = parties_by_id.get(party_id, {})
                party_name = party.get("name", "Unknown Party")
                
                # Get state name
                state_name = get_state_name(state_id)
                
                # Generate politician ID
                politician_id = generate_politician_id("MP", year, state_id, constituency_id)
                
                # Create election record
                election_record = ElectionRecord(
                    year=year,
                    type="MP",
                    state=state_name,
                    constituency=constituency_name,
                    party=party_name,
                    status="WON"
                )
                
                # Create politician
                politician = Politician(
                    id=politician_id,
                    name=candidate.get("name", "Unknown"),
                    photo=candidate.get("image_url"),
                    state=state_name,
                    constituency=constituency_name,
                    type="MP",
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
                
                politicians.append(politician)
                
            except Exception as e:
                logger.error(f"Error processing candidate {candidate.get('name', 'Unknown')}: {e}")
                continue
    
    logger.info(f"\n✅ Migrated {len(politicians)} MPs")
    return politicians


def migrate_vidhan_sabha_data(base_data_dir: Path) -> List[Politician]:
    """Migrate Vidhan Sabha (MLA) data to Politician format."""
    logger.info("=" * 60)
    logger.info("Migrating Vidhan Sabha (MLA) data...")
    logger.info("=" * 60)
    
    politicians = []
    vidhan_sabha_dir = base_data_dir / "vidhan_sabha"
    
    if not vidhan_sabha_dir.exists():
        logger.warning(f"Vidhan Sabha directory not found: {vidhan_sabha_dir}")
        return politicians
    
    # Find all vidhan sabha election folders
    election_folders = [d for d in vidhan_sabha_dir.iterdir() if d.is_dir()]
    
    for election_dir in election_folders:
        logger.info(f"\nProcessing: {election_dir.name}")
        
        candidates_file = election_dir / "candidates.json"
        constituencies_file = election_dir / "constituencies.json"
        parties_file = election_dir / "parties.json"
        
        # Load data
        candidates = load_json_file(candidates_file)
        constituencies = load_json_file(constituencies_file)
        parties = load_json_file(parties_file)
        
        if not candidates:
            logger.warning(f"No candidates found in {election_dir.name}")
            continue
        
        # Create lookup dictionaries
        parties_by_id = {p.get("id"): p for p in parties}
        # Create constituency lookup by state_id + constituency_id
        constituencies_by_key = {}
        for const in constituencies:
            state_id = const.get("state_id", "")
            const_id = const.get("id", "")
            key = f"{state_id}_{const_id}"
            constituencies_by_key[key] = const
        
        # Extract year and state from folder name (e.g., "CG_2025_ASSEMBLY" -> CG, 2025)
        import re
        year_match = re.search(r"20\d{2}", election_dir.name)
        year = int(year_match.group(0)) if year_match else 2025
        
        # Extract state code (first 2-3 letters before underscore)
        state_code_match = re.match(r"^([A-Z]{2,3})_", election_dir.name)
        state_code = state_code_match.group(1) if state_code_match else None
        
        logger.info(f"Processing {len(candidates)} candidates for {state_code} {year}")
        
        # Filter only WON candidates
        won_candidates = [c for c in candidates if c.get("status", "").upper() == "WON"]
        logger.info(f"Found {len(won_candidates)} winning candidates")
        
        # Process each winning candidate
        for candidate in won_candidates:
            try:
                state_id = candidate.get("state_id", state_code or "")
                constituency_id = candidate.get("constituency_id", "")
                
                # Look up constituency name
                constituency_key = f"{state_id}_{constituency_id}"
                constituency = constituencies_by_key.get(constituency_key, {})
                constituency_name = constituency.get("name", candidate.get("constituency_name", f"Constituency {constituency_id}"))
                
                # Get party info
                party_id = candidate.get("party_id", "INDEPENDENT")
                party = parties_by_id.get(party_id, {})
                party_name = party.get("name", "Unknown Party")
                
                # Get state name
                state_name = get_state_name(state_id)
                
                # Generate politician ID
                politician_id = generate_politician_id("MLA", year, state_id, constituency_id)
                
                # Create election record
                election_record = ElectionRecord(
                    year=year,
                    type="MLA",
                    state=state_name,
                    constituency=constituency_name,
                    party=party_name,
                    status="WON"
                )
                
                # Create politician
                politician = Politician(
                    id=politician_id,
                    name=candidate.get("name", "Unknown"),
                    photo=candidate.get("image_url"),
                    state=state_name,
                    constituency=constituency_name,
                    type="MLA",
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
                
                politicians.append(politician)
                
            except Exception as e:
                logger.error(f"Error processing candidate {candidate.get('name', 'Unknown')}: {e}: {e}")
                continue
    
    logger.info(f"\n✅ Migrated {len(politicians)} MLAs")
    return politicians


def main():
    """Main migration function."""
    logger.info("Starting migration to Politician format...")
    
    # Determine base data directory
    base_data_dir = Path(__file__).resolve().parents[1] / "app" / "data"
    
    if not base_data_dir.exists():
        logger.error(f"Data directory not found: {base_data_dir}")
        return
    
    # Migrate MPs
    mp_politicians = migrate_lok_sabha_data(base_data_dir)
    
    # Migrate MLAs
    mla_politicians = migrate_vidhan_sabha_data(base_data_dir)
    
    # Save to output files
    output_dir = base_data_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save MPs
    if mp_politicians:
        mp_file = output_dir / "mp.json"
        mp_data = [_stringify_values(p.model_dump(exclude_none=True)) for p in mp_politicians]
        with open(mp_file, "w", encoding="utf-8") as f:
            json.dump(mp_data, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✅ Saved {len(mp_politicians)} MPs to {mp_file}")
    else:
        logger.warning("No MPs to save")
    
    # Save MLAs
    if mla_politicians:
        mla_file = output_dir / "mla.json"
        mla_data = [_stringify_values(p.model_dump(exclude_none=True)) for p in mla_politicians]
        with open(mla_file, "w", encoding="utf-8") as f:
            json.dump(mla_data, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(mla_politicians)} MLAs to {mla_file}")
    else:
        logger.warning("No MLAs to save")
    
    logger.info("\n" + "=" * 60)
    logger.info("Migration complete!")
    logger.info(f"Total MPs: {len(mp_politicians)}")
    logger.info(f"Total MLAs: {len(mla_politicians)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
