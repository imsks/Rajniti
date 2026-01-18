"""
Unit tests for DbDataService.

Tests cover data access operations for elections, candidates, parties, and constituencies.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.services.db_data_service import DbDataService


@pytest.fixture
def data_service():
    """Create a DbDataService instance."""
    service = DbDataService()
    service._elections_cache = None  # Reset cache for each test
    return service


@pytest.mark.unit
class TestGetElections:
    """Tests for get_elections method."""

    def test_get_all_elections(self, data_service, sample_election_data):
        """Test getting all elections."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            mock_election = Mock()
            mock_election.id = sample_election_data['id']
            mock_election.name = sample_election_data['name']
            mock_election.type = sample_election_data['type']
            mock_election.year = sample_election_data['year']
            
            with patch('app.database.models.Election.get_all', return_value=[mock_election]):
                elections = data_service.get_elections()
                
                assert len(elections) == 1
                assert elections[0]['id'] == sample_election_data['id']

    def test_elections_are_cached(self, data_service, sample_election_data):
        """Test that elections are cached after first call."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            mock_election = Mock()
            mock_election.id = sample_election_data['id']
            mock_election.name = sample_election_data['name']
            mock_election.type = sample_election_data['type']
            mock_election.year = sample_election_data['year']
            
            with patch('app.database.models.Election.get_all', return_value=[mock_election]) as mock_get:
                # First call
                data_service.get_elections()
                # Second call should use cache
                data_service.get_elections()
                
                # get_all should only be called once due to caching
                assert mock_get.call_count == 1


@pytest.mark.unit
class TestGetElection:
    """Tests for get_election method."""

    def test_get_election_found(self, data_service, sample_election_data):
        """Test getting election by ID when found."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            mock_election = Mock()
            mock_election.id = sample_election_data['id']
            mock_election.name = sample_election_data['name']
            mock_election.type = sample_election_data['type']
            mock_election.year = sample_election_data['year']
            
            with patch('app.database.models.Election.get_by_id', return_value=mock_election):
                election = data_service.get_election('lok-sabha-2024')
                
                assert election is not None
                assert election['id'] == 'lok-sabha-2024'

    def test_get_election_not_found(self, data_service):
        """Test getting election by ID when not found."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            with patch('app.database.models.Election.get_by_id', return_value=None):
                election = data_service.get_election('nonexistent')
                
                assert election is None


@pytest.mark.unit
class TestGetCandidates:
    """Tests for get_candidates method."""

    def test_get_candidates_election_not_found(self, data_service):
        """Test getting candidates when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            candidates = data_service.get_candidates('nonexistent')
            assert candidates == []

    def test_get_candidates_empty(self, data_service, sample_election_data):
        """Test getting candidates when none exist."""
        with patch.object(data_service, 'get_election', return_value=sample_election_data):
            with patch('app.services.db_data_service.get_db_session') as mock_ctx:
                mock_session = Mock()
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                with patch('app.database.models.Candidate.get_all', return_value=[]):
                    candidates = data_service.get_candidates('lok-sabha-2024')
                    assert candidates == []


@pytest.mark.unit
class TestGetParties:
    """Tests for get_parties method."""

    def test_get_parties_election_not_found(self, data_service):
        """Test getting parties when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            parties = data_service.get_parties('nonexistent')
            assert parties == []

    def test_get_parties_success(self, data_service, sample_election_data, sample_party_data):
        """Test getting parties successfully."""
        with patch.object(data_service, 'get_election', return_value=sample_election_data):
            with patch('app.services.db_data_service.get_db_session') as mock_ctx:
                mock_session = Mock()
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                mock_party = Mock()
                mock_party.id = sample_party_data['id']
                mock_party.name = sample_party_data['name']
                mock_party.short_name = sample_party_data['short_name']
                mock_party.symbol = sample_party_data['symbol']
                
                with patch('app.database.models.Party.get_all', return_value=[mock_party]):
                    parties = data_service.get_parties('lok-sabha-2024')
                    
                    assert len(parties) == 1
                    assert parties[0]['id'] == 'BJP'


@pytest.mark.unit
class TestGetConstituencies:
    """Tests for get_constituencies method."""

    def test_get_constituencies_election_not_found(self, data_service):
        """Test getting constituencies when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            constituencies = data_service.get_constituencies('nonexistent')
            assert constituencies == []

    def test_get_constituencies_success(self, data_service, sample_election_data, sample_constituency_data):
        """Test getting constituencies successfully."""
        with patch.object(data_service, 'get_election', return_value=sample_election_data):
            with patch('app.services.db_data_service.get_db_session') as mock_ctx:
                mock_session = Mock()
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                mock_constituency = Mock()
                mock_constituency.id = sample_constituency_data['id']
                mock_constituency.name = sample_constituency_data['name']
                mock_constituency.state_id = sample_constituency_data['state_id']
                
                with patch('app.database.models.Constituency.get_all', return_value=[mock_constituency]):
                    constituencies = data_service.get_constituencies('lok-sabha-2024')
                    
                    assert len(constituencies) == 1
                    assert constituencies[0]['id'] == 'DL-1'


@pytest.mark.unit
class TestSearchCandidates:
    """Tests for search_candidates method."""

    def test_search_candidates_election_not_found(self, data_service):
        """Test searching candidates when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            candidates = data_service.search_candidates('test', 'nonexistent')
            assert candidates == []


@pytest.mark.unit
class TestGetCandidateById:
    """Tests for get_candidate_by_id method."""

    def test_get_candidate_election_not_found(self, data_service):
        """Test getting candidate when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            candidate = data_service.get_candidate_by_id('candidate-123', 'nonexistent')
            assert candidate is None

    def test_get_candidate_not_found(self, data_service, sample_election_data):
        """Test getting candidate when candidate not found."""
        with patch.object(data_service, 'get_election', return_value=sample_election_data):
            with patch('app.services.db_data_service.get_db_session') as mock_ctx:
                mock_session = Mock()
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                with patch('app.database.models.Candidate.get_by_id', return_value=None):
                    candidate = data_service.get_candidate_by_id('nonexistent', 'lok-sabha-2024')
                    assert candidate is None


@pytest.mark.unit
class TestGetCandidateByIdOnly:
    """Tests for get_candidate_by_id_only method."""

    def test_get_candidate_by_id_only_not_found(self, data_service):
        """Test getting candidate by ID only when not found."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            with patch('app.database.models.Candidate.get_by_id', return_value=None):
                candidate = data_service.get_candidate_by_id_only('nonexistent')
                assert candidate is None


@pytest.mark.unit
class TestGetPartyByName:
    """Tests for get_party_by_name method."""

    def test_get_party_election_not_found(self, data_service):
        """Test getting party when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            party = data_service.get_party_by_name('BJP', 'nonexistent')
            assert party is None

    def test_get_party_not_found(self, data_service, sample_election_data):
        """Test getting party when party not found."""
        with patch.object(data_service, 'get_election', return_value=sample_election_data):
            with patch('app.services.db_data_service.get_db_session') as mock_ctx:
                mock_session = Mock()
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                with patch('app.database.models.Party.get_by_name', return_value=None):
                    party = data_service.get_party_by_name('NONEXISTENT', 'lok-sabha-2024')
                    assert party is None


@pytest.mark.unit
class TestGetConstituencyById:
    """Tests for get_constituency_by_id method."""

    def test_get_constituency_election_not_found(self, data_service):
        """Test getting constituency when election not found."""
        with patch.object(data_service, 'get_election', return_value=None):
            constituency = data_service.get_constituency_by_id('DL-1', 'nonexistent')
            assert constituency is None


@pytest.mark.unit
class TestGetElectionStatistics:
    """Tests for get_election_statistics method."""

    def test_get_statistics(self, data_service):
        """Test getting election statistics."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            # Mock the count queries
            mock_session.query.return_value.scalar.return_value = 100
            mock_session.query.return_value.filter.return_value.scalar.return_value = 50
            
            stats = data_service.get_election_statistics('lok-sabha-2024')
            
            assert 'total_candidates' in stats
            assert 'total_winners' in stats
            assert 'total_parties' in stats
            assert 'total_constituencies' in stats


@pytest.mark.unit
class TestGetPartySeatCounts:
    """Tests for get_party_seat_counts method."""

    def test_get_party_seat_counts(self, data_service, sample_party_data):
        """Test getting party seat counts."""
        with patch('app.services.db_data_service.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            # Mock the group by query for first query (party_seats)
            mock_query1 = Mock()
            mock_query1.filter.return_value = mock_query1
            mock_query1.group_by.return_value = mock_query1
            mock_query1.order_by.return_value = mock_query1
            mock_query1.limit.return_value = mock_query1
            # Return actual tuples, not Mock objects
            mock_query1.all.return_value = [('BJP', 240)]
            
            # Mock party lookup (second query)
            mock_party = Mock()
            mock_party.id = 'BJP'
            mock_party.name = sample_party_data['name']
            mock_party.short_name = sample_party_data['short_name']
            
            mock_query2 = Mock()
            mock_query2.filter.return_value = mock_query2
            mock_query2.all.return_value = [mock_party]
            
            # Setup query to return different mocks based on call order
            mock_session.query.side_effect = [mock_query1, mock_query2]
            
            result = data_service.get_party_seat_counts('lok-sabha-2024', limit=5)
            
            assert isinstance(result, list)
