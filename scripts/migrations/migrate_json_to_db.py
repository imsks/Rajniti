"""
Migration script to migrate JSON data to database.

This script reads data from the existing JSON files and migrates them to the database.
Works with both local PostgreSQL and Supabase.

Usage:
    python scripts/migrations/migrate_json_to_db.py
    
    # Specify election data directory
    python scripts/migrations/migrate_json_to_db.py --election-dir app/data/lok_sabha/lok-sabha-2024
    
    # Dry run (no changes to database)
    python scripts/migrations/migrate_json_to_db.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import get_db_session, init_db
from app.database.models import Candidate, Constituency, Party


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []


def migrate_parties(
    session, parties_data: List[Dict[str, Any]], dry_run: bool = False
) -> int:
    """Migrate parties to database."""
    print(
        f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {len(parties_data)} parties..."
    )

    if dry_run:
        for party in parties_data[:5]:  # Show first 5 in dry run
            print(f"  - Would create: {party['name']} ({party['short_name']})")
        if len(parties_data) > 5:
            print(f"  - ... and {len(parties_data) - 5} more")
        return len(parties_data)

    try:
        Party.bulk_create(session, parties_data)
        print(f"✓ Successfully migrated {len(parties_data)} parties")
        return len(parties_data)
    except Exception as e:
        print(f"✗ Error migrating parties: {e}")
        return 0


def migrate_constituencies(
    session, constituencies_data: List[Dict[str, Any]], dry_run: bool = False
) -> int:
    """Migrate constituencies to database."""
    print(
        f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {len(constituencies_data)} constituencies..."
    )

    if dry_run:
        for const in constituencies_data[:5]:  # Show first 5 in dry run
            print(f"  - Would create: {const['name']} ({const['state_id']})")
        if len(constituencies_data) > 5:
            print(f"  - ... and {len(constituencies_data) - 5} more")
        return len(constituencies_data)

    try:
        Constituency.bulk_create(session, constituencies_data)
        print(f"✓ Successfully migrated {len(constituencies_data)} constituencies")
        return len(constituencies_data)
    except Exception as e:
        print(f"✗ Error migrating constituencies: {e}")
        return 0


def normalize_candidate_status(status: str) -> str:
    """
    Normalize candidate status to valid enum value.
    
    The candidate_status enum only accepts "WON" or "LOST".
    Empty strings and invalid values are normalized to "LOST".
    
    Args:
        status: Status value from JSON data
        
    Returns:
        Normalized status ("WON" or "LOST")
    """
    if not status or not status.strip():
        return "LOST"
    
    status_upper = status.strip().upper()
    if status_upper == "WON":
        return "WON"
    elif status_upper == "LOST":
        return "LOST"
    else:
        # Handle "UNKNOWN" or any other invalid status
        return "LOST"


def normalize_candidates_data(candidates_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize candidate data before migration.
    
    Ensures all required fields are present and valid enum values are used.
    
    Args:
        candidates_data: List of candidate dictionaries from JSON
        
    Returns:
        Normalized list of candidate dictionaries
    """
    normalized = []
    for candidate in candidates_data:
        normalized_candidate = candidate.copy()
        # Normalize status to valid enum value
        normalized_candidate["status"] = normalize_candidate_status(
            candidate.get("status", "")
        )
        normalized.append(normalized_candidate)
    return normalized


def migrate_candidates(
    session, candidates_data: List[Dict[str, Any]], dry_run: bool = False
) -> int:
    """Migrate candidates to database."""
    print(
        f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {len(candidates_data)} candidates..."
    )

    # Normalize candidate data (handle empty/invalid status values)
    normalized_candidates = normalize_candidates_data(candidates_data)
    
    # Count how many statuses were normalized
    empty_status_count = sum(
        1 for c in candidates_data 
        if not c.get("status") or not c.get("status").strip()
    )
    if empty_status_count > 0:
        print(f"  Note: Normalizing {empty_status_count} candidates with empty/invalid status to 'LOST'")

    if dry_run:
        for cand in normalized_candidates[:5]:  # Show first 5 in dry run
            print(f"  - Would create: {cand['name']} ({cand.get('party_id', 'N/A')}) - Status: {cand.get('status', 'N/A')}")
        if len(normalized_candidates) > 5:
            print(f"  - ... and {len(normalized_candidates) - 5} more")
        return len(normalized_candidates)

    try:
        Candidate.bulk_create(session, normalized_candidates)
        print(f"✓ Successfully migrated {len(normalized_candidates)} candidates")
        return len(normalized_candidates)
    except Exception as e:
        print(f"✗ Error migrating candidates: {e}")
        return 0


def migrate_election_data(election_dir: Path, dry_run: bool = False):
    """
    Migrate election data from JSON files to database.

    Args:
        election_dir: Path to election data directory
        dry_run: If True, only show what would be done without making changes
    """
    print(f"\n{'='*60}")
    print(f"{'DRY RUN - ' if dry_run else ''}Migrating JSON data to database")
    print(f"Source: {election_dir}")
    print(f"{'='*60}")

    # Load JSON files
    parties_file = election_dir / "parties.json"
    constituencies_file = election_dir / "constituencies.json"
    candidates_file = election_dir / "candidates.json"

    parties_data = load_json_file(parties_file)
    constituencies_data = load_json_file(constituencies_file)
    candidates_data = load_json_file(candidates_file)

    if not parties_data and not constituencies_data and not candidates_data:
        print("\n✗ No data found in JSON files. Exiting.")
        return

    # Show summary
    print(f"\nData Summary:")
    print(f"  Parties: {len(parties_data)}")
    print(f"  Constituencies: {len(constituencies_data)}")
    print(f"  Candidates: {len(candidates_data)}")

    if dry_run:
        print(f"\n{'='*60}")
        print("DRY RUN MODE - No changes will be made to database")
        print(f"{'='*60}")

        # Show what would be migrated
        with get_db_session() as session:
            migrate_parties(session, parties_data, dry_run=True)
            migrate_constituencies(session, constituencies_data, dry_run=True)
            migrate_candidates(session, candidates_data, dry_run=True)

        print(f"\n{'='*60}")
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
        print(f"{'='*60}")
        return

    # Proceed with actual migration
    try:
        # Initialize database (create tables if they don't exist)
        print("\nInitializing database...")
        init_db()
        print("✓ Database initialized")

        # Migrate data
        total_migrated = 0
        with get_db_session() as session:
            total_migrated += migrate_parties(session, parties_data)
            total_migrated += migrate_constituencies(session, constituencies_data)
            total_migrated += migrate_candidates(session, candidates_data)

        print(f"\n{'='*60}")
        print(f"Migration Complete!")
        print(f"Total records migrated: {total_migrated}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate JSON election data to database"
    )
    parser.add_argument(
        "--election-dir",
        type=Path,
        default=Path("app/data/lok_sabha/lok-sabha-2024"),
        help="Path to election data directory (default: app/data/lok_sabha/lok-sabha-2024)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Validate election directory
    if not args.election_dir.exists():
        print(f"✗ Error: Election directory not found: {args.election_dir}")
        sys.exit(1)

    # Run migration
    migrate_election_data(args.election_dir, args.dry_run)


if __name__ == "__main__":
    main()
