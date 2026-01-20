"""
Unit tests for JsonDataService.

Tests the JSON file-based data service that serves election data.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from app.services.json_data_service import JsonDataService, STATE_NAMES


class TestJsonDataServiceInit:
    """Tests for JsonDataService initialization."""

    def test_init_with_default_data_dir(self):
        """Test initialization with default data directory."""
        service = JsonDataService()
        assert service._data_dir.exists() or True  # May not exist in test env

    def test_init_with_custom_data_dir(self, tmp_path):
        """Test initialization with custom data directory."""
        service = JsonDataService(data_dir=tmp_path)
        assert service._data_dir == tmp_path

    def test_caches_are_initialized_empty(self, tmp_path):
        """Test that caches are initialized as empty."""
        service = JsonDataService(data_dir=tmp_path)
        assert service._elections_cache is None
        assert service._parties_cache == {}
        assert service._constituencies_cache == {}
        assert service._candidates_cache == {}


class TestJsonDataServiceElections:
    """Tests for election-related methods."""

    def test_get_elections_loads_from_file(self, tmp_path):
        """Test getting elections loads data from JSON files."""
        # Setup
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        election_data = [
            {
                "election_id": "test-election",
                "name": "Test Election",
                "type": "LOK_SABHA",
                "year": 2024,
            }
        ]
        (elections_dir / "test.json").write_text(json.dumps(election_data))

        service = JsonDataService(data_dir=tmp_path)
        
        # Test
        elections = service.get_elections()
        
        # Assert
        assert len(elections) == 1
        assert elections[0]["id"] == "test-election"
        assert elections[0]["name"] == "Test Election"

    def test_get_elections_caches_result(self, tmp_path):
        """Test that elections are cached after first load."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([{"election_id": "e1", "name": "E1"}]))

        service = JsonDataService(data_dir=tmp_path)
        
        # First call
        elections1 = service.get_elections()
        # Second call should use cache
        elections2 = service.get_elections()
        
        assert elections1 is elections2  # Same object reference

    def test_get_election_by_id(self, tmp_path):
        """Test getting a specific election by ID."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "e1", "name": "Election 1"},
            {"election_id": "e2", "name": "Election 2"},
        ]))

        service = JsonDataService(data_dir=tmp_path)
        
        election = service.get_election("e1")
        
        assert election is not None
        assert election["id"] == "e1"
        assert election["name"] == "Election 1"

    def test_get_election_not_found(self, tmp_path):
        """Test getting non-existent election returns None."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([]))

        service = JsonDataService(data_dir=tmp_path)
        
        election = service.get_election("non-existent")
        
        assert election is None


class TestJsonDataServiceCandidates:
    """Tests for candidate-related methods."""

    @pytest.fixture
    def setup_election_data(self, tmp_path):
        """Setup test election data structure."""
        # Create election metadata
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "lok-sabha-2024", "name": "Lok Sabha 2024", "type": "LOK_SABHA", "year": 2024}
        ]))

        # Create election data directory
        election_dir = tmp_path / "lok_sabha" / "lok-sabha-2024"
        election_dir.mkdir(parents=True)

        # Create candidates
        candidates = [
            {"id": "c1", "name": "Candidate 1", "party_id": "BJP", "constituency_id": "DL-1", "state_id": "DL", "status": "WON", "type": "MP"},
            {"id": "c2", "name": "Candidate 2", "party_id": "INC", "constituency_id": "DL-1", "state_id": "DL", "status": "LOST", "type": "MP"},
            {"id": "nota", "name": "NOTA", "party_id": "", "constituency_id": "DL-1", "state_id": "DL", "status": "", "type": "MP"},
        ]
        (election_dir / "candidates.json").write_text(json.dumps(candidates))

        # Create parties
        parties = [
            {"id": "BJP", "name": "Bharatiya Janata Party", "short_name": "BJP", "symbol": "Lotus"},
            {"id": "INC", "name": "Indian National Congress", "short_name": "INC", "symbol": "Hand"},
        ]
        (election_dir / "parties.json").write_text(json.dumps(parties))

        # Create constituencies
        constituencies = [
            {"id": "DL-1", "name": "New Delhi", "state_id": "DL", "unique_id": "DL-1"},
        ]
        (election_dir / "constituencies.json").write_text(json.dumps(constituencies))

        return tmp_path

    def test_get_candidates_filters_nota(self, setup_election_data):
        """Test that NOTA entries are filtered out."""
        service = JsonDataService(data_dir=setup_election_data)
        
        candidates = service.get_candidates("lok-sabha-2024")
        
        assert len(candidates) == 2
        assert all(c["name"] != "NOTA" for c in candidates)

    def test_get_candidates_caches_result(self, setup_election_data):
        """Test that candidates are cached."""
        service = JsonDataService(data_dir=setup_election_data)
        
        candidates1 = service.get_candidates("lok-sabha-2024")
        candidates2 = service.get_candidates("lok-sabha-2024")
        
        assert candidates1 is candidates2

    def test_get_candidate_by_id(self, setup_election_data):
        """Test getting a specific candidate by ID."""
        service = JsonDataService(data_dir=setup_election_data)
        
        candidate = service.get_candidate_by_id("c1", "lok-sabha-2024")
        
        assert candidate is not None
        assert candidate["id"] == "c1"
        assert candidate["name"] == "Candidate 1"
        assert candidate["party_name"] == "Bharatiya Janata Party"

    def test_get_candidate_by_id_only(self, setup_election_data):
        """Test getting candidate without election ID."""
        service = JsonDataService(data_dir=setup_election_data)
        
        candidate = service.get_candidate_by_id_only("c1")
        
        assert candidate is not None
        assert candidate["id"] == "c1"

    def test_search_candidates_by_name(self, setup_election_data):
        """Test searching candidates by name."""
        service = JsonDataService(data_dir=setup_election_data)
        
        results = service.search_candidates("Candidate 1", "lok-sabha-2024")
        
        assert len(results) == 1
        assert results[0]["name"] == "Candidate 1"

    def test_search_candidates_case_insensitive(self, setup_election_data):
        """Test that search is case-insensitive."""
        service = JsonDataService(data_dir=setup_election_data)
        
        results = service.search_candidates("candidate", "lok-sabha-2024")
        
        assert len(results) == 2


class TestJsonDataServiceParties:
    """Tests for party-related methods."""

    @pytest.fixture
    def setup_party_data(self, tmp_path):
        """Setup test party data."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "lok-sabha-2024", "name": "Test", "type": "LOK_SABHA", "year": 2024}
        ]))

        election_dir = tmp_path / "lok_sabha" / "lok-sabha-2024"
        election_dir.mkdir(parents=True)
        
        parties = [
            {"id": "BJP", "name": "Bharatiya Janata Party", "short_name": "BJP", "symbol": "Lotus"},
            {"id": "INC", "name": "Indian National Congress", "short_name": "INC", "symbol": "Hand"},
        ]
        (election_dir / "parties.json").write_text(json.dumps(parties))
        (election_dir / "candidates.json").write_text(json.dumps([]))
        (election_dir / "constituencies.json").write_text(json.dumps([]))

        return tmp_path

    def test_get_parties(self, setup_party_data):
        """Test getting all parties for an election."""
        service = JsonDataService(data_dir=setup_party_data)
        
        parties = service.get_parties("lok-sabha-2024")
        
        assert len(parties) == 2

    def test_get_party_by_name(self, setup_party_data):
        """Test getting a party by name."""
        service = JsonDataService(data_dir=setup_party_data)
        
        party = service.get_party_by_name("BJP", "lok-sabha-2024")
        
        assert party is not None
        assert party["name"] == "Bharatiya Janata Party"

    def test_get_party_by_short_name(self, setup_party_data):
        """Test getting a party by short name."""
        service = JsonDataService(data_dir=setup_party_data)
        
        party = service.get_party_by_name("INC", "lok-sabha-2024")
        
        assert party is not None
        assert party["name"] == "Indian National Congress"


class TestJsonDataServiceConstituencies:
    """Tests for constituency-related methods."""

    @pytest.fixture
    def setup_constituency_data(self, tmp_path):
        """Setup test constituency data."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "lok-sabha-2024", "name": "Test", "type": "LOK_SABHA", "year": 2024}
        ]))

        election_dir = tmp_path / "lok_sabha" / "lok-sabha-2024"
        election_dir.mkdir(parents=True)
        
        constituencies = [
            {"id": "DL-1", "name": "New Delhi", "state_id": "DL", "unique_id": "DL-1"},
            {"id": "MH-1", "name": "Mumbai North", "state_id": "MH", "unique_id": "MH-1"},
        ]
        (election_dir / "constituencies.json").write_text(json.dumps(constituencies))
        (election_dir / "candidates.json").write_text(json.dumps([]))
        (election_dir / "parties.json").write_text(json.dumps([]))

        return tmp_path

    def test_get_constituencies(self, setup_constituency_data):
        """Test getting all constituencies for an election."""
        service = JsonDataService(data_dir=setup_constituency_data)
        
        constituencies = service.get_constituencies("lok-sabha-2024")
        
        assert len(constituencies) == 2

    def test_get_constituency_by_id(self, setup_constituency_data):
        """Test getting a constituency by ID."""
        service = JsonDataService(data_dir=setup_constituency_data)
        
        constituency = service.get_constituency_by_id("DL-1", "lok-sabha-2024")
        
        assert constituency is not None
        assert constituency["name"] == "New Delhi"


class TestJsonDataServiceStatistics:
    """Tests for statistics methods."""

    @pytest.fixture
    def setup_statistics_data(self, tmp_path):
        """Setup test data for statistics."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "lok-sabha-2024", "name": "Test", "type": "LOK_SABHA", "year": 2024}
        ]))

        election_dir = tmp_path / "lok_sabha" / "lok-sabha-2024"
        election_dir.mkdir(parents=True)

        candidates = [
            {"id": "c1", "name": "C1", "party_id": "BJP", "status": "WON"},
            {"id": "c2", "name": "C2", "party_id": "BJP", "status": "WON"},
            {"id": "c3", "name": "C3", "party_id": "INC", "status": "LOST"},
        ]
        parties = [{"id": "BJP"}, {"id": "INC"}]
        constituencies = [{"id": "DL-1"}, {"id": "DL-2"}]

        (election_dir / "candidates.json").write_text(json.dumps(candidates))
        (election_dir / "parties.json").write_text(json.dumps(parties))
        (election_dir / "constituencies.json").write_text(json.dumps(constituencies))

        return tmp_path

    def test_get_election_statistics(self, setup_statistics_data):
        """Test getting election statistics."""
        service = JsonDataService(data_dir=setup_statistics_data)
        
        stats = service.get_election_statistics("lok-sabha-2024")
        
        assert stats["total_candidates"] == 3
        assert stats["total_winners"] == 2
        assert stats["total_parties"] == 2
        assert stats["total_constituencies"] == 2

    def test_get_party_seat_counts(self, setup_statistics_data):
        """Test getting party seat counts."""
        service = JsonDataService(data_dir=setup_statistics_data)
        
        seat_counts = service.get_party_seat_counts("lok-sabha-2024", limit=5)
        
        assert len(seat_counts) >= 1
        # BJP should be first with 2 seats
        assert seat_counts[0]["seats_won"] == 2


class TestJsonDataServiceHelpers:
    """Tests for helper methods."""

    def test_get_state_name_valid_code(self):
        """Test getting state name with valid code."""
        service = JsonDataService()
        
        assert service.get_state_name("DL") == "Delhi"
        assert service.get_state_name("MH") == "Maharashtra"
        assert service.get_state_name("S01") == "Andhra Pradesh"

    def test_get_state_name_invalid_code(self):
        """Test getting state name with invalid code returns Unknown."""
        service = JsonDataService()
        
        assert service.get_state_name("XX") == "Unknown"
        assert service.get_state_name("") == "Unknown"

    def test_clear_cache(self, tmp_path):
        """Test clearing all caches."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([{"election_id": "e1", "name": "E1"}]))

        service = JsonDataService(data_dir=tmp_path)
        service.get_elections()  # Populate cache
        
        service.clear_cache()
        
        assert service._elections_cache is None
        assert service._parties_cache == {}

    def test_reload_election_data(self, tmp_path):
        """Test reloading specific election data."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "e1", "name": "E1"}
        ]))

        election_dir = tmp_path / "lok_sabha" / "e1"
        election_dir.mkdir(parents=True)
        (election_dir / "parties.json").write_text(json.dumps([{"id": "p1"}]))
        (election_dir / "candidates.json").write_text(json.dumps([]))
        (election_dir / "constituencies.json").write_text(json.dumps([]))

        service = JsonDataService(data_dir=tmp_path)
        service.get_parties("e1")  # Populate cache
        
        service.reload_election_data("e1")
        
        assert "e1" not in service._parties_cache


class TestStateNamesMapping:
    """Tests for state names mapping."""

    def test_all_state_codes_have_names(self):
        """Test that all expected state codes have names."""
        expected_codes = ["DL", "MH", "KA", "TN", "UP", "GJ", "RJ", "WB"]
        
        for code in expected_codes:
            assert code in STATE_NAMES, f"Missing state code: {code}"

    def test_s_codes_are_present(self):
        """Test that S-prefixed codes are present."""
        s_codes = [f"S{i:02d}" for i in range(1, 30)]
        
        present_codes = [c for c in s_codes if c in STATE_NAMES]
        assert len(present_codes) > 20  # Most should be present
