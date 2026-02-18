from __future__ import annotations

from typing import Any, Dict


class PoliticianPrompts:
    """Central place for politician-related prompt builders."""

    @staticmethod
    def education(politician: Dict[str, Any]) -> str:
        """Build a strict JSON prompt for education extraction."""
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")

        return (
            "You are extracting structured data about an Indian politician.\n"
            "Return ONLY valid JSON array. Each item format:\n"
            "[{\"qualification\": \"HIGH_SCHOOL|DIPLOMA|BACHELOR|MASTER|DOCTORATE|PROFESSIONAL|OTHERS|null\", "
            "\"institution\": \"string|null\", \"year_completed\": number|null}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return []"
        )

    @staticmethod
    def political_background(politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting a politician's political background.\n"
            "Return ONLY a valid JSON object matching this shape:\n"
            '{ "elections": [ { "year": 2024, "type": "MP|MLA", "state": "string", '
            '"constituency": "string", "party": "string", "status": "WINNER|LOSER|INCUMBENT" } ], '
            '"summary": "short textual summary or null" }\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return {\"elections\": [], \"summary\": null}"
        )

