"""Flower lookup routes. Thin -- everything real happens in
services/flower_service.py.

Route order matters: /categories and /search are literal path
segments and must be registered BEFORE /{flower_id}, or a request to
e.g. /api/flowers/search would be swallowed by the {flower_id}: int
route and rejected as invalid input instead of reaching search().
"""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.flower import FlowerListResponse, FlowerOut
from app.services import flower_service

router = APIRouter(prefix="/api/flowers", tags=["flowers"])


@router.get("", response_model=FlowerListResponse)
def list_flowers(
    search: str | None = Query(None, description="Partial, case-insensitive flower-name match"),
    category: str | None = Query(None, description="Exact communication_category match"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    records, total = flower_service.list_flowers(category=category, search=search, limit=limit, offset=offset)
    return FlowerListResponse(
        total=total,
        limit=limit,
        offset=offset,
        results=[FlowerOut(**r.to_dict()) for r in records],
    )


@router.get("/categories", response_model=list[str])
def list_categories():
    return flower_service.list_categories()


@router.get("/search", response_model=FlowerListResponse)
def search_flowers(query: str = Query(..., min_length=1)):
    """Tolerant flower-name search: 'rose', 'Rose, Red', 'ROSE RED' all
    work (spec section 9). Returns an empty list, never a fabricated
    record, when nothing matches."""
    records = flower_service.search_flowers_by_name(query)
    return FlowerListResponse(total=len(records), limit=len(records), offset=0, results=[FlowerOut(**r.to_dict()) for r in records])


@router.get("/{flower_id}", response_model=FlowerOut)
def get_flower(flower_id: int):
    record = flower_service.get_flower(flower_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No flower found with id {flower_id}")
    return FlowerOut(**record.to_dict())
