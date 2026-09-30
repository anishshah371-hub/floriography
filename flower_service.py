"""Flower lookup/search -- API route handlers call these, never the
repository directly.
"""

from __future__ import annotations

from app.config import settings
from app.database import repository
from app.database.connection import get_connection
from app.database.models import Flower


def list_flowers(
    category: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Flower], int]:
    conn = get_connection(settings.DB_PATH)
    try:
        records = repository.get_all(conn, category=category, search=search, limit=limit, offset=offset)
        total = repository.count_all(conn, category=category, search=search)
    finally:
        conn.close()
    return records, total


def get_flower(flower_id: int) -> Flower | None:
    conn = get_connection(settings.DB_PATH)
    try:
        return repository.get_by_id(conn, flower_id)
    finally:
        conn.close()


def search_flowers_by_name(query: str) -> list[Flower]:
    """Tolerant flower-name search (spec section 9): 'rose', 'Rose,
    Red', 'ROSE RED' should all find the right records."""
    conn = get_connection(settings.DB_PATH)
    try:
        return repository.search_by_name(conn, query)
    finally:
        conn.close()


def list_categories() -> list[str]:
    conn = get_connection(settings.DB_PATH)
    try:
        return repository.get_categories(conn)
    finally:
        conn.close()
