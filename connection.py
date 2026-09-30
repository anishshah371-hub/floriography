"""SQLite connection + schema.

Plain sqlite3 (stdlib) -- no ORM. For a single, small, mostly-static
reference table this keeps the schema and the queries fully visible
(repository.py) instead of hidden behind ORM mapping magic, which
matters for a project meant to be explained line-by-line.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS flowers (
    id INTEGER PRIMARY KEY,
    flower TEXT NOT NULL,
    historical_meaning TEXT NOT NULL,
    human_language_meaning TEXT NOT NULL,
    communication_category TEXT NOT NULL,
    normalized_flower TEXT NOT NULL,
    normalized_historical_meaning TEXT NOT NULL,
    normalized_human_language_meaning TEXT NOT NULL,
    normalized_communication_category TEXT NOT NULL,
    search_text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_flowers_category ON flowers (communication_category);
CREATE INDEX IF NOT EXISTS idx_flowers_normalized_flower ON flowers (normalized_flower);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
