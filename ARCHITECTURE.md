# Architecture

## Layers

**Frontend** (`frontend/`) — React + Vite + Tailwind CSS + React
Router + Recharts (analytics chart only). Talks to the backend only
over HTTP/JSON through `src/services/api.js`. Contains no NLP or
retrieval logic — it displays whatever the API returns, including the
`explanation` / `matched_terms` fields, rather than computing anything
itself.

**API layer** (`backend/app/api/`) — FastAPI route handlers:
`health.py`, `flowers.py`, `search.py`, `analytics.py`. Each is a thin
`APIRouter` that validates input (via Pydantic query/path params),
calls exactly one service function, and returns a Pydantic response
model (`backend/app/schemas/`). No SQL, no NLP, and no business logic
lives here.

**Service layer** (`backend/app/services/`) — `flower_service.py`,
`search_service.py`, `analytics_service.py`. Orchestrates calls to
`database/` and `nlp/`, and is the only layer that knows about both.
Uses plain functions and dataclasses (`database/models.py`) — no
FastAPI or Pydantic imports — so it can be (and is) unit-tested without
FastAPI installed.

**Database layer** (`backend/app/database/`) — `connection.py`
(SQLite connection + schema), `models.py` (the `Flower` dataclass),
`repository.py` (every SQL query, all parameterized), `pipeline.py`
(raw CSV → validated → cleaned), `build_database.py` (the runnable
pipeline entry point). One denormalized `flowers` table — deliberately
not split into a separate categories table; 30 rows of reference data
doesn't need that normalization, and the extra join would be
complexity with no real benefit at this scale.

**NLP layer** (`backend/app/nlp/`) — `preprocessing.py` (shared
tokenization), `keyword_search.py` (Jaccard-overlap baseline),
`tfidf_search.py` (TF-IDF + cosine similarity, the primary method),
`ranking.py` (formats results + generates evidence-based
explanations), `evaluation.py` (precision/recall/hit-rate/MRR +
the dataset-justified relevance set), `build_artifacts.py` /
`run_evaluation.py` (runnable scripts). No FastAPI/Pydantic imports
here either — every module in this layer is directly unit-tested in
`tests/test_nlp.py` against the real database.

**Config** (`backend/app/config/settings.py`) — the handful of values
that differ between environments (DB path, TF-IDF artifact path, CORS
origins, default `top_k`, the similarity threshold), read from
environment variables with sensible defaults. Not a settings
framework — there wasn't enough configuration to justify one.

**Preprocessing / artifacts** (`notebooks/`, `artifacts/`, `data/`) —
`data/raw/` holds the untouched source CSV; `data/processed/` holds the
cleaned CSV, the SQLite database, and the data-quality report;
`artifacts/` holds the pickled, pre-fit TF-IDF vectorizer + matrix
(`build_artifacts.py`), loaded once at FastAPI startup
(`main.py`'s `lifespan`) rather than refit per request.

## Data flow

    React frontend
          |  HTTP / JSON  (src/services/api.js)
          v
    FastAPI routes            (backend/app/api/)
          |
          v
    Service layer              (backend/app/services/)
          |
      +---+-------------------+
      v                       v
    database/                nlp/
    (SQLite, parameterized     (keyword_search -> tfidf_search
     queries, repository.py)    -> ranking -> evaluation)

    Offline / build-time, not per-request:
    data/raw/*.csv -> pipeline.py -> data/processed/*.csv + SQLite
    SQLite -> build_artifacts.py -> artifacts/tfidf_index.pkl

## Why this shape

- **database/ and nlp/ never import FastAPI or Pydantic.** This was a
  deliberate constraint, not an accident: it means the entire data
  pipeline, retrieval, ranking, and evaluation logic can be (and is,
  in `tests/test_database.py` and `tests/test_nlp.py`) imported and
  tested directly, with nothing about the web framework getting in the
  way of understanding or debugging the actual retrieval logic.
- **The TF-IDF index is a lazily-loaded module-level singleton**
  (`search_service.get_index()`), not a FastAPI dependency-injected
  object. For a project this size, `Depends()` machinery would be
  another abstraction to explain without adding real flexibility —
  a plain "load once, cache in a module global" pattern is one that
  a BCA Data Science student can point to and fully explain.
- **One `flowers` table**, not a normalized category table with a
  foreign key. Categories are just a `GROUP BY` away
  (`repository.get_category_distribution`); a separate table would be
  schema complexity the 30-row (or even a few-hundred-row) dataset
  doesn't need — see spec section 6 ("avoid unnecessary schema
  complexity").

## Current status (all implemented)

Data pipeline, database, keyword search, TF-IDF search, ranking,
evaluation, all backend API endpoints, and the full frontend (6 pages)
described above are implemented and — everywhere the sandboxed build
environment allowed it — actually executed and tested, not just
written. See the top-level README's "Testing" and "Known limitations"
sections for exactly which parts were runtime-verified versus
syntax-checked only.
