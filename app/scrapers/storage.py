"""
JSON storage layer for politician data.

Handles reading, writing, and deduplication of mp.json / mla.json.
All functions are stateless — they operate on file paths.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ── Helpers ──────────────────────────────────────────────────────────────────


def _serialize(obj: Any) -> Any:
    """Recursively convert non-JSON-native types (Pydantic Url, etc.) to str."""
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if hasattr(obj, "__str__") and not isinstance(
        obj, (str, int, float, bool, type(None))
    ):
        return str(obj)
    return obj


# ── Public API ───────────────────────────────────────────────────────────────


def load_politicians(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load existing politicians from a JSON file.

    Returns an empty list if the file doesn't exist or is invalid.
    """
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s", filepath, exc)
        return []


def load_existing_ids(filepath: Path) -> Set[str]:
    """Return the set of politician ``id`` values already on disk."""
    return {p.get("id") for p in load_politicians(filepath) if p.get("id")}


def save_politicians(politicians: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Atomically write a full list of politicians to *filepath*.

    Uses a temp-file + rename so a crash never leaves a half-written file.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    safe_data = _serialize(politicians)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(safe_data, fh, indent=2, ensure_ascii=False)
    tmp.replace(filepath)
    logger.info("Saved %d politicians → %s", len(politicians), filepath)


def append_politician(
    politician_dict: Dict[str, Any],
    filepath: Path,
    existing_ids: Set[str],
) -> bool:
    """
    Append a single politician to *filepath* **if** their ``id`` is new.

    Updates *existing_ids* in-place on success so the caller's set stays
    current without re-reading the file.

    Returns ``True`` if the politician was added, ``False`` if skipped (dup).
    """
    pid = politician_dict.get("id", "")
    if pid in existing_ids:
        logger.debug("Skipping duplicate: %s", pid)
        return False

    # Load → append → save (atomic via save_politicians)
    current = load_politicians(filepath)
    current.append(politician_dict)
    save_politicians(current, filepath)
    existing_ids.add(pid)
    return True


def get_output_path(election_type: str, data_dir: Optional[Path] = None) -> Path:
    """Return ``data_dir/mp.json`` or ``data_dir/mla.json``."""
    base = data_dir or Path("app/data")
    return base / f"{election_type.lower()}.json"
