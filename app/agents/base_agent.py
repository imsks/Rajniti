from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.config.agent_config import get_agent_llm

class BaseAgent:
    def __init__(self):
        """Initialize the shared LLM client for all agents."""
        self.llm = get_agent_llm()

    def _run_llm(self, prompt: str) -> str:
        """Send a prompt to the LLM and return plain text output."""
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def _parse_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a JSON object from raw LLM text with a fallback slice."""
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
