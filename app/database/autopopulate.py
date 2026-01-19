"""
Lightweight, safe data seeding on app startup.

- Only runs when AUTO_POPULATE_DB=true (default).
- Skips if candidates already exist (idempotent).
- Uses the existing JSON dataset and loads a small chunk by default to keep
  local/dev environments fast.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_session, init_db
from app.database.models import Candidate, Constituency, Party

logger = logging.getLogger(__name__)


def _should_populate() -> bool:
    return os.getenv("AUTO_POPULATE_DB", "true").lower() == "true"


def _get_settings() -> Tuple[Path, int]:
    data_dir = Path(
        os.getenv(
            "AUTO_POPULATE_ELECTION_DIR", "app/data/lok_sabha/lok-sabha-2024"
        )
    )
    limit_str = os.getenv("AUTO_POPULATE_LIMIT", "500")
    try:
        limit = max(1, int(limit_str))
    except ValueError:
        limit = 500
    return data_dir, limit


def _load_json(path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
    if not path.exists():
        logger.warning("Seed file missing: %s", path)
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if limit is not None:
                return data[:limit]
            return data
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to read %s: %s", path, exc)
        return []


def _filter_nota(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove NOTA entries from candidates list."""
    return [c for c in candidates if c.get("name") != "NOTA"]


def _load_dataset(base_dir: Path, limit: int) -> Dict[str, List[Dict[str, Any]]]:
    candidates = _load_json(base_dir / "candidates.json", limit)
    return {
        "parties": _load_json(base_dir / "parties.json", None),  # usually small
        "constituencies": _load_json(base_dir / "constituencies.json", None),
        "candidates": _filter_nota(candidates),
    }


def populate_if_empty() -> None:
    """
    Seed database with a small slice of JSON data if empty.

    Safe to call repeatedly; it bails out if candidates already exist.
    """
    if not _should_populate():
        logger.info("AUTO_POPULATE_DB disabled; skipping seed.")
        return

    data_dir, limit = _get_settings()
    if not data_dir.exists():
        logger.warning("Seed directory does not exist: %s", data_dir)
        return

    try:
        init_db()
    except Exception as exc:  # pragma: no cover
        logger.error("Skipping seed; init_db failed: %s", exc)
        return

    with get_db_session() as session:
        existing = session.query(Candidate).count()
        if existing > 0:
            logger.info("Database already has candidates (%s); skipping seed.", existing)
            return

        dataset = _load_dataset(data_dir, limit)
        if not dataset["candidates"]:
            logger.warning("No seed candidates found in %s; skipping seed.", data_dir)
            return

        logger.info(
            "Auto-populating DB from %s (limit candidates=%s)...", data_dir, limit
        )
        parties_count = Party.bulk_upsert(session, dataset["parties"])
        const_count = Constituency.bulk_upsert(session, dataset["constituencies"])
        cand_count = Candidate.bulk_upsert(session, dataset["candidates"])
        logger.info(
            "Seed complete: parties=%s constituencies=%s candidates=%s",
            parties_count,
            const_count,
            cand_count,
        )

