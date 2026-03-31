import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set

from app.core.slugify import slugify, short_id_from_uuid

logger = logging.getLogger(__name__)

ElectionType = Literal["MP", "MLA"]

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------- NORMALIZE ----------
def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z ]', '', name)
    return name.strip()


class PoliticianService:

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self._data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._slugs_ensured: bool = False
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._by_slug: Dict[str, Dict[str, Any]] = {}

        # 🔥 LOAD PERFORMANCE HERE (SAFE)
        self._perf_map = self._load_performance()

    # ---------- LOAD PERFORMANCE ----------
    def _load_performance(self) -> Dict[str, Dict]:
        path = self._data_dir / "performance.json"

        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                normalize(p["name"]): p["performance"]
                for p in data
            }

        except Exception as e:
            logger.error("Performance load error: %s", e)
            return {}

    # ---------- ADD PERFORMANCE ----------
    def _attach_performance(self, p: Dict[str, Any]) -> Dict[str, Any]:
        name = normalize(p.get("name", ""))

        p["performance"] = self._perf_map.get(name, {
            "attendance": 0,
            "questions": 0,
            "debates": 0
        })

        return p

    # ---------- SLUG ----------
    def _ensure_slugs(self) -> None:
        if self._slugs_ensured:
            return

        mp_records = self._load("MP")
        mla_records = self._load("MLA")
        all_records = mp_records + mla_records

        base_counts: Dict[str, int] = {}

        for p in all_records:
            base = slugify(p.get("name", "")) or "politician"
            base_counts[base] = base_counts.get(base, 0) + 1

        self._by_id = {}
        self._by_slug = {}

        for p in all_records:
            pid = str(p.get("id", ""))
            base = slugify(p.get("name", "")) or "politician"
            short_id = short_id_from_uuid(pid) or "00000000"

            slug = base if base_counts[base] <= 1 else f"{base}-{short_id}"
            p["slug"] = slug

            if pid:
                self._by_id[pid] = p
            self._by_slug[slug] = p

        self._slugs_ensured = True

    # ---------- LOAD ----------
    def _path(self, election_type: ElectionType) -> Path:
        return self._data_dir / f"{election_type.lower()}.json"

    def _load(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        fp = self._path(election_type)

        if not fp.exists():
            return []

        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- API ----------
    def get_all(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        self._ensure_slugs()
        data = self._load(election_type)

        return [self._attach_performance(p) for p in data]

    def get_all_politicians(self) -> List[Dict[str, Any]]:
        self._ensure_slugs()
        data = self._load("MP") + self._load("MLA")

        return [self._attach_performance(p) for p in data]

    def get_by_id(self, politician_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_slugs()
        p = self._by_id.get(politician_id)

        return self._attach_performance(p) if p else None

    def get_by_slug(self, politician_slug: str) -> Optional[Dict[str, Any]]:
        self._ensure_slugs()
        p = self._by_slug.get(politician_slug)

        return self._attach_performance(p) if p else None

    def search(
        self,
        query: str,
        *,
        election_type: Optional[ElectionType] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:

        self._ensure_slugs()
        q = query.lower()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        results = []

        for p in data:
            if q in p.get("name", "").lower():
                results.append(self._attach_performance(p))

            if len(results) >= limit:
                break

        return results