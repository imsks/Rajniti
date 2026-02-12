"""
Politician Service — read / search / filter politicians from mp.json & mla.json.

This is the single data-access layer for the Politician model.
All controllers and other services go through here.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set
from difflib import SequenceMatcher

from app.schemas.politician import Politician
from app.core.exceptions import NotFoundError, ValidationError, DatabaseError
from app.core.cache import cached, invalidate_cache

logger = logging.getLogger(__name__)

ElectionType = Literal["MP", "MLA"]

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class PoliticianService:
    """
    Read-oriented service over ``mp.json`` and ``mla.json``.

    Caches data in memory after first load.  Call ``reload()`` to refresh.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self._data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    # ── private helpers ───────────────────────────────────────────────────

    def _path(self, election_type: ElectionType) -> Path:
        return self._data_dir / f"{election_type.lower()}.json"

    @cached(ttl=600, key_prefix='politician_data')  # Cache for 10 minutes
    def _load(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        if election_type in self._cache:
            return self._cache[election_type]

        fp = self._path(election_type)
        if not fp.exists():
            logger.warning("File not found: %s", fp)
            self._cache[election_type] = []
            return []

        try:
            with open(fp, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            records = data if isinstance(data, list) else []
            self._cache[election_type] = records
            logger.info("Loaded %d %ss from %s", len(records), election_type, fp)
            return records
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in %s: %s", fp, exc)
            raise DatabaseError(f"Corrupted data file: {fp.name}", operation="load")
        except Exception as exc:
            logger.error("Error loading %s: %s", fp, exc)
            raise DatabaseError(f"Failed to load data: {str(exc)}", operation="load")

    def _save(self, election_type: ElectionType, data: List[Dict[str, Any]]) -> None:
        fp = self._path(election_type)
        fp.parent.mkdir(parents=True, exist_ok=True)
        tmp = fp.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            tmp.replace(fp)
            self._cache[election_type] = data
            # Invalidate cache on data update
            invalidate_cache('politician_data')
            logger.info("Saved %d %ss → %s", len(data), election_type, fp)
        except Exception as exc:
            logger.error("Error saving %s: %s", fp, exc)
            if tmp.exists():
                tmp.unlink()
            raise DatabaseError(f"Failed to save data: {str(exc)}", operation="save")
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.6) -> float:
        """
        Calculate fuzzy match score between two strings.
        
        Args:
            text1: First string
            text2: Second string
            threshold: Minimum similarity threshold (0-1)
        
        Returns:
            Similarity score between 0 and 1
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_relevance(self, politician: Dict[str, Any], query: str) -> float:
        """
        Calculate relevance score for politician based on query.
        Higher scores = better matches.
        
        Scoring:
        - Name match: 10.0
        - Exact party match: 5.0
        - State match: 3.0
        - Constituency match: 3.0
        - Fuzzy name match: 0-8.0
        - Partial text match: 1.0
        """
        score = 0.0
        q = query.lower().strip()
        
        name = politician.get("name", "").lower()
        state = politician.get("state", "").lower()
        constituency = politician.get("constituency", "").lower()
        
        # Exact name match
        if q == name:
            score += 10.0
        # Fuzzy name match
        elif q in name or name in q:
            score += 5.0
        else:
            fuzzy_score = self._fuzzy_match(q, name)
            if fuzzy_score > 0.6:
                score += fuzzy_score * 8.0
        
        # State match
        if q in state:
            score += 3.0
        
        # Constituency match
        if q in constituency:
            score += 3.0
        
        # Party match
        bg = politician.get("political_background", {})
        for election in bg.get("elections", []):
            party = election.get("party", "").lower()
            if q == party:
                score += 5.0
            elif q in party:
                score += 2.0
        
        # General text match
        searchable = f"{name} {state} {constituency}".lower()
        if q in searchable and score == 0:
            score += 1.0
        
        return score

    # ── public API: read ──────────────────────────────────────────────────

    def get_all(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        """Return all politicians of a given type."""
        return self._load(election_type)

    def get_all_politicians(self) -> List[Dict[str, Any]]:
        """Return all MPs + MLAs."""
        return self._load("MP") + self._load("MLA")

    def get_by_id(self, politician_id: str) -> Optional[Dict[str, Any]]:
        """Lookup a politician by ID across both MP and MLA."""
        if not politician_id or not politician_id.strip():
            raise ValidationError("Politician ID cannot be empty", field="politician_id")
        
        for etype in ("MP", "MLA"):
            for p in self._load(etype):
                if p.get("id") == politician_id:
                    return p
        return None

    def search(
        self,
        query: str,
        *,
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        limit: int = 50,
        use_fuzzy: bool = True,
        sort_by_relevance: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search politicians by name, state, constituency, or party.

        All filters are case-insensitive substring matches.
        
        Args:
            query: Search query string
            election_type: Filter by MP or MLA
            state: Filter by state
            party: Filter by party
            limit: Maximum results to return
            use_fuzzy: Enable fuzzy matching for better results
            sort_by_relevance: Sort results by relevance score
        
        Returns:
            List of politician dictionaries
        """
        if not query or len(query.strip()) == 0:
            raise ValidationError("Search query cannot be empty", field="query")
        
        if len(query) > 200:
            raise ValidationError("Query too long (max 200 characters)", field="query")
        
        q = query.lower().strip()
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]

        results: List[tuple[Dict[str, Any], float]] = []
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                # Apply filters
                if state and state.lower() not in p.get("state", "").lower():
                    continue
                if party:
                    party_match = False
                    bg = p.get("political_background", {})
                    for election in bg.get("elections", []):
                        if party.lower() in election.get("party", "").lower():
                            party_match = True
                            break
                    if not party_match:
                        continue

                # Calculate relevance score
                if use_fuzzy:
                    relevance = self._calculate_relevance(p, q)
                    if relevance > 0:
                        results.append((p, relevance))
                else:
                    # Original substring matching
                    searchable = " ".join([
                        p.get("name", ""),
                        p.get("state", ""),
                        p.get("constituency", ""),
                    ]).lower()

                    # Also include party names from elections
                    bg = p.get("political_background", {})
                    for election in bg.get("elections", []):
                        searchable += " " + election.get("party", "").lower()

                    if q in searchable:
                        results.append((p, 1.0))
        
        # Sort by relevance if enabled
        if sort_by_relevance:
            results.sort(key=lambda x: x[1], reverse=True)
        
        # Apply limit and return politicians only
        return [p for p, _ in results[:limit]]

    def get_by_state(
        self, state: str, election_type: Optional[ElectionType] = None
    ) -> List[Dict[str, Any]]:
        """Get all politicians from a specific state."""
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]
        results: List[Dict[str, Any]] = []
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                if state.lower() in p.get("state", "").lower():
                    results.append(p)
        return results

    def get_by_party(
        self, party: str, election_type: Optional[ElectionType] = None
    ) -> List[Dict[str, Any]]:
        """Get all politicians from a specific party."""
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]
        results: List[Dict[str, Any]] = []
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                bg = p.get("political_background", {})
                for election in bg.get("elections", []):
                    if party.lower() in election.get("party", "").lower():
                        results.append(p)
                        break
        return results

    def get_states(self, election_type: Optional[ElectionType] = None) -> List[str]:
        """Return sorted list of unique states."""
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]
        states: Set[str] = set()
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                s = p.get("state", "")
                if s:
                    states.add(s)
        return sorted(states)

    def get_parties(self, election_type: Optional[ElectionType] = None) -> List[str]:
        """Return sorted list of unique party names."""
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]
        parties: Set[str] = set()
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                bg = p.get("political_background", {})
                for election in bg.get("elections", []):
                    party = election.get("party", "")
                    if party:
                        parties.add(party)
        return sorted(parties)

    def stats(self, election_type: Optional[ElectionType] = None) -> Dict[str, Any]:
        """Return summary statistics."""
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]
        total = 0
        by_state: Dict[str, int] = {}
        by_party: Dict[str, int] = {}
        for etype in types:
            records = self._load(etype)  # type: ignore[arg-type]
            total += len(records)
            for p in records:
                s = p.get("state", "Unknown")
                by_state[s] = by_state.get(s, 0) + 1
                bg = p.get("political_background", {})
                for election in bg.get("elections", []):
                    party = election.get("party", "Unknown")
                    by_party[party] = by_party.get(party, 0) + 1

        return {
            "total_politicians": total,
            "total_states": len(by_state),
            "total_parties": len(by_party),
            "top_parties": sorted(by_party.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_states": sorted(by_state.items(), key=lambda x: x[1], reverse=True)[:10],
        }

    # ── public API: write ─────────────────────────────────────────────────

    def update_politician(
        self, politician_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a politician's fields in-place and persist.

        Returns the updated record, or None if not found.
        """
        if not politician_id or not politician_id.strip():
            raise ValidationError("Politician ID cannot be empty", field="politician_id")
        
        if not updates:
            raise ValidationError("No updates provided", field="updates")
        
        for etype in ("MP", "MLA"):
            records = self._load(etype)  # type: ignore[arg-type]
            for i, p in enumerate(records):
                if p.get("id") == politician_id:
                    records[i] = {**p, **updates}
                    self._save(etype, records)  # type: ignore[arg-type]
                    return records[i]
        return None

    # ── cache management ──────────────────────────────────────────────────

    def reload(self, election_type: Optional[ElectionType] = None) -> None:
        """Clear cache so next access re-reads from disk."""
        if election_type:
            self._cache.pop(election_type, None)
        else:
            self._cache.clear()
