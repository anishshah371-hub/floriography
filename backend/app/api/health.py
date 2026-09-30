"""Health-check route. Also confirms the database is reachable, so a
green /api/health means "the API is up AND the data layer is up",
not just "the process is running".
"""

from fastapi import APIRouter

from app.config import settings
from app.database.connection import get_connection
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    try:
        conn = get_connection(settings.DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        message="Floriography API is running" if db_ok else "API is running, but the database is unreachable",
    )
