"""Database access functions.

API route handlers never touch SQL directly -- they call the service
layer, which calls these functions. Every query is parameterized
(no string-built SQL) to avoid injection, per spec section 41.
"""

from __future__ import annotations

import sqlite3

from app.nlp.preprocessing import normalize_text, tokenize

from .models import Flower

COLUMNS = ", ".join(Flower.__dataclass_fields__)


def insert_flowers(conn: sqlite3.Connection, rows: list[dict]) -> int:
    placeholders = ", ".join(f":{c}" for c in Flower.__dataclass_fields__)
    conn.executemany(
        f"INSERT OR REPLACE INTO flowers ({COLUMNS}) VALUES ({placeholders})",
        rows,
    )
    conn.commit()
    return len(rows)


def get_all(
    conn: sqlite3.Connection,
    category: str | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Flower]:
    query = f"SELECT {COLUMNS} FROM flowers WHERE 1=1"
    params: dict = {}
    if category:
        query += " AND communication_category = :category"
        params["category"] = category
    if search:
        query += " AND normalized_flower LIKE :search"
        params["search"] = f"%{search.strip().lower()}%"
    query += " ORDER BY id LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    rows = conn.execute(query, params).fetchall()
    return [Flower.from_row(r) for r in rows]


def count_all(conn: sqlite3.Connection, category: str | None = None, search: str | None = None) -> int:
    query = "SELECT COUNT(*) AS n FROM flowers WHERE 1=1"
    params: dict = {}
    if category:
        query += " AND communication_category = :category"
        params["category"] = category
    if search:
        query += " AND normalized_flower LIKE :search"
        params["search"] = f"%{search.strip().lower()}%"
    return conn.execute(query, params).fetchone()["n"]


def get_by_id(conn: sqlite3.Connection, flower_id: int) -> Flower | None:
    row = conn.execute(
        f"SELECT {COLUMNS} FROM flowers WHERE id = :id", {"id": flower_id}
    ).fetchone()
    return Flower.from_row(row) if row else None


def search_by_name(conn: sqlite3.Connection, query: str) -> list[Flower]:
    """Tolerant flower-name search (spec section 9): exact normalized
    match, then substring match, then token match -- in that order, so
    'rose' finds every Rose variant AND 'ROSE RED' / 'red rose' find
    "Rose, Red" even though punctuation and word order differ.

    Token match is needed because normalized_flower keeps punctuation
    ("rose, red"), so a comma-free query like "ROSE RED" won't appear
    as a literal substring of it -- tokenizing strips the comma from
    both sides before comparing.
    """
    normalized = normalize_text(query)

    exact = conn.execute(
        f"SELECT {COLUMNS} FROM flowers WHERE normalized_flower = :q", {"q": normalized}
    ).fetchall()
    if exact:
        return [Flower.from_row(r) for r in exact]

    partial = conn.execute(
        f"SELECT {COLUMNS} FROM flowers WHERE normalized_flower LIKE :q ORDER BY id",
        {"q": f"%{normalized}%"},
    ).fetchall()
    if partial:
        return [Flower.from_row(r) for r in partial]

    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []
    all_rows = conn.execute(f"SELECT {COLUMNS} FROM flowers ORDER BY id").fetchall()
    return [
        Flower.from_row(r) for r in all_rows
        if query_tokens <= set(tokenize(r["normalized_flower"]))
    ]


def get_all_search_records(conn: sqlite3.Connection) -> list[Flower]:
    """Every record, for building the in-memory TF-IDF index at startup."""
    rows = conn.execute(f"SELECT {COLUMNS} FROM flowers ORDER BY id").fetchall()
    return [Flower.from_row(r) for r in rows]


def get_categories(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT communication_category FROM flowers ORDER BY communication_category"
    ).fetchall()
    return [r["communication_category"] for r in rows]


def get_category_distribution(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT communication_category, COUNT(*) AS n FROM flowers "
        "GROUP BY communication_category ORDER BY n DESC"
    ).fetchall()
    return {r["communication_category"]: r["n"] for r in rows}


def get_text_length_stats(conn: sqlite3.Connection) -> dict:
    """Length stats computed in Python (SQLite has no stdev builtin) so
    the numbers are easy to verify by hand."""
    rows = conn.execute(
        "SELECT historical_meaning, human_language_meaning FROM flowers"
    ).fetchall()
    hist_lens = [len(r["historical_meaning"]) for r in rows]
    human_lens = [len(r["human_language_meaning"]) for r in rows]

    def stats(values: list[int]) -> dict:
        n = len(values)
        return {
            "min": min(values) if n else 0,
            "max": max(values) if n else 0,
            "mean": round(sum(values) / n, 1) if n else 0,
        }

    return {
        "historical_meaning": stats(hist_lens),
        "human_language_meaning": stats(human_lens),
    }
