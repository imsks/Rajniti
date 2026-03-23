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
            '[{"qualification": "HIGH_SCHOOL|DIPLOMA|BACHELOR|MASTER|DOCTORATE|PROFESSIONAL|OTHERS|null", '
            '"institution": "string|null", "year_completed": number|null}]\n'
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
            '"constituency": "string", "party": "string", "status": "WON|LOST|CONTESTED" } ], '
            '"summary": "short textual summary or null" }\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            'If unknown, return {"elections": [], "summary": null}'
        )

    @staticmethod
    def political_background_elections_only(politician: Dict[str, Any]) -> str:
        """Focused prompt to extract elections array if missing/empty."""
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting ONLY the election history for this politician.\n"
            "Return ONLY a valid JSON array. Each item format:\n"
            '[{ "year": 2024, "type": "MP|MLA", "state": "string", "constituency": "string", '
            '"party": "string", "status": "WON|LOST|CONTESTED" }]\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return []"
        )

    @staticmethod
    def social_media(politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting social media links for an Indian politician.\n"
            "Return ONLY a valid JSON object matching this shape:\n"
            '{"twitter": "url|null", "facebook": "url|null", "instagram": "url|null", '
            '"linkedin": "url|null", "youtube": "url|null", "website": "url|null"}\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include verified/official links. "
            'If unknown, return {"twitter": null, "facebook": null, "instagram": null, '
            '"linkedin": null, "youtube": null, "website": null}'
        )

    @staticmethod
    def family_background(politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting family background for an Indian politician.\n"
            "Return ONLY a valid JSON array. Each item format:\n"
            '[{"name": "string", '
            '"relation": "FATHER|MOTHER|SIBLING|SON|DAUGHTER|WIFE|HUSBAND|OTHERS", '
            '"photo": "url|null", "social_media": null}]\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include publicly known family members. "
            "If unknown, return []"
        )

    @staticmethod
    def criminal_records(politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting criminal records for an Indian politician.\n"
            "Return ONLY a valid JSON array. Each item format:\n"
            '[{"name": "brief case description", '
            '"type": "MURDER|RAPE|KIDNAPPING|THEFT|CORRUPTION|ECONOMIC|OTHERS|null", '
            '"year": number|null}]\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include publicly reported and documented cases. Do not speculate. "
            "If unknown or none, return []"
        )

    @staticmethod
    def contact(politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")
        return (
            "You are extracting contact information for an Indian politician.\n"
            "Return ONLY a valid JSON object matching this shape:\n"
            '{"email": "string|null", "phone": "string|null", "address": "string|null"}\n'
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include officially published contact details. "
            'If unknown, return {"email": null, "phone": null, "address": null}'
        )
