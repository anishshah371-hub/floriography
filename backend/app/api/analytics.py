"""Analytics route -- every number is computed from the live database
at request time, never hard-coded (spec sections 4, 25, 59)."""

from fastapi import APIRouter

from app.schemas.analytics import AnalyticsResponse
from app.services import analytics_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    return AnalyticsResponse(**analytics_service.get_analytics())
