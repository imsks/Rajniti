from __future__ import annotations

import json
from typing import Any, Dict, Optional, TypeVar

from pydantic import TypeAdapter, ValidationError

from app.config.agent_config import get_agent_llm

class BaseAgent:
    def __init__(self):
        """Initialize the shared LLM client for all agents."""
        self.llm = get_agent_llm()

    def _run_llm(self, prompt: str) -> str:
        """Send a prompt to the LLM and return plain text output."""
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def _parse_json_value(self, text: str) -> Optional[Any]:
        """Parse any JSON value (object/array) from raw LLM text."""
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        starts = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
        start = min(starts) if starts else -1
        end_object = text.rfind("}") + 1
        end_array = text.rfind("]") + 1
        end = max(end_object, end_array)

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                return None
        return None

    def _parse_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a JSON object from raw text (backward-compatible helper)."""
        value = self._parse_json_value(text)
        return value if isinstance(value, dict) else None

    def _coerce_to_list(self, value: Any) -> Optional[list[Any]]:
        """Normalize object/array payload into a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]
        return None

    T = TypeVar("T")

    def _validate_with_adapter(
        self, value: Any, adapter: TypeAdapter[T]
    ) -> tuple[Optional[T], Optional[list[dict[str, Any]]]]:
        """Validate arbitrary payload using a provided Pydantic TypeAdapter."""
        try:
            return adapter.validate_python(value), None
        except ValidationError as exc:
            return None, exc.errors()
