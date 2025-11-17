#!/usr/bin/env python3
"""
Example script showing how to populate candidate data with the Perplexity agent.

This demonstrates how the new detailed candidate fields can be populated
incrementally without breaking if some data is not found.
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def populate_candidate_education(candidate_name: str):
    """
    Example: Populate education background for a candidate.

    In real implementation, this would use Perplexity AI to fetch data.
    """
    logger.info(f"Fetching education background for {candidate_name}")

    try:
        # Simulating Perplexity AI response
        # In real implementation: perplexity_service.search(f"Education background of {candidate_name}")
        education_data = {
            "graduation_year": 1983,
            "stream": "Political Science",
            "college_or_school": "Delhi University",
        }
        logger.info(f"✅ Education data found for {candidate_name}")
        return education_data
    except Exception as e:
        logger.warning(f"⚠️  Could not fetch education data: {e}")
        return None


def populate_candidate_political_history(candidate_name: str):
    """
    Example: Populate political background for a candidate.
    """
    logger.info(f"Fetching political history for {candidate_name}")

    try:
        # Simulating Perplexity AI response
        political_data = {
            "elections": [
                {
                    "election_year": 2019,
                    "election_type": "MP",
                    "constituency": "Varanasi",
                    "party": "Bharatiya Janata Party",
                    "status": "WON",
                },
                {
                    "election_year": 2014,
                    "election_type": "MP",
                    "constituency": "Varanasi",
                    "party": "Bharatiya Janata Party",
                    "status": "WON",
                },
            ]
        }
        logger.info(
            f"✅ Political history found: {len(political_data['elections'])} elections"
        )
        return political_data
    except Exception as e:
        logger.warning(f"⚠️  Could not fetch political history: {e}")
        return None


def populate_candidate_family(candidate_name: str):
    """
    Example: Populate family background for a candidate.
    """
    logger.info(f"Fetching family background for {candidate_name}")

    try:
        # Simulating partial data - not all fields available
        family_data = {
            "father": {"name": "Damodardas Mulchand Modi", "profession": "Tea Seller"},
            "mother": {
                "name": "Heeraben Modi",
                "profession": None,  # Data not available
            },
            # spouse and children data might not be available
        }
        logger.info(f"✅ Family data found (partial)")
        return family_data
    except Exception as e:
        logger.warning(f"⚠️  Could not fetch family data: {e}")
        return None


def populate_candidate_assets(candidate_name: str):
    """
    Example: Populate assets information for a candidate.
    """
    logger.info(f"Fetching assets information for {candidate_name}")

    try:
        # Simulating assets data
        assets_data = {
            "commercial_assets": "No commercial assets declared",
            "cash_assets": "Bank deposits and savings as per affidavit",
            "bank_details": [],  # Bank details might not be publicly available
        }
        logger.info(f"✅ Assets information found")
        return assets_data
    except Exception as e:
        logger.warning(f"⚠️  Could not fetch assets data: {e}")
        return None


def create_candidate_with_detailed_info(candidate_id: str, candidate_name: str):
    """
    Example: Create a candidate record with all available detailed information.

    This demonstrates:
    1. How to populate data incrementally
    2. How missing data doesn't break the code
    3. How to use logging for visibility
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing candidate: {candidate_name} (ID: {candidate_id})")
    logger.info(f"{'='*60}\n")

    # Basic candidate data (always required)
    candidate_basic = {
        "id": candidate_id,
        "name": candidate_name,
        "party_id": "BJP001",
        "constituency_id": "UP-77",
        "state_id": "UP",
        "status": "WON",
        "type": "MP",
        "image_url": "https://example.com/candidate.jpg",
    }

    # Try to populate detailed information
    # Each function returns None if data not found - this is fine!
    candidate_basic["education_background"] = populate_candidate_education(
        candidate_name
    )
    candidate_basic["political_background"] = populate_candidate_political_history(
        candidate_name
    )
    candidate_basic["family_background"] = populate_candidate_family(candidate_name)
    candidate_basic["assets"] = populate_candidate_assets(candidate_name)

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Candidate record created successfully")
    logger.info(f"{'='*60}\n")

    return candidate_basic


def main():
    """Main function demonstrating the workflow"""
    print("\n🚀 Candidate Data Population Example")
    print("=" * 60)
    print("This demonstrates how the Perplexity agent can populate")
    print("candidate data incrementally without breaking if some")
    print("data is not found.\n")

    # Example: Process a candidate
    candidate_data = create_candidate_with_detailed_info("C_MODI_001", "Narendra Modi")

    # Show the final data structure
    print("\n📊 Final Candidate Data Structure:")
    print("=" * 60)
    print(json.dumps(candidate_data, indent=2))

    # Show summary
    print("\n📋 Summary:")
    print("=" * 60)
    fields_populated = sum(
        [
            1
            for field in [
                "education_background",
                "political_background",
                "family_background",
                "assets",
            ]
            if candidate_data.get(field) is not None
        ]
    )
    print(f"✅ Basic fields: Always present")
    print(f"✅ Detailed fields populated: {fields_populated}/4")
    print(
        f"   - Education: {'✓' if candidate_data.get('education_background') else '✗'}"
    )
    print(
        f"   - Political History: {'✓' if candidate_data.get('political_background') else '✗'}"
    )
    print(f"   - Family: {'✓' if candidate_data.get('family_background') else '✗'}")
    print(f"   - Assets: {'✓' if candidate_data.get('assets') else '✗'}")

    print("\n💡 Note: Missing data is handled gracefully - the API")
    print("   can still create the candidate record and update it later!")
    print()


if __name__ == "__main__":
    main()
