"""Analytics computed live from the database -- never hard-coded
(spec sections 4, 59)."""

from __future__ import annotations

from app.config import settings
from app.database import repository
from app.database.connection import get_connection


def get_analytics() -> dict:
    conn = get_connection(settings.DB_PATH)
    try:
        total = repository.count_all(conn)
        distribution = repository.get_category_distribution(conn)
        text_stats = repository.get_text_length_stats(conn)
    finally:
        conn.close()

    return {
        "total_records": total,
        "category_distribution": distribution,
        "category_count": len(distribution),
        "text_length_stats": text_stats,
    }
