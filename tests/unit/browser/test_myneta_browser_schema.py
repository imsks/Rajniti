"""MyNeta browser extract schema — compatible with browser-use extract tool."""

import json

import pytest
from browser_use.tools.extraction.schema_utils import schema_dict_to_pydantic_model

from app.browser.myneta_extract import MyNetaBrowserExtract, to_agent_result


def test_browser_schema_has_no_defs_or_refs() -> None:
    schema = MyNetaBrowserExtract.model_json_schema()
    raw = json.dumps(schema)
    assert "$defs" not in raw
    assert "$ref" not in raw
    assert "anyOf" not in raw


def test_browser_schema_accepted_by_browser_use_utils() -> None:
    schema = MyNetaBrowserExtract.model_json_schema()
    model = schema_dict_to_pydantic_model(schema)
    assert model is not None


def test_to_agent_result_validates_full_payload() -> None:
    profile = "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=1"
    extracted = MyNetaBrowserExtract.model_validate(
        {
            "financial_disclosure": {
                "total_assets_inr": 1000000,
                "total_liabilities_inr": 0,
                "net_worth_inr": 1000000,
                "as_of_election": "Bihar 2025",
                "citation": {"link": profile, "source": "MYNETA"},
            },
            "education": [
                {
                    "qualification": "BACHELOR",
                    "institution": "Test College",
                    "year_completed": 2010,
                    "citation": {"link": profile, "source": "MYNETA"},
                }
            ],
            "criminal_records": [
                {
                    "name": "IPC 420",
                    "type": "ECONOMIC",
                    "citation": {"link": profile, "source": "MYNETA"},
                }
            ],
        }
    )
    result = to_agent_result(extracted)
    assert result.financial_disclosure.total_assets_inr == 1000000
    assert result.education[0].qualification.value == "BACHELOR"


@pytest.mark.parametrize("bad_qualification", ["Graduate", "12th Pass"])
def test_to_agent_result_rejects_invalid_qualification(bad_qualification: str) -> None:
    profile = "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=1"
    extracted = MyNetaBrowserExtract.model_validate(
        {
            "financial_disclosure": {
                "total_assets_inr": 1,
                "citation": {"link": profile, "source": "MYNETA"},
            },
            "education": [
                {
                    "qualification": bad_qualification,
                    "citation": {"link": profile, "source": "MYNETA"},
                }
            ],
        }
    )
    with pytest.raises(Exception):
        to_agent_result(extracted)
