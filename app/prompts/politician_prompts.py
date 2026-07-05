from __future__ import annotations

import json
from typing import Any, Dict, Optional

_CITATION_SHAPE = '"citation": {"link": "https://...", "source": "ECI|MYNETA|GOV_WEBSITE|NEWS|OTHERS"}'

_CITATION_RULES = (
    "Every non-empty fact MUST include a real HTTPS citation object "
    + _CITATION_SHAPE
    + ". Prefer primary sources (ECI results, myneta.info affidavits, "
    "official Lok Sabha / state assembly portals, government gazettes) over news. "
    "The URL must directly support the specific fact."
)


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
            '"institution": "string|null", "year_completed": number|null, '
            + _CITATION_SHAPE
            + "}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return [].\n" + _CITATION_RULES
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
            '"constituency": "string", "party": "string", "status": "WON|LOST|CONTESTED", '
            + _CITATION_SHAPE
            + " } ], "
            '"summary": "2-4 sentence narrative biography. Cover: party affiliations over their career, '
              'every constituency contested (with year, result), and current role. '
              'Write in flowing prose — no bullet points. Use title-case name once at the start, '
              'then pronouns. Do NOT pad with generic filler like \'latest available result shows\'. '
              'If genuinely unknown, null.", '
            '"summary_citation": '
            "{ " + _CITATION_SHAPE + " } | null "
            "}\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If summary is null, set summary_citation to null. Otherwise summary_citation is required.\n"
            'If unknown, return {"elections": [], "summary": null, "summary_citation": null}\n'
            + _CITATION_RULES
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
            '"party": "string", "status": "WON|LOST|CONTESTED", '
            + _CITATION_SHAPE
            + "}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return []\n" + _CITATION_RULES
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
            '"linkedin": "url|null", "youtube": "url|null", "website": "url|null", '
            '"social_media_citations": { "twitter": {"link":"url","source":"GOV_WEBSITE"}, ... } }\n'
            "Include one entry in social_media_citations for **each** non-null platform URL, "
            "using a page that verifies the account (official party site, candidate affidavit, "
            "or the platform profile URL itself with source GOV_WEBSITE or OTHERS as appropriate).\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include verified/official links. If all unknown, use all null URLs and {} for "
            "social_media_citations.\n" + _CITATION_RULES
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
            '"photo": "url|null", "social_media": null, ' + _CITATION_SHAPE + "}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include publicly known family members. "
            "If unknown, return []\n" + _CITATION_RULES
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
            '"year": number|null, ' + _CITATION_SHAPE + "}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include publicly reported and documented cases (e.g. election affidavits, "
            "court reporting). Do not speculate. If unknown or none, return []\n"
            + _CITATION_RULES
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
            '{"email": "string|null", "phone": "string|null", "address": "string|null", '
            '"contact_citations": { "email": {"link":"url","source":"GOV_WEBSITE"}, ... } }\n'
            "Include contact_citations entries only for non-null fields; each citation must "
            "support that field (official portal, assembly contact page, etc.).\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "Only include officially published contact details. "
            "If unknown, use all nulls and {} for contact_citations.\n"
            + _CITATION_RULES
        )

    @staticmethod
    def citation_audit(
        politician: Dict[str, Any],
        citation_backlog: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Ask LLM for citation-only patches aligned with existing detail rows.

        ``citation_backlog`` narrows scope to indices/keys that still lack citations
        (merge never overwrites existing citation objects).
        """
        payload = {
            "education": politician.get("education"),
            "political_background": politician.get("political_background"),
            "family_background": politician.get("family_background"),
            "criminal_records": politician.get("criminal_records"),
            "contact": politician.get("contact"),
            "social_media": politician.get("social_media"),
            "performance": politician.get("performance"),
            "type": politician.get("type"),
        }
        raw = json.dumps(payload, ensure_ascii=False, indent=2)
        backlog_block = ""
        if citation_backlog:
            backlog_json = json.dumps(citation_backlog, ensure_ascii=False, indent=2)
            backlog_block = (
                "CITATION_BACKLOG_JSON (YOU MUST ADDRESS ONLY THESE SLOTS; anything already "
                "carrying a citation object in INPUT is OUT OF SCOPE — use null everywhere else):\n"
                "- education_citations / family_citations / criminal_citations: output arrays "
                "with the SAME length as INPUT; ONLY indices listed "
                "(e.g. education_indices) may be citation objects.\n"
                "- elections_indices: same rule for elections_citations vs political_background.elections.\n"
                "- summary_needs_citation true: populate summary_citation only if INPUT has summary text.\n"
                "- contact_keys / social_media_keys / performance_keys: only those keys "
                "in *_citations objects.\n\n"
                f"{backlog_json}\n\n"
            )

        return (
            "You are a fact-checking assistant. Given the following JSON details for ONE "
            "Indian politician, propose **ONLY** source citations. Do NOT change factual text, "
            "party names, dates, or counts — only fill missing citation URLs in backlog slots.\n"
            "The server merges into JSON **only empty citation slots**; it will IGNORE proposals "
            "that would overwrite an existing citation object.\n"
            "Return ONLY valid JSON with this exact shape (use null for array positions "
            "where no citation is needed or unknown):\n"
            "{\n"
            '  "education_citations": [ { "link": "https://...", "source": "ECI" } | null, ... ],\n'
            '  "elections_citations": [ { "link": "...", "source": "ECI" } | null, ... ],\n'
            '  "summary_citation": { "link": "...", "source": "..." } | null,\n'
            '  "family_citations": [ ... ],\n'
            '  "criminal_citations": [ ... ],\n'
            '  "contact_citations": { "email": { ... }, ... },\n'
            '  "social_media_citations": { ... },\n'
            '  "performance_citations": { "attendance": { ... }, "questions": { ... }, '
            '"debates": { ... } },\n'
            '  "issues": [ "optional notes about uncertainty" ]\n'
            "}\n"
            "Rules:\n"
            "- Arrays MUST be parallel to the input arrays (same length); use null for "
            "entries you cannot source.\n"
            "- Omit keys you cannot populate, or use null / {} as appropriate.\n"
            "- source must be one of: ECI, MYNETA, GOV_WEBSITE, NEWS, OTHERS.\n"
            "- performance_citations only if type is MP and performance numbers exist; "
            "prefer Lok Sabha / PRS sources.\n\n" + backlog_block + f"INPUT:\n{raw}\n"
        )
