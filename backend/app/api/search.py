"""Meaning-search route: natural-language query -> ranked, explainable
flower results (spec sections 8, 10, 15)."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.search import MeaningSearchResponse
from app.services import search_service

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/meaning", response_model=MeaningSearchResponse)
def meaning_search(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    method: str = Query("tfidf", description="'tfidf' (primary) or 'keyword' (baseline, for comparison)"),
):
    if method not in ("tfidf", "keyword"):
        raise HTTPException(status_code=422, detail="method must be 'tfidf' or 'keyword'")
    result = search_service.search_meaning(query, top_k=top_k, method=method)
    return MeaningSearchResponse(**result)
