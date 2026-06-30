"""Regression tests for political_background prompt status enum values.

The elections-only fallback prompt previously instructed the LLM to return
``"status": "WINNER | LOSER | INCUMBENT"``, but ``StatusEnum`` only accepts
``WON | LOST | CONTESTED``. The mismatch caused the fallback path to silently
fail Pydantic validation. These tests lock the prompts to the correct enum.
"""

from app.prompts.politician_prompts import PoliticianPrompts
from app.schemas.types import StatusEnum


POLITICIAN = {
    "name": "Test Politician",
    "state": "Bihar",
    "constituency": "Test AC",
    "type": "MLA",
}


def _expected_status_fragment() -> str:
    return "|".join(s.value for s in StatusEnum)


def test_political_background_prompt_uses_status_enum_values() -> None:
    prompt = PoliticianPrompts.political_background(POLITICIAN)
    assert _expected_status_fragment() in prompt
    for invalid in ("WINNER", "LOSER", "INCUMBENT"):
        assert invalid not in prompt


def test_political_background_elections_only_prompt_uses_status_enum_values() -> None:
    prompt = PoliticianPrompts.political_background_elections_only(POLITICIAN)
    assert _expected_status_fragment() in prompt
    for invalid in ("WINNER", "LOSER", "INCUMBENT"):
        assert invalid not in prompt
