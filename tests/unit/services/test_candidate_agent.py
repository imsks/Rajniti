import json

import pytest

from app.schemas.candidate_data import CandidateDetailedProfile
from app.services.candidate_agent import CandidateAgent


class FakeSearchService:
    def __init__(self, answer_text: str):
        self._answer_text = answer_text

    def search_india(self, query: str, region=None, city=None):  # noqa: ANN001
        return {"answer": self._answer_text, "error": None}


def test_extract_json_from_response_parses_plain_json():
    agent = CandidateAgent(enable_cache=False, enable_vector_db=False, search_service=FakeSearchService("{}"))
    parsed = agent._extract_json_from_response('{"a": 1, "b": [2, 3]}')
    assert parsed == {"a": 1, "b": [2, 3]}


def test_extract_json_from_response_parses_fenced_json():
    agent = CandidateAgent(enable_cache=False, enable_vector_db=False, search_service=FakeSearchService("{}"))
    parsed = agent._extract_json_from_response(
        "Here you go:\n```json\n{\"x\": true, \"y\": [\"a\"]}\n```\nThanks!"
    )
    assert parsed == {"x": True, "y": ["a"]}


def test_extract_json_from_response_returns_none_on_garbage():
    agent = CandidateAgent(enable_cache=False, enable_vector_db=False, search_service=FakeSearchService("{}"))
    assert agent._extract_json_from_response("not-json at all") is None


def test_populate_candidate_data_validates_and_writes_expected_types():
    answer = json.dumps(
        {
            "education": [
                {"year": "2000", "college": "Demo University", "stream": "Arts", "other_details": "N/A"}
            ],
            "political": [
                {
                    "party": "Demo Party",
                    "constituency": "Demo Constituency",
                    "election_year": "2019",
                    "position": "MP",
                    "result": "WON",
                }
            ],
            "family": [{"name": "Demo Relative", "profession": "Service", "relation": "Father", "age": "60"}],
            "assets": [{"type": "CASH", "amount": 1000.0, "description": "Demo", "owned_by": "SELF"}],
            "liabilities": [{"type": "LOAN", "amount": 500.0, "description": "Demo", "owned_by": "SELF"}],
            "crime_cases": [
                {
                    "fir_no": "0",
                    "police_station": "Demo PS",
                    "sections_applied": ["IPC 420"],
                    "charges_framed": False,
                    "description": "Demo",
                }
            ],
        }
    )

    agent = CandidateAgent(
        enable_cache=False,
        enable_vector_db=False,
        search_service=FakeSearchService(answer),
    )

    candidate = {
        "id": "c-1",
        "name": "Test Candidate",
        "constituency_id": "DL-1",
        # All detailed fields missing so agent should fetch everything
        "education_background": None,
        "political_background": None,
        "family_background": None,
        "assets": None,
        "liabilities": None,
        "crime_cases": None,
    }

    status = agent.populate_candidate_data(candidate, election_id="lok-sabha-2024", delay_between_requests=0)

    assert status == {
        "education": True,
        "political": True,
        "family": True,
        "assets": True,
        "liabilities": True,
        "crime_cases": True,
    }

    # Validate the populated structure via the Pydantic profile (type/shape checks)
    profile = CandidateDetailedProfile(
        education_background=candidate["education_background"],
        political_background=candidate["political_background"],
        family_background=candidate["family_background"],
        assets=candidate["assets"],
        liabilities=candidate["liabilities"],
        crime_cases=candidate["crime_cases"],
    )
    assert len(profile.education_background) == 1
    assert profile.assets[0].amount == 1000.0
    assert profile.crime_cases[0].charges_framed is False
    assert profile.crime_cases[0].sections_applied == ["IPC 420"]


def test_populate_candidate_data_skips_invalid_items_instead_of_crashing():
    # Invalid: education year not 4-digit, assets type invalid, political party too short
    answer = json.dumps(
        {
            "education": [{"year": "20", "college": "X", "stream": "Y"}],
            "political": [{"party": "A", "election_year": "2019", "result": "WON"}],
            "family": [{"relation": "Father"}],  # valid minimal (relation is required)
            "assets": [{"type": "CURRENCY", "amount": 10}],
            "liabilities": [{"type": "LOAN", "amount": 1}],
            "crime_cases": [{"charges_framed": True, "sections_applied": ["IPC 1"]}],
        }
    )

    agent = CandidateAgent(
        enable_cache=False,
        enable_vector_db=False,
        search_service=FakeSearchService(answer),
    )

    candidate = {
        "id": "c-2",
        "name": "Test Candidate 2",
        "education_background": None,
        "political_background": None,
        "family_background": None,
        "assets": None,
        "liabilities": None,
        "crime_cases": None,
    }

    status = agent.populate_candidate_data(candidate, election_id="lok-sabha-2024", delay_between_requests=0)

    # Family, liabilities, crime_cases should validate; education, political, assets should be rejected
    assert status["family"] is True
    assert status["liabilities"] is True
    assert status["crime_cases"] is True
    assert status["education"] is False
    assert status["political"] is False
    assert status["assets"] is False

