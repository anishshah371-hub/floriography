"""FastAPI application entry point.

Kept small: creates the app, wires middleware, pre-loads the TF-IDF
index once at startup, and includes routers. Route logic lives in
api/, business/retrieval logic in services/ and nlp/ -- not here.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.flowers import router as flowers_router
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.config import settings
from app.services import search_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load (or build, if the pickled artifact is missing) the TF-IDF
    # index once here, so the first real search request isn't also
    # the request that pays the fit/load cost (spec sections 12, 32).
    search_service.get_index()
    yield


app = FastAPI(title="Floriography API", lifespan=lifespan)

# Local Vite dev server only. Production origins get added when the
# app is actually deployed -- not before it's needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(flowers_router)
app.include_router(search_router)
app.include_router(analytics_router)
