import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parents[2] / "app" / "data" / "cache.db"


class PoliticianCache:
    _instance: Optional["PoliticianCache"] = None

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = str(db_path or DB_PATH)

    @classmethod
    def get_instance(cls) -> "PoliticianCache":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.init()
        return cls._instance

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def init(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS politicians (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    last_fetched TEXT NOT NULL
                )
                """
            )
        logger.info("Politician cache ready at %s", self._db_path)

    def is_processed(self, politician_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM politicians WHERE id = ?", (politician_id,)
            ).fetchone()
        return row is not None

    def mark_processed(self, politician_id: str, type_: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO politicians (id, type, last_fetched) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET type=excluded.type, last_fetched=excluded.last_fetched",
                (politician_id, type_, now),
            )

    def get(self, politician_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, type, last_fetched FROM politicians WHERE id = ?",
                (politician_id,),
            ).fetchone()
        if not row:
            return None
        return {"id": row[0], "type": row[1], "last_fetched": row[2]}

    def list_all(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, type, last_fetched FROM politicians ORDER BY id"
            ).fetchall()
        return [{"id": r[0], "type": r[1], "last_fetched": r[2]} for r in rows]

    def remove(self, politician_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM politicians WHERE id = ?", (politician_id,)
            )
        return cursor.rowcount > 0

    def clear(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM politicians")
        return cursor.rowcount
