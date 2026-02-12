from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from app.config.agent_config import get_agent_llm
from app.services.politician_service import PoliticianService

logger = logging.getLogger(__name__)

class PoliticianAgent:
    def __init__(self):
        self.llm = get_agent_llm()
        self.politician_service = PoliticianService()

    def run(self, politician_id: str):
        politician = self.politician_service.get_politician(politician_id)
        return self.llm.invoke(politician)

    def get_politician(self, politician_id: str):
        return self.politician_service.get_by_id(politician_id)

    def _build_education_prompt(self, politician: Dict[str, Any]) -> str:
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")

        return (
            "You are extracting structured data about an Indian politician.\n"
            "Return ONLY valid JSON object with keys:\n"
            "{"
            "\"qualification\": \"HIGH_SCHOOL|DIPLOMA|BACHELOR|MASTER|DOCTORATE|PROFESSIONAL|OTHERS|null\", "
            "\"institution\": \"string|null\", "
            "\"year_completed\": " "number|null"
            "}\n\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, use null."
        )

    def _run_llm(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def _parse_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end])
                except Exception:
                    return None
        return None

    def enrich_education(self, politician_id: str, force: bool = False) -> Dict[str, Any]:
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