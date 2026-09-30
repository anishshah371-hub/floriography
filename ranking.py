"""Turns a keyword_search.KeywordResult / tfidf_search.TfidfResult list
into the API-facing result shape, with a plain-language, evidence-based
explanation -- never a fabricated one (spec section 15).

A result whose score falls below MIN_SIMILARITY_SCORE is dropped
before this module ever sees it (see search_service.py) rather than
shown with a "this probably isn't relevant" score -- see
docs/EVALUATION.md for how that threshold was chosen.
"""

from __future__ import annotations


def explain(matched_terms: list[str], max_terms: int = 5) -> str:
    if not matched_terms:
        return "No shared documented terms were found for this query."
    shown = matched_terms[:max_terms]
    return "Matched because the documented meaning shares these terms with your query: " + ", ".join(shown) + "."


def to_result_dict(result, rank: int) -> dict:
    f = result.flower
    return {
        "rank": rank,
        "id": f.id,
        "flower": f.flower,
        "historical_meaning": f.historical_meaning,
        "human_language_meaning": f.human_language_meaning,
        "communication_category": f.communication_category,
        "similarity_score": round(result.score, 4),
        "matched_terms": result.matched_terms,
        "explanation": explain(result.matched_terms),
    }


def to_result_dicts(results) -> list[dict]:
    return [to_result_dict(r, rank=i) for i, r in enumerate(results, start=1)]
