# Floriography

An information-retrieval application over a documented dataset of
flower symbolism — not a chatbot, not generative AI. It searches a
flower name and returns its documented meaning, or takes a natural-
language description of a feeling and ranks flowers whose documented
meanings actually match it, using TF-IDF + cosine similarity. Built as
a BCA Data Science portfolio project, designed to be explainable
line-by-line in a technical interview.

## Problem statement

Floriography (the historical practice of assigning symbolic meanings
to flowers) is documented but scattered and inconsistent across
sources. This project makes a small, documented slice of it
searchable in both directions — by flower name, and by the feeling or
intention someone wants to communicate — while being explicit about
what is and isn't backed by evidence: no invented meanings, no
fabricated sources, no confidence values that aren't real computed
scores.

## Features

- **Flower search** — exact, partial, and token-based matching, so
  "rose", "Rose, Red", and "ROSE RED" all find the right record(s).
- **Flower detail pages** — documented historical meaning,
  human-language interpretation, and category.
- **Meaning search** — natural-language query → ranked flowers, each
  with a real similarity score, the actual matched terms, and an
  expandable "why this matched" explanation generated from that
  evidence.
- **Category explorer** — browse/filter the dataset; categories are
  loaded from the database, never hard-coded.
- **Analytics page** — category distribution and text-length stats,
  computed live from the database on every load.
- **Baseline vs. improved retrieval, actually measured**: a simple
  keyword-overlap method and TF-IDF + cosine similarity are both
  implemented and evaluated against each other — see
  `docs/EVALUATION.md`.

## Tech stack

| | |
|---|---|
| Frontend | React, Vite, Tailwind CSS, React Router, Recharts |
| Backend | Python, FastAPI, Pydantic |
| Data | pandas |
| NLP | scikit-learn (TF-IDF, cosine similarity) |
| Database | SQLite |

## Architecture

`frontend/` (React) → HTTP/JSON → `backend/app/api/` (thin FastAPI
routes) → `backend/app/services/` (orchestration) →
`backend/app/database/` (SQLite) + `backend/app/nlp/` (keyword search,
TF-IDF, ranking, evaluation). Full explanation, including *why* it's
shaped this way, in **`docs/ARCHITECTURE.md`**.

## Dataset

30 records, 12 categories, supplied as `data/raw/sample_for_floriography.csv`
and treated as authoritative. Full field-by-field description and the
one documented cleaning transformation in **`docs/DATA_DICTIONARY.md`**.

## Data pipeline

`data/raw/*.csv` → validate (required columns, unique/valid ids, no
missing values) → clean (lowercase/whitespace-normalize into a
separate `normalized_*` + `search_text` representation; raw text is
never overwritten) → `data/processed/*.csv` + SQLite. Reproducible:

    cd backend
    python -m app.database.build_database

## Search methodology

Full explanation — term frequency, inverse document frequency, cosine
similarity, why TF-IDF beats raw keyword overlap on this dataset (with
a real measured example), why embeddings weren't added, and how
"why this matched" explanations are generated from actual evidence —
in **`docs/SEARCH_METHODOLOGY.md`**.

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Process + database connectivity check |
| `GET /api/flowers?search=&category=&limit=&offset=` | List/filter/paginate |
| `GET /api/flowers/categories` | Distinct categories, from the DB |
| `GET /api/flowers/search?query=` | Tolerant flower-name search |
| `GET /api/flowers/{id}` | Single flower detail |
| `GET /api/search/meaning?query=&top_k=&method=` | Meaning search (`method=tfidf`\|`keyword`) |
| `GET /api/analytics` | Live-computed dataset statistics |

Interactive docs at `/docs` once the backend is running (FastAPI's
built-in OpenAPI UI).

## Frontend

`/` dual search entry · `/flowers` explorer (search + category filter)
· `/flowers/:id` detail · `/search` meaning-search results ·
`/analytics` stats + chart · `/about` methodology. Every page has
loading, error, and empty states — no silent failures, no fabricated
data when a search comes up empty.

## Evaluation

TF-IDF beats the keyword baseline on every measured metric (MRR 0.667
→ 0.812, Recall@5 0.49 → 0.646). Full methodology, the 8-query
evaluation set with dataset-backed relevance judgments, the exact
numbers, and where/why the two methods disagree: **`docs/EVALUATION.md`**.
Reproduce it yourself with `python -m app.nlp.run_evaluation` from
`backend/`.

## Testing

| Suite | Covers | Status in this build |
|---|---|---|
| `tests/test_database.py` (13 tests) | Validation, cleaning, DB queries, tolerant search | **Run — all passing** |
| `tests/test_nlp.py` (14 tests) | Preprocessing, keyword/TF-IDF search, ranking, evaluation | **Run — all passing** |
| `tests/test_api.py` | Every API endpoint via FastAPI's `TestClient` | Written, **not run** — see Known limitations |

```
python -m unittest tests.test_database tests.test_nlp -v
```

## Project structure

    floriography/
    ├── frontend/          React app (src/pages, components, services)
    ├── backend/
    │   ├── app/
    │   │   ├── api/       thin FastAPI routes
    │   │   ├── services/  orchestration
    │   │   ├── database/  SQLite, pipeline, models
    │   │   ├── nlp/       keyword/TF-IDF search, ranking, evaluation
    │   │   ├── schemas/   Pydantic request/response models
    │   │   ├── config/    environment-driven settings
    │   │   └── main.py
    │   └── requirements.txt
    ├── data/
    │   ├── raw/           untouched source CSV
    │   └── processed/     cleaned CSV, SQLite DB, data-quality report
    ├── artifacts/         pickled, pre-fit TF-IDF index
    ├── tests/
    └── docs/

## Installation & running locally

### Backend

    cd backend
    python3 -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python -m app.database.build_database   # builds data/processed/ + SQLite
    python -m app.nlp.build_artifacts        # fits + pickles the TF-IDF index
    uvicorn app.main:app --reload

API: http://127.0.0.1:8000 · Docs: http://127.0.0.1:8000/docs · Health:
http://127.0.0.1:8000/api/health

### Frontend

    cd frontend
    npm install
    npm run dev

App: http://localhost:5173 (Vite will pick another free port and tell
you if 5173 is taken — that's normal, not a failure).

## Environment variables

`backend/.env.example` and `frontend/.env.example` list everything
available; nothing is required to run locally (all have sensible
defaults). `frontend/`'s `VITE_API_BASE_URL` points the frontend at
the backend — set it if the backend isn't at the default
`http://127.0.0.1:8000`.

## Development workflow

Incremental, one reviewable change at a time; raw data is never
overwritten; the service/NLP layers have no FastAPI dependency so they
stay independently testable; every claim in this README and in
`docs/` is either something that was actually run in this build (data
pipeline, NLP, the 27 passing tests) or is explicitly flagged as not
yet runtime-verified (see below) — never asserted without one or the
other.

## Known limitations

- **Backend/frontend were not runtime-started in the environment this
  was built in** — it has no network access, so `pip install` /
  `npm install` cannot run there. What *was* verified in that
  environment: the entire data pipeline, the database layer, and the
  full NLP layer (keyword search, TF-IDF, ranking, evaluation) —
  27 automated tests, all passing, plus the service layer exercised
  directly against the real 30-record database. The FastAPI route
  layer and the React app are syntactically checked (Python
  `py_compile` + `tsc --noEmit` against every file) and were built by
  wrapping the already-tested service layer as thinly as possible, but
  have **not** been started and hit over real HTTP — that's the first
  thing to verify by running the commands above.
- **A real, measured retrieval gap**: "reject" (query) doesn't match
  "rejecting" (dataset text) because no stemming/lemmatization is
  applied (a deliberate trade-off — see `docs/SEARCH_METHODOLOGY.md`).
  Confirmed in `docs/EVALUATION.md`: both methods miss the one query
  this affects.
- **No source citations exist in the current dataset**, so none are
  shown. The schema is ready for `source_name` / `source_url` /
  `source_reference` fields to be added later without a redesign, but
  they aren't fabricated in the meantime.
- **8-query evaluation set** is enough to demonstrate and measure a
  real baseline-vs-improved difference, not enough for a statistically
  rigorous quality estimate — see `docs/EVALUATION.md`'s own
  limitations section.
- A found-and-fixed bug worth naming rather than hiding: tolerant
  flower-name search (`"ROSE RED"` finding `"Rose, Red"`) initially
  failed because substring matching breaks on punctuation differences;
  a token-matching fallback was added after `tests/test_database.py`
  caught it. Left in this README as evidence the test suite was
  actually run, not just written.

## Future improvements

Sentence-embedding retrieval (only if it measurably beats TF-IDF on a
larger evaluation set — see `docs/SEARCH_METHODOLOGY.md`); light
stemming to close the "reject/rejecting" gap; source-citation fields
once real sources are added; a larger, multi-annotator evaluation set;
running `tests/test_api.py` and adding frontend interaction tests once
dependencies can actually be installed; deployment.

## Technical interview explanation

Short version: *"I built a small, honest information-retrieval system.
Raw data is preserved and cleaning is separate and documented. Search
starts from a measurable baseline (keyword overlap) and only adds
TF-IDF because I measured it winning — MRR 0.667 to 0.812 on an
evaluation set I built and justified from the data itself, not assumed.
Every result shows real evidence for why it matched, and the system
says so plainly when nothing matches well, instead of guessing. The
retrieval and data layers have zero web-framework dependency, so I
could unit-test them directly — 27 tests, all passing — independent of
whether the API server itself happens to be running."* Full depth in
`docs/ARCHITECTURE.md`, `docs/SEARCH_METHODOLOGY.md`, and
`docs/EVALUATION.md`.
