"""Fits the TF-IDF vectorizer once against the current database and
pickles it to artifacts/ so the API never has to refit at request
time (spec sections 12, 31, 32).

Run from backend/ any time the database changes:

    python -m app.nlp.build_artifacts

main.py loads this pickle at FastAPI startup (see app/main.py). If the
pickle is missing, main.py builds the index in-memory as a fallback --
fine for 30 records, but the pickle is what keeps startup instant as
the dataset grows (spec section 57 assumes it will).
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "floriography.db"
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "tfidf_index.pkl"

sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import connection, repository  # noqa: E402
from app.nlp.tfidf_search import build_index  # noqa: E402


def main() -> None:
    conn = connection.get_connection(str(DB_PATH))
    records = repository.get_all_search_records(conn)
    conn.close()

    index = build_index(records)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACT_PATH, "wb") as f:
        pickle.dump(index, f)

    print(f"Fit TF-IDF over {len(records)} records, {len(index.vectorizer.get_feature_names_out())} vocabulary terms.")
    print(f"Wrote {ARTIFACT_PATH} ({ARTIFACT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
