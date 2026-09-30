"""Meaning-search service: loads the TF-IDF index once and reuses it,
runs keyword or TF-IDF retrieval, applies the similarity threshold,
and returns the API-facing result shape from ranking.py.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from app.config import settings
from app.database import repository
from app.database.connection import get_connection
from app.nlp import keyword_search, ranking, tfidf_search
from app.nlp.tfidf_search import TfidfIndex

_index: TfidfIndex | None = None


def get_index() -> TfidfIndex:
    """Load the TF-IDF index once (from the pickled artifact if
    present, else built in-memory from the DB) and reuse it for every
    request -- never refit per request (spec section 12). Called once
    at FastAPI startup (see app/main.py's lifespan) so the pickle read
    / fit cost never lands on a real user request."""
    global _index
    if _index is not None:
        return _index

    artifact_path = Path(settings.TFIDF_ARTIFACT_PATH)
    if artifact_path.exists():
        with open(artifact_path, "rb") as f:
            _index = pickle.load(f)
        return _index

    conn = get_connection(settings.DB_PATH)
    try:
        records = repository.get_all_search_records(conn)
    finally:
        conn.close()
    _index = tfidf_search.build_index(records)
    return _index


def search_meaning(query: str, top_k: int | None = None, method: str = "tfidf") -> dict:
    top_k = top_k or settings.DEFAULT_SEARCH_TOP_K
    index = get_index()

    if method == "keyword":
        results = keyword_search.search(query, index.records, top_k=top_k)
    else:
        results = tfidf_search.search(query, index, top_k=top_k)
        # Drop noise-level matches (spec section 16) -- see
        # config/settings.py for how this threshold was chosen.
        results = [r for r in results if r.score >= settings.MIN_SIMILARITY_SCORE]

    result_dicts = ranking.to_result_dicts(results)
    message = None if result_dicts else "No strong documented matches were found for this query."
    return {"query": query, "method": method, "results": result_dicts, "message": message}
