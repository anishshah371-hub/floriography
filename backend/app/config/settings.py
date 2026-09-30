"""Centralized configuration. Plain module-level constants read from
the environment, not a settings framework -- there are only a handful
of values and they don't change per-request, so a heavier settings
library would be complexity this project doesn't need yet.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/config/settings.py -> floriography/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Loads floriography/.env if present (see .env.example at the project
# root). Explicit path rather than relying on cwd, so this works
# whether the backend is started from backend/ or from the project
# root. Safe to call even if the file doesn't exist -- os.environ.get
# defaults below still apply.
load_dotenv(PROJECT_ROOT / ".env")

DB_PATH = os.environ.get(
    "FLORIOGRAPHY_DB_PATH", str(PROJECT_ROOT / "data" / "processed" / "floriography.db")
)
TFIDF_ARTIFACT_PATH = os.environ.get(
    "FLORIOGRAPHY_TFIDF_ARTIFACT", str(PROJECT_ROOT / "artifacts" / "tfidf_index.pkl")
)

CORS_ORIGINS = os.environ.get(
    "FLORIOGRAPHY_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

DEFAULT_SEARCH_TOP_K = int(os.environ.get("FLORIOGRAPHY_SEARCH_TOP_K", "5"))

# Below this TF-IDF cosine-similarity score, a "match" is noise (a
# single common word like "and") rather than real evidence -- chosen
# by inspecting the actual score distribution over the evaluation
# queries (docs/EVALUATION.md): scores cluster at 0.057-0.059 for
# single-stopword overlaps, then jump to 0.165+ for anything with a
# genuinely shared content word. 0.1 sits in that gap.
MIN_SIMILARITY_SCORE = float(os.environ.get("FLORIOGRAPHY_MIN_SIMILARITY", "0.1"))
