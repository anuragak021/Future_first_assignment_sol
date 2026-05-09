# traceStore — SQLite store for tool traces exposed to the frontend
import sqlite3
import json
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("/tmp/trace_store.db")


class TraceStore:
    """Lightweight SQLite store: one row per request, tool trace as JSON."""

    def __init__(self, dbPath: Path = DB_PATH) -> None:
        self._dbPath = dbPath
        self._initDb()

    def _initDb(self) -> None:
        with sqlite3.connect(self._dbPath) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    trace_json TEXT NOT NULL,
                    verdict TEXT,
                    faithfulness REAL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON traces(session_id)")
            conn.commit()

    def saveTrace(
        self,
        sessionId: str,
        query: str,
        toolTrace: list[dict],
        verdict: str = "",
        faithfulness: float = 1.0,
    ) -> int:
        with sqlite3.connect(self._dbPath) as conn:
            cursor = conn.execute(
                "INSERT INTO traces (session_id, query, trace_json, verdict, faithfulness, created_at) VALUES (?,?,?,?,?,?)",
                (sessionId, query, json.dumps(toolTrace), verdict, faithfulness, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return cursor.lastrowid

    def getTracesForSession(self, sessionId: str, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self._dbPath) as conn:
            rows = conn.execute(
                "SELECT id, query, trace_json, verdict, faithfulness, created_at FROM traces WHERE session_id=? ORDER BY id DESC LIMIT ?",
                (sessionId, limit),
            ).fetchall()
        return [
            {
                "id": r[0],
                "query": r[1],
                "trace": json.loads(r[2]),
                "verdict": r[3],
                "faithfulness": r[4],
                "createdAt": r[5],
            }
            for r in rows
        ]


@lru_cache()
def getTraceStore() -> TraceStore:
    return TraceStore()
