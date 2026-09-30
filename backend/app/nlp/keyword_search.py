"""Baseline retrieval: token-overlap (Jaccard) keyword matching.

This is the "before" in the baseline-vs-improved comparison in
docs/EVALUATION.md. It has no notion of term importance -- every
shared word counts the same, so common words dominate. TF-IDF
(tfidf_search.py) is the fix for that; this module exists so the
improvement is actually measured against something, not asserted.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.database.models import Flower
from app.nlp.preprocessing import tokenize


@dataclass
class KeywordResult:
    flower: Flower
    score: float  # Jaccard similarity of token sets, in [0, 1]
    matched_terms: list[str]


def search(query: str, records: list[Flower], top_k: int = 5) -> list[KeywordResult]:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    scored = []
    for record in records:
        record_tokens = set(tokenize(record.search_text))
        shared = query_tokens & record_tokens
        if not shared:
            continue
        union = query_tokens | record_tokens
        jaccard = len(shared) / len(union)
        scored.append(KeywordResult(flower=record, score=jaccard, matched_terms=sorted(shared)))

    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]
