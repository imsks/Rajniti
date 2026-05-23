import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from .logger import log

logger = logging.getLogger(__name__)


class CacheManager:
    """Minimal SQLite cache with set/get/delete (TTL support optional)."""

    def __init__(self, db_path: Optional[str] = None):
        default_path = Path(__file__).resolve().parents[1] / "database" / "cache.db"
        self.db_path = str(db_path or default_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    @log(logger, "CacheManager._connect")
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    @log(logger, "CacheManager._init_table")
    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER
                )
                """)

    @log(logger, "CacheManager.set")
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        now = int(time.time())
        expires_at = now + ttl_seconds if ttl_seconds else None
        value_text = json.dumps(value, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    created_at = excluded.created_at,
                    expires_at = excluded.expires_at
                """,
                (key, value_text, now, expires_at),
            )

    @log(logger, "CacheManager.get")
    def get(self, key: str) -> Optional[Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?",
                (key,),
            ).fetchone()

        if not row:
            return None

        value_text, expires_at = row
        now = int(time.time())

        if expires_at is not None and now > expires_at:
            self.delete(key)
            return None

        try:
            return json.loads(value_text)
        except Exception:
            return value_text

    @log(logger, "CacheManager.exists")
    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    @log(logger, "CacheManager.delete")
    def delete(self, key: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        return cur.rowcount > 0

    @log(logger, "CacheManager.clear")
    def clear(self) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM cache")
        return cur.rowcount
