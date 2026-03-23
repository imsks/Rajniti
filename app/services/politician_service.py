"""
Politician Service — read / search / filter politicians from mp.json & mla.json.

This is the single data-access layer for the Politician model.
All controllers and other services go through here.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set

from app.core.slugify import slugify, short_id_from_uuid

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
        self._slugs_ensured: bool = False
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._by_slug: Dict[str, Dict[str, Any]] = {}

    # ── slug handling ─────────────────────────────────────────────────

    def _ensure_slugs(self) -> None:
        """
        Ensure each politician record has a `slug` field and build indices.

        Slug rules:
        - baseSlug = slugify(name)
        - if multiple records share the same baseSlug, append `-<shortId>`
        - otherwise baseSlug alone
        """
        if self._slugs_ensured:
            return

        # Load both datasets so duplicates are resolved consistently.
        mp_records = self._load("MP")
        mla_records = self._load("MLA")
        all_records = mp_records + mla_records

        base_counts: Dict[str, int] = {}
        for p in all_records:
            name = (p.get("name") or "").strip()
            base = slugify(name)
            if not base:
                base = "politician"
            base_counts[base] = base_counts.get(base, 0) + 1

        self._by_id = {}
        self._by_slug = {}

        for p in all_records:
            pid = str(p.get("id") or "").strip()
            name = (p.get("name") or "").strip()
            base = slugify(name) or "politician"
            short_id = short_id_from_uuid(pid) or "00000000"

            count = base_counts.get(base, 0)
            expected = base if count <= 1 else f"{base}-{short_id}"

            # If slugify collisions still happen, disambiguate deterministically.
            candidate = expected
            if candidate in self._by_slug and str(self._by_slug[candidate].get("id")) != pid:
                candidate = f"{expected}-{short_id}"

            # Only write slug if missing/empty OR to keep consistency.
            existing = p.get("slug")
            if not isinstance(existing, str) or not existing.strip():
                p["slug"] = candidate
            else:
                # Keep API response consistent with current generation rules.
                p["slug"] = candidate

            if pid:
                self._by_id[pid] = p
            self._by_slug[str(p.get("slug"))] = p

        self._slugs_ensured = True

    # ── private helpers ───────────────────────────────────────────────────

    def _path(self, election_type: ElectionType) -> Path:
        return self._data_dir / f"{election_type.lower()}.json"

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
        except Exception as exc:
            logger.error("Error loading %s: %s", fp, exc)
            self._cache[election_type] = []
            return []

    def _save(self, election_type: ElectionType, data: List[Dict[str, Any]]) -> None:
        fp = self._path(election_type)
        fp.parent.mkdir(parents=True, exist_ok=True)
        tmp = fp.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        tmp.replace(fp)
        self._cache[election_type] = data
        logger.info("Saved %d %ss → %s", len(data), election_type, fp)

    # ── public API: read ──────────────────────────────────────────────────

    def get_all(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        """Return all politicians of a given type."""
        self._ensure_slugs()
        return self._load(election_type)

    def get_all_politicians(self) -> List[Dict[str, Any]]:
        """Return all MPs + MLAs."""
        self._ensure_slugs()
        return self._load("MP") + self._load("MLA")

    def get_by_id(self, politician_id: str) -> Optional[Dict[str, Any]]:
        """Lookup a politician by ID across both MP and MLA."""
        self._ensure_slugs()
        return self._by_id.get(politician_id)

    def get_by_slug(self, politician_slug: str) -> Optional[Dict[str, Any]]:
        """Lookup a politician by slug across both MP and MLA."""
        self._ensure_slugs()
        return self._by_slug.get(politician_slug)

    def search(
        self,
        query: str,
        *,
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search politicians by name, state, constituency, or party.

        All filters are case-insensitive substring matches.
        """
        self._ensure_slugs()
        q = query.lower().strip()
        types: list[str] = [election_type] if election_type else ["MP", "MLA"]

        results: List[Dict[str, Any]] = []
        for etype in types:
            for p in self._load(etype):  # type: ignore[arg-type]
                if limit and len(results) >= limit:
                    break

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

                # Search across key text fields
                searchable = " ".join(
                    [
                        p.get("name", ""),
                        p.get("state", ""),
                        p.get("constituency", ""),
                    ]
                ).lower()

                # Also include party names from elections
                bg = p.get("political_background", {})
                for election in bg.get("elections", []):
                    searchable += " " + election.get("party", "").lower()

                if q in searchable:
                    results.append(p)

        return results

    def get_by_state(
        self, state: str, election_type: Optional[ElectionType] = None
    ) -> List[Dict[str, Any]]:
        """Get all politicians from a specific state."""
        self._ensure_slugs()
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
        self._ensure_slugs()
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
            "top_parties": sorted(by_party.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
            "top_states": sorted(by_state.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
        }

    # ── public API: write ─────────────────────────────────────────────────

    def update_politician(
        self, politician_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a politician's fields in-place and persist.

        Returns the updated record, or None if not found.
        """
        for etype in ("MP", "MLA"):
            records = self._load(etype)  # type: ignore[arg-type]
            for i, p in enumerate(records):
                if p.get("id") == politician_id:
                    merged = self._merge_nested(p, updates)
                    records[i] = merged
                    self._save(etype, records)  # type: ignore[arg-type]
                    # Ensure slug indices remain consistent with any potential name changes.
                    self._slugs_ensured = False
                    return records[i]
        return None

    def _merge_nested(
        self, existing: Dict[str, Any], updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Shallow merge with special handling for political_background (append elections)."""
        merged = {**existing, **updates}

        if "political_background" in updates and isinstance(
            existing.get("political_background"), dict
        ):
            merged["political_background"] = self._merge_political_background(
                existing.get("political_background") or {},
                updates.get("political_background") or {},
            )

        return merged

    @staticmethod
    def _merge_political_background(
        existing_pb: Dict[str, Any], new_pb: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Append elections without duplicating existing entries; prefer new summary if provided."""
        existing_elections = existing_pb.get("elections") or []
        new_elections = new_pb.get("elections") or []

        # Deduplicate by tuple of core fields
        def key(e: Dict[str, Any]) -> tuple:
            return (
                e.get("year"),
                e.get("type"),
                (e.get("state") or "").lower(),
                (e.get("constituency") or "").lower(),
                (e.get("party") or "").lower(),
                (e.get("status") or "").lower(),
            )

        seen = {key(e): e for e in existing_elections if isinstance(e, dict)}
        for e in new_elections:
            if not isinstance(e, dict):
                continue
            k = key(e)
            if k not in seen:
                seen[k] = e

        merged_elections = list(seen.values())

        summary = new_pb.get("summary")
        merged_summary = summary if summary is not None else existing_pb.get("summary")

        return {"elections": merged_elections, "summary": merged_summary}

    # ── cache management ──────────────────────────────────────────────────

    def reload(self, election_type: Optional[ElectionType] = None) -> None:
        """Clear cache so next access re-reads from disk."""
        if election_type:
            self._cache.pop(election_type, None)
        else:
            self._cache.clear()
