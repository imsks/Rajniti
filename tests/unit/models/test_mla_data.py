"""
Unit tests for mla.json data integrity and schema validation.

Tests verify that the MLA JSON data file is valid, consistent,
and conforms to the Politician Pydantic schema.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from collections import Counter
import pytest

# Mock chromadb before imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

from app.schemas.politician import Politician
from app.schemas.types import PoliticianType, StatusEnum

# ── File path ────────────────────────────────────────────────────────────────

MLA_JSON_PATH = Path(__file__).resolve().parents[3] / "app" / "data" / "mla.json"


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def mla_data():
    """Load mla.json once for all tests in this module."""
    assert MLA_JSON_PATH.exists(), f"mla.json not found at {MLA_JSON_PATH}"
    with open(MLA_JSON_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list), "mla.json must contain a JSON array"
    return data


@pytest.fixture(scope="module")
def first_mla(mla_data):
    """Return the first MLA record for detailed field tests."""
    assert len(mla_data) > 0, "mla.json must contain at least one record"
    return mla_data[0]


# =============================================================================
# File-Level Tests
# =============================================================================


@pytest.mark.unit
class TestMLAFileIntegrity:
    """Tests for mla.json file-level integrity."""

    def test_file_exists(self):
        """mla.json should exist in app/data/."""
        assert MLA_JSON_PATH.exists()

    def test_file_is_valid_json(self):
        """mla.json should be parseable as valid JSON."""
        with open(MLA_JSON_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data is not None

    def test_top_level_is_list(self, mla_data):
        """Top-level structure must be a JSON array."""
        assert isinstance(mla_data, list)

    def test_data_is_not_empty(self, mla_data):
        """MLA data file should contain at least one record."""
        assert len(mla_data) > 0

    def test_all_entries_are_dicts(self, mla_data):
        """Every entry in the array should be a dict/object."""
        for idx, entry in enumerate(mla_data):
            assert isinstance(entry, dict), f"Entry at index {idx} is not a dict"


# =============================================================================
# Unique ID Tests
# =============================================================================


@pytest.mark.unit
class TestMLAUniqueIds:
    """Tests to ensure MLA records have unique identifiers."""

    def test_all_entries_have_id(self, mla_data):
        """Every MLA entry should have a non-empty 'id' field."""
        for idx, entry in enumerate(mla_data):
            assert "id" in entry, f"Entry at index {idx} missing 'id'"
            assert entry["id"], f"Entry at index {idx} has empty 'id'"

    def test_no_duplicate_ids(self, mla_data):
        """All MLA ids must be unique."""
        ids = [entry["id"] for entry in mla_data if "id" in entry]
        duplicates = {id_ for id_, count in Counter(ids).items() if count > 1}
        assert not duplicates, f"Duplicate IDs found: {duplicates}"


# =============================================================================
# Required Fields Tests
# =============================================================================


@pytest.mark.unit
class TestMLARequiredFields:
    """Tests for required fields in each MLA record."""

    REQUIRED_TOP_LEVEL_KEYS = [
        "id",
        "name",
        "state",
        "constituency",
        "type",
        "political_background",
    ]

    def test_required_top_level_keys_present(self, mla_data):
        """Every entry must have the core required fields."""
        for idx, entry in enumerate(mla_data):
            for key in self.REQUIRED_TOP_LEVEL_KEYS:
                assert key in entry, (
                    f"Entry {idx} (id={entry.get('id', 'N/A')}) missing '{key}'"
                )

    def test_name_is_non_empty_string(self, mla_data):
        """Every MLA must have a non-empty name."""
        for idx, entry in enumerate(mla_data):
            name = entry.get("name")
            assert isinstance(name, str) and len(name.strip()) > 0, (
                f"Entry {idx} has invalid name: {name!r}"
            )

    def test_type_is_mla(self, mla_data):
        """All records in mla.json must have type == 'MLA'."""
        for idx, entry in enumerate(mla_data):
            assert entry.get("type") == "MLA", (
                f"Entry {idx} (id={entry.get('id', 'N/A')}) has type "
                f"'{entry.get('type')}', expected 'MLA'"
            )

    def test_state_is_non_empty_string(self, mla_data):
        """Every MLA must have a non-empty state."""
        for idx, entry in enumerate(mla_data):
            state = entry.get("state")
            assert isinstance(state, str) and len(state.strip()) > 0, (
                f"Entry {idx} has invalid state: {state!r}"
            )

    def test_constituency_is_non_empty_string(self, mla_data):
        """Every MLA must have a non-empty constituency."""
        for idx, entry in enumerate(mla_data):
            constituency = entry.get("constituency")
            assert isinstance(constituency, str) and len(constituency.strip()) > 0, (
                f"Entry {idx} has invalid constituency: {constituency!r}"
            )


# =============================================================================
# Political Background Tests
# =============================================================================


@pytest.mark.unit
class TestMLAPoliticalBackground:
    """Tests for the political_background nested structure."""

    def test_political_background_is_dict(self, mla_data):
        """political_background should be a dict with an 'elections' key."""
        for idx, entry in enumerate(mla_data):
            pb = entry.get("political_background")
            assert isinstance(pb, dict), (
                f"Entry {idx}: political_background must be a dict"
            )

    def test_elections_key_exists(self, mla_data):
        """political_background must contain an 'elections' list."""
        for idx, entry in enumerate(mla_data):
            pb = entry.get("political_background", {})
            assert "elections" in pb, (
                f"Entry {idx}: political_background missing 'elections'"
            )
            assert isinstance(pb["elections"], list), (
                f"Entry {idx}: elections must be a list"
            )

    def test_some_mlas_have_elections(self, mla_data):
        """At least some MLAs should have election records."""
        with_elections = sum(
            1
            for entry in mla_data
            if len(entry.get("political_background", {}).get("elections", [])) > 0
        )
        assert with_elections > 0, "No MLAs have election records"

    def test_elections_not_all_empty(self, mla_data):
        """Count of MLAs with election data for visibility."""
        total = len(mla_data)
        with_elections = sum(
            1
            for entry in mla_data
            if len(entry.get("political_background", {}).get("elections", [])) > 0
        )
        # Informational: currently ~36% have elections; this will grow as data is scraped
        assert with_elections > 0, "Expected at least 1 MLA with election data"

    def test_election_records_have_required_fields(self, mla_data):
        """Each election record must include year, type, state, constituency, party, status."""
        required = {"year", "type", "state", "constituency", "party", "status"}
        for idx, entry in enumerate(mla_data):
            elections = entry.get("political_background", {}).get("elections", [])
            for e_idx, election in enumerate(elections):
                missing = required - set(election.keys())
                assert not missing, (
                    f"Entry {idx}, election {e_idx}: missing fields {missing}"
                )

    def test_election_year_is_int(self, mla_data):
        """Election year must be an integer."""
        for idx, entry in enumerate(mla_data):
            elections = entry.get("political_background", {}).get("elections", [])
            for e_idx, election in enumerate(elections):
                year = election.get("year")
                assert isinstance(year, int), (
                    f"Entry {idx}, election {e_idx}: year must be int, got {type(year)}"
                )

    def test_election_status_is_valid(self, mla_data):
        """Election status must be WON, LOST, or CONTESTED."""
        valid = {"WON", "LOST", "CONTESTED"}
        for idx, entry in enumerate(mla_data):
            elections = entry.get("political_background", {}).get("elections", [])
            for e_idx, election in enumerate(elections):
                status = election.get("status")
                assert status in valid, (
                    f"Entry {idx}, election {e_idx}: invalid status '{status}'"
                )

    def test_election_type_is_mla(self, mla_data):
        """Election type in mla.json elections should be 'MLA'."""
        for idx, entry in enumerate(mla_data):
            elections = entry.get("political_background", {}).get("elections", [])
            for e_idx, election in enumerate(elections):
                assert election.get("type") == "MLA", (
                    f"Entry {idx}, election {e_idx}: type should be 'MLA', "
                    f"got '{election.get('type')}'"
                )


# =============================================================================
# Optional Fields Structure Tests
# =============================================================================


@pytest.mark.unit
class TestMLAOptionalFields:
    """Tests for optional field structure and types."""

    def test_education_is_list_or_null_when_present(self, mla_data):
        """education should be a list or null when present."""
        for idx, entry in enumerate(mla_data):
            if "education" in entry:
                val = entry["education"]
                assert val is None or isinstance(val, list), (
                    f"Entry {idx}: education must be a list or null, got {type(val)}"
                )

    def test_education_entries_have_qualification(self, mla_data):
        """Each education entry should have a 'qualification' field."""
        valid_qualifications = {
            "HIGH_SCHOOL", "DIPLOMA", "BACHELOR", "MASTER",
            "DOCTORATE", "PROFESSIONAL", "OTHERS"
        }
        for idx, entry in enumerate(mla_data):
            for e_idx, edu in enumerate(entry.get("education") or []):
                assert "qualification" in edu, (
                    f"Entry {idx}, education {e_idx}: missing 'qualification'"
                )
                assert edu["qualification"] in valid_qualifications, (
                    f"Entry {idx}, education {e_idx}: "
                    f"invalid qualification '{edu['qualification']}'"
                )

    def test_social_media_is_dict_when_present(self, mla_data):
        """social_media should be a dict when present."""
        for idx, entry in enumerate(mla_data):
            if "social_media" in entry and entry["social_media"] is not None:
                assert isinstance(entry["social_media"], dict), (
                    f"Entry {idx}: social_media must be a dict"
                )

    def test_social_media_has_expected_keys(self, mla_data):
        """social_media should only contain known platform keys."""
        expected_keys = {"twitter", "facebook", "instagram", "linkedin", "youtube", "website"}
        for idx, entry in enumerate(mla_data):
            sm = entry.get("social_media")
            if sm and isinstance(sm, dict):
                unknown = set(sm.keys()) - expected_keys
                assert not unknown, (
                    f"Entry {idx}: unexpected social_media keys {unknown}"
                )

    def test_contact_is_dict_when_present(self, mla_data):
        """contact should be a dict when present."""
        for idx, entry in enumerate(mla_data):
            if "contact" in entry and entry["contact"] is not None:
                assert isinstance(entry["contact"], dict), (
                    f"Entry {idx}: contact must be a dict"
                )

    def test_criminal_records_is_list_or_null_when_present(self, mla_data):
        """criminal_records should be a list or null when present."""
        for idx, entry in enumerate(mla_data):
            if "criminal_records" in entry:
                val = entry["criminal_records"]
                assert val is None or isinstance(val, list), (
                    f"Entry {idx}: criminal_records must be a list or null"
                )

    def test_criminal_records_entries_have_name(self, mla_data):
        """Each criminal record must have a 'name' field."""
        for idx, entry in enumerate(mla_data):
            for c_idx, cr in enumerate(entry.get("criminal_records") or []):
                assert "name" in cr, (
                    f"Entry {idx}, criminal_record {c_idx}: missing 'name'"
                )

    def test_family_background_is_list_or_null_when_present(self, mla_data):
        """family_background should be a list or null when present."""
        for idx, entry in enumerate(mla_data):
            if "family_background" in entry:
                val = entry["family_background"]
                assert val is None or isinstance(val, list), (
                    f"Entry {idx}: family_background must be a list or null"
                )

    def test_family_members_have_required_fields(self, mla_data):
        """Each family member must have 'name' and 'relation'."""
        valid_relations = {
            "FATHER", "MOTHER", "SIBLING", "SON",
            "DAUGHTER", "WIFE", "HUSBAND", "OTHERS"
        }
        for idx, entry in enumerate(mla_data):
            for f_idx, fm in enumerate(entry.get("family_background") or []):
                assert "name" in fm, (
                    f"Entry {idx}, family {f_idx}: missing 'name'"
                )
                assert "relation" in fm, (
                    f"Entry {idx}, family {f_idx}: missing 'relation'"
                )
                assert fm["relation"] in valid_relations, (
                    f"Entry {idx}, family {f_idx}: "
                    f"invalid relation '{fm['relation']}'"
                )


# =============================================================================
# Schema Validation (Pydantic)
# =============================================================================


@pytest.mark.unit
class TestMLASchemaValidation:
    """Validate a sample of MLA records against the Pydantic Politician model."""

    def test_first_record_validates(self, first_mla):
        """The first MLA record should pass Pydantic validation."""
        politician = Politician.parse_obj(first_mla)
        assert politician.type == PoliticianType.MLA
        assert politician.name == first_mla["name"]
        assert str(politician.id) == first_mla["id"]

    def test_sample_records_validate(self, mla_data):
        """Validate a sample of records (first 20 + last 10) against the schema."""
        sample = mla_data[:20] + mla_data[-10:]
        errors = []
        for idx, entry in enumerate(sample):
            try:
                Politician.parse_obj(entry)
            except Exception as exc:
                errors.append(
                    f"Record id={entry.get('id', 'N/A')}: {exc}"
                )
        assert not errors, (
            f"{len(errors)} record(s) failed schema validation:\n"
            + "\n".join(errors[:5])
        )

    def test_all_records_validate(self, mla_data):
        """Every record in mla.json should pass Pydantic validation."""
        errors = []
        for idx, entry in enumerate(mla_data):
            try:
                Politician.parse_obj(entry)
            except Exception as exc:
                errors.append(
                    f"Index {idx}, id={entry.get('id', 'N/A')}: {exc}"
                )
        assert not errors, (
            f"{len(errors)} / {len(mla_data)} records failed validation:\n"
            + "\n".join(errors[:10])
        )


# =============================================================================
# Data Consistency Tests
# =============================================================================


@pytest.mark.unit
class TestMLADataConsistency:
    """Cross-field consistency checks."""

    def test_entry_state_matches_election_state(self, mla_data):
        """The top-level state should appear in at least one election record."""
        mismatches = []
        for idx, entry in enumerate(mla_data):
            top_state = (entry.get("state") or "").strip().lower()
            elections = entry.get("political_background", {}).get("elections", [])
            election_states = {
                (e.get("state") or "").strip().lower() for e in elections
            }
            if top_state and election_states and top_state not in election_states:
                mismatches.append(
                    f"Index {idx} (id={entry.get('id', 'N/A')}): "
                    f"top-level state='{entry.get('state')}' not in election states "
                    f"{[e.get('state') for e in elections]}"
                )
        assert not mismatches, (
            f"{len(mismatches)} state mismatch(es):\n" + "\n".join(mismatches[:5])
        )

    def test_photo_urls_are_valid_format(self, mla_data):
        """Photo URLs, when present, should start with http:// or https://."""
        invalid = []
        for idx, entry in enumerate(mla_data):
            photo = entry.get("photo")
            if photo is not None and not photo.startswith(("http://", "https://")):
                invalid.append(
                    f"Index {idx} (id={entry.get('id', 'N/A')}): photo='{photo}'"
                )
        assert not invalid, (
            f"{len(invalid)} invalid photo URL(s):\n" + "\n".join(invalid[:5])
        )

    def test_social_media_urls_are_valid_format(self, mla_data):
        """Social media URLs, when not null, should start with http(s)://."""
        invalid = []
        for idx, entry in enumerate(mla_data):
            sm = entry.get("social_media", {})
            if not isinstance(sm, dict):
                continue
            for platform, url in sm.items():
                if url is not None and not url.startswith(("http://", "https://")):
                    invalid.append(
                        f"Index {idx}, {platform}: '{url}'"
                    )
        assert not invalid, (
            f"{len(invalid)} invalid social media URL(s):\n" + "\n".join(invalid[:5])
        )

    def test_election_years_are_reasonable(self, mla_data):
        """Election years should be between 1950 and 2030."""
        out_of_range = []
        for idx, entry in enumerate(mla_data):
            elections = entry.get("political_background", {}).get("elections", [])
            for e_idx, election in enumerate(elections):
                year = election.get("year")
                if isinstance(year, int) and (year < 1950 or year > 2030):
                    out_of_range.append(
                        f"Index {idx}, election {e_idx}: year={year}"
                    )
        assert not out_of_range, (
            f"{len(out_of_range)} election(s) with out-of-range year:\n"
            + "\n".join(out_of_range[:5])
        )
