#!/usr/bin/env python3
"""
Verification script to demonstrate Vidhan Sabha scraper output format.

This creates sample JSON files to show the expected structure.
"""

import json
import os
from pathlib import Path


def create_sample_json_files():
    """Create sample JSON files showing the expected output format."""
    # Base path
    base_path = Path("app/data")

    # Sample data directory
    sample_dir = base_path / "vidhan_sabha" / "SAMPLE_2025_ASSEMBLY"
    sample_dir.mkdir(parents=True, exist_ok=True)

    # Sample parties data
    parties_data = [
        {"party_name": "Bharatiya Janata Party", "symbol": "Lotus", "total_seats": 48},
        {"party_name": "Aam Aadmi Party", "symbol": "Broom", "total_seats": 22},
        {
            "party_name": "Indian National Congress",
            "symbol": "Hand",
            "total_seats": 0,
        },
    ]

    # Sample constituencies data
    constituencies_data = [
        {
            "constituency_id": "U051",
            "constituency_name": "New Delhi",
            "state_id": "DL",
        },
        {
            "constituency_id": "U052",
            "constituency_name": "Chandni Chowk",
            "state_id": "DL",
        },
    ]

    # Sample candidates data
    candidates_data = [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "Constituency Code": "U051",
            "Name": "Sample Candidate 1",
            "Party": "Bharatiya Janata Party",
            "Status": "WON",
            "Votes": "50123",
            "Margin": "(+5234)",
            "Image URL": "https://example.com/image1.jpg",
        },
        {
            "uuid": "223e4567-e89b-12d3-a456-426614174001",
            "Constituency Code": "U051",
            "Name": "Sample Candidate 2",
            "Party": "Aam Aadmi Party",
            "Status": "LOST",
            "Votes": "44889",
            "Margin": None,
            "Image URL": "https://example.com/image2.jpg",
        },
    ]

    # Sample election metadata
    election_metadata = [
        {
            "election_id": "SAMPLE_2025_ASSEMBLY",
            "name": "Sample State Assembly Election 2025",
            "type": "VIDHANSABHA",
            "year": 2025,
            "date": None,
            "state_id": "SAMPLE",
            "state_name": "Sample State",
            "total_constituencies": 2,
            "total_candidates": 2,
            "total_parties": 3,
            "voter_turnout": None,
            "result_status": "DECLARED",
            "result_date": None,
            "runner_up_party": "Aam Aadmi Party",
            "runner_up_seats": 22,
        }
    ]

    # Save files
    with open(sample_dir / "parties.json", "w", encoding="utf-8") as f:
        json.dump(parties_data, f, indent=4, ensure_ascii=False)

    with open(sample_dir / "constituencies.json", "w", encoding="utf-8") as f:
        json.dump(constituencies_data, f, indent=4, ensure_ascii=False)

    with open(sample_dir / "candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates_data, f, indent=4, ensure_ascii=False)

    elections_dir = base_path / "elections"
    elections_dir.mkdir(parents=True, exist_ok=True)

    with open(elections_dir / "VS-SAMPLE-2025.json", "w", encoding="utf-8") as f:
        json.dump(election_metadata, f, indent=4, ensure_ascii=False)

    print("✅ Sample JSON files created successfully!")
    print(f"\n📁 Output directory: {sample_dir}")
    print("\n📄 Files created:")
    print(f"  - {sample_dir / 'parties.json'}")
    print(f"  - {sample_dir / 'constituencies.json'}")
    print(f"  - {sample_dir / 'candidates.json'}")
    print(f"  - {elections_dir / 'VS-SAMPLE-2025.json'}")

    # Display sample party data
    print("\n📊 Sample parties.json:")
    print(json.dumps(parties_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    create_sample_json_files()
