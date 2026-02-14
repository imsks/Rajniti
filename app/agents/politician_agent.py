from __future__ import annotations

import logging
from typing import Any, Dict
from app.agents.base_agent import BaseAgent
from app.services.politician_service import PoliticianService

logger = logging.getLogger(__name__)

class PoliticianAgent(BaseAgent):
    def __init__(self):
        """Initialize politician data service and shared agent capabilities."""
        super().__init__()
        self.politician_service = PoliticianService()

    def run(self, politician_id: str, force: bool = False):
        """Run the default politician enrichment workflow."""
        return self.enrich_education(politician_id, force=force)

    def get_politician(self, politician_id: str):
        """Fetch a politician record by id from the JSON data layer."""
        return self.politician_service.get_by_id(politician_id)

    def _build_education_prompt(self, politician: Dict[str, Any]) -> str:
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
            "If unknown, return []"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, use null."
        )

    def enrich_education(self, politician_id: str, force: bool = False) -> Dict[str, Any]:
        """Enrich and persist the education field for one politician."""
        politician = self.get_politician(politician_id)
        if not politician:
            return {"ok": False, "error": "politician_not_found"}

        if politician.get("education") and not force:
            return {"ok": True, "skipped": True, "reason": "already_present"}

        prompt = self._build_education_prompt(politician)
        raw = self._run_llm(prompt)
        parsed = self._parse_json_object(raw)

        if not parsed:
            return {"ok": False, "error": "invalid_llm_json", "raw": raw}

        updates = {"education": parsed}
        updated = self.politician_service.update_politician(politician_id, updates)

        if not updated:
            return {"ok": False, "error": "update_failed"}

        return {"ok": True, "skipped": False, "updated_fields": ["education"]}