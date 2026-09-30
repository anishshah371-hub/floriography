# Project Specification (condensed)

Condensed from the full authoritative specification supplied for this
build. Not a verbatim copy — see git history / conversation record for
the complete original if needed.

## Product

An information-retrieval application over a documented flower-
symbolism dataset, in two directions:

1. **Flower → meaning** — look up a flower's documented historical
   meaning, human-language interpretation, and category.
2. **Meaning → flower** — describe an emotion/intention in natural
   language; get flowers ranked by textual similarity to their
   documented meanings.

This is retrieval, not generation: results only ever come from the
supplied dataset. The system must never invent a flower, a meaning, a
source, or a confidence value that isn't backed by the data.

## Dataset

30 records (`data/raw/sample_for_floriography.csv`), columns: `id,
flower, historical_meaning, human_language_meaning,
communication_category`. Treated as authoritative seed data — see
`docs/DATA_DICTIONARY.md` for the full field-by-field description and
the one documented cleaning transformation applied.

## Stack

React + Vite + Tailwind + React Router + Recharts (frontend); FastAPI
+ Pydantic (backend); pandas (pipeline); scikit-learn (TF-IDF +
cosine similarity); SQLite (database). No FAISS, no LLM-generated
explanations, no authentication, no Docker — none were justified at
this scale.

## Architecture

`api/` (thin FastAPI routes) → `services/` (orchestration) →
`database/` (SQLite, parameterized queries) + `nlp/` (keyword search,
TF-IDF search, ranking, evaluation). Full detail in
`docs/ARCHITECTURE.md`.

## Search methodology

Baseline keyword (Jaccard token overlap) vs. primary TF-IDF + cosine
similarity, measured against each other on a small dataset-justified
evaluation set — not asserted, measured (`docs/EVALUATION.md`). Every
result includes the actual matched terms and a templated, evidence-
based explanation of why it matched. Full detail in
`docs/SEARCH_METHODOLOGY.md`.

## API

`GET /api/health` (checks DB connectivity too) · `GET /api/flowers`
(list/filter/paginate) · `GET /api/flowers/categories` · `GET
/api/flowers/search?query=` · `GET /api/flowers/{id}` · `GET
/api/search/meaning?query=&top_k=&method=` · `GET /api/analytics`.

## Frontend routes

`/` (dual flower/meaning search entry) · `/flowers` (explorer, search +
category filter) · `/flowers/:id` (detail) · `/search` (meaning-search
results, expandable "why this matched") · `/analytics` (live-computed
stats + category chart) · `/about` (methodology).

## Non-negotiables carried through the whole build

- No hard-coded dataset statistics anywhere in the UI or API — every
  number in `/api/analytics` is a live query.
- No fabricated sources, scores, or confidence values — every
  `similarity_score` is a real computed cosine similarity or Jaccard
  value; there is currently no source-citation data, so none is shown.
- Raw dataset preserved exactly; all cleaning happens in a separate,
  documented, reproducible processed copy.
- Every stage of the pipeline (validate → clean → DB → TF-IDF artifact
  → retrieval → ranking → evaluation) is runnable as a standalone
  script, not only reachable through the API.
