"""
Enrichment Agent — fill empty Politician fields using an LLM.

Works directly with the Politician schema (mp.json / mla.json).
After enrichment, the updated record is persisted immediately.

Enrichable fields:
  - education
  - family_background
  - criminal_records
  - social_media
  - contact
  - political_background.summary

Usage:
    python scripts/enrich_politicians.py --type MP --batch-size 10
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

from app.services.politician_service import PoliticianService
from app.services.llm_cache import get_cache

logger = logging.getLogger(__name__)

# Fields that the LLM should try to fill, mapped to their Politician schema keys.
_ENRICHABLE_FIELDS = {
    "education": "education",
    "family_background": "family_background",
    "criminal_records": "criminal_records",
    "social_media": "social_media",
    "contact": "contact",
    "political_summary": "political_background",
}


class EnrichmentAgent:
    """
    Enrich politicians by fetching missing fields via LLM.

    Features:
    - Works with new Politician schema (not old candidate model)
    - Batch LLM query (one call per politician, all missing fields)
    - In-memory caching to avoid repeat calls
    - Incremental save (each politician persisted immediately)
    - Optional vector DB sync after enrichment
    """

    def __init__(
        self,
        politician_service: Optional[PoliticianService] = None,
        llm_provider: Optional[str] = None,
        enable_cache: bool = True,
        cache_ttl_hours: int = 24,
    ) -> None:
        self.pol_service = politician_service or PoliticianService()
        self.cache = get_cache(ttl_hours=cache_ttl_hours) if enable_cache else None

        # Lazy import so the agent works even without LLM keys configured
        from app.services.llm_service import get_llm_service

        self.llm = get_llm_service(provider=llm_provider)
        logger.info("EnrichmentAgent initialized (provider=%s)", llm_provider or "default")

    # ── Detect what's missing ─────────────────────────────────────────────

    @staticmethod
    def _is_empty(val: Any) -> bool:
        if val is None:
            return True
        if isinstance(val, (list, dict)) and len(val) == 0:
            return True
        if isinstance(val, str) and val.strip() == "":
            return True
        return False

    def find_missing_fields(self, politician: Dict[str, Any]) -> List[str]:
        """Return list of enrichable field keys that are empty/missing."""
        missing: List[str] = []

        if self._is_empty(politician.get("education")):
            missing.append("education")
        if self._is_empty(politician.get("family_background")):
            missing.append("family_background")
        if self._is_empty(politician.get("criminal_records")):
            missing.append("criminal_records")
        if self._is_empty(politician.get("social_media")):
            missing.append("social_media")
        if self._is_empty(politician.get("contact")):
            missing.append("contact")

        bg = politician.get("political_background") or {}
        if self._is_empty(bg.get("summary")):
            missing.append("political_summary")

        return missing

    def find_politicians_needing_enrichment(
        self,
        election_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find politicians with at least one empty enrichable field."""
        types = [election_type] if election_type else ["MP", "MLA"]
        results: List[Dict[str, Any]] = []
        for etype in types:
            for p in self.pol_service.get_all(etype):  # type: ignore[arg-type]
                if self.find_missing_fields(p):
                    results.append(p)
                    if len(results) >= limit:
                        return results
        return results

    # ── LLM query construction ────────────────────────────────────────────

    def _build_prompt(self, politician: Dict[str, Any], missing: List[str]) -> str:
        """Build a single LLM prompt requesting all missing fields."""
        name = politician.get("name", "Unknown")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")

        sections: List[str] = []

        formats = {
            "education": '{"qualification": "...", "institution": "...", "year_completed": 2020}',
            "family_background": '[{"name": "...", "relation": "Father/Spouse/..."}]',
            "criminal_records": '[{"name": "...", "type": "MURDER/RAPE/KIDNAPPING/THEFT/CORRUPTION/ECONOMIC/OTHERS", "year": 2020}]',
            "social_media": '{"twitter": "url", "facebook": "url", "instagram": "url", "website": "url"}',
            "contact": '{"email": "...", "phone": "...", "address": "..."}',
            "political_summary": '"A brief 2-3 sentence summary of their political career."',
        }

        for field in missing:
            sections.append(f"  - {field}: {formats.get(field, '...')}")

        return (
            f"Provide the following information about Indian politician "
            f"{name}, {ptype} from {constituency}, {state}.\n\n"
            f"Return a JSON object with these keys:\n"
            + "\n".join(sections)
            + "\n\n"
            "Use reliable sources (MyNeta.info, official records). "
            "If data is not available, use null for that key. "
            "Return ONLY valid JSON — no markdown, no code blocks, no extra text."
        )

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract a JSON object from LLM response text."""
        try:
            # Strip markdown code fences
            match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1)
            text = text.strip()

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

            # Fallback: find the outermost { ... }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
        except Exception:
            pass
        return None

    # ── Enrich a single politician ────────────────────────────────────────

    def enrich_one(
        self,
        politician: Dict[str, Any],
        *,
        delay: float = 1.0,
    ) -> Dict[str, bool]:
        """
        Enrich a single politician with LLM data.

        Returns a dict of field → was_enriched.
        """
        missing = self.find_missing_fields(politician)
        status = {f: False for f in _ENRICHABLE_FIELDS}

        # Mark already-present fields as done
        for f in _ENRICHABLE_FIELDS:
            if f not in missing:
                status[f] = True

        if not missing:
            logger.info("  ✓ %s — all fields present", politician.get("name"))
            return status

        prompt = self._build_prompt(politician, missing)

        # Check cache
        response_text: Optional[str] = None
        if self.cache:
            cached = self.cache.get(prompt)
            if cached:
                response_text = cached.get("answer", "")

        if response_text is None:
            result = self.llm.search_india(prompt)
            if result.get("error"):
                logger.error("  ✗ LLM error for %s: %s", politician.get("name"), result["error"])
                return status
            response_text = result.get("answer", "") or ""
            if self.cache:
                self.cache.set(prompt, result)

        parsed = self._extract_json(response_text)
        if not parsed:
            logger.warning("  ✗ Could not parse LLM JSON for %s", politician.get("name"))
            return status

        # Apply fields
        updates: Dict[str, Any] = {}
        for field in missing:
            value = parsed.get(field)
            if field == "political_summary":
                if value and isinstance(value, str):
                    bg = politician.get("political_background") or {}
                    bg["summary"] = value
                    updates["political_background"] = bg
                    status["political_summary"] = True
            elif value is not None:
                updates[field] = value
                status[field] = True

        if updates:
            self.pol_service.update_politician(politician["id"], updates)
            logger.info("  ✓ Enriched %s — updated %s", politician.get("name"), list(updates.keys()))

        time.sleep(delay)
        return status

    # ── Batch run ─────────────────────────────────────────────────────────

    def run(
        self,
        election_type: Optional[str] = None,
        batch_size: int = 10,
        delay: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Enrich a batch of politicians.

        Returns summary stats.
        """
        candidates = self.find_politicians_needing_enrichment(
            election_type=election_type, limit=batch_size
        )
        logger.info("Found %d politicians needing enrichment", len(candidates))

        stats = {"total": len(candidates), "enriched": 0, "partial": 0, "failed": 0}

        for i, pol in enumerate(candidates, 1):
            logger.info("[%d/%d] %s (%s)", i, len(candidates), pol.get("name"), pol.get("id"))
            result = self.enrich_one(pol, delay=delay)
            enriched_count = sum(1 for v in result.values() if v)
            total_fields = len(result)

            if enriched_count == total_fields:
                stats["enriched"] += 1
            elif enriched_count > 0:
                stats["partial"] += 1
            else:
                stats["failed"] += 1

        logger.info("Enrichment done. %s", stats)
        return stats
