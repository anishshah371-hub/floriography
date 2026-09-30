# Data Dictionary

## Source

`data/raw/sample_for_floriography.csv` — 30 records, supplied as the
project's authoritative seed dataset. Never modified; every other
data artifact in this project is derived from it.

## Raw columns (as supplied)

| Column | Description |
|---|---|
| `id` | Unique record identifier, 1-30. |
| `flower` | Display name of the flower, exactly as supplied (e.g. `"Rose, Red"`). |
| `historical_meaning` | Documented historical/floriography meaning, exactly as supplied. May contain multiple short phrases separated by a period (e.g. `"Purity. Sweetness"`) — this is meaningful structure, not a typo, and is preserved as-is. |
| `human_language_meaning` | A natural-language sentence interpretation of the historical meaning, exactly as supplied. |
| `communication_category` | A single documented category label (e.g. `Love`, `Friendship`). 12 distinct values across the 30 records. |

## Derived columns (added by `backend/app/database/pipeline.py`)

| Column | How it's derived | Why it exists |
|---|---|---|
| `normalized_flower` | `flower`, lowercased + whitespace-collapsed. | Case/whitespace-insensitive flower lookup. |
| `normalized_historical_meaning` | `historical_meaning`, lowercased + whitespace-collapsed, **plus the one documented spelling correction below**. | Search text; never shown to users. |
| `normalized_human_language_meaning` | `human_language_meaning`, lowercased + whitespace-collapsed. | Search text. |
| `normalized_communication_category` | `communication_category`, lowercased + whitespace-collapsed. | Search text. |
| `search_text` | `normalized_historical_meaning + " " + normalized_human_language_meaning + " " + normalized_communication_category` | The exact string that gets vectorized for both keyword and TF-IDF meaning search. Flower name is deliberately excluded — see docs/SEARCH_METHODOLOGY.md. |

None of the raw display columns (`flower`, `historical_meaning`,
`human_language_meaning`, `communication_category`) are ever modified —
they are carried through to `data/processed/flowers_processed.csv` and
the database unchanged.

## Documented data-cleaning transformations

Exactly one transformation is applied, and only to the normalized/search
copy of the text:

| Raw text | Normalized text | Record |
|---|---|---|
| `"Decrease of love. Jealously"` | `"...jealousy"` (not "jealously") | id 3, Rose, Yellow |

`historical_meaning` for id 3 uses the adjective "Jealously" where the
noun "Jealousy" was clearly intended. The **raw** field is left exactly
as supplied (so it's still recoverable and displayed as-is on the
flower detail page); the **normalized** copy used for search has this
one correction applied, via an explicit dictionary in
`backend/app/database/pipeline.py`:

```python
SPELLING_CORRECTIONS = {"jealously": "jealousy"}
```

No other normalization beyond lowercasing and whitespace collapsing is
applied anywhere. In particular, punctuation inside meanings (e.g.
`"Purity. Sweetness"`, `"Fidelity. Marriage"`) is preserved in both raw
and normalized text — see the "Data cleaning philosophy" note in
docs/SEARCH_METHODOLOGY.md for why.

## Validation rules (`backend/app/database/pipeline.py: validate()`)

Before any cleaning happens, the raw CSV is checked for:

- all 5 required columns present
- every `id` is a valid integer
- no duplicate `id` values
- no duplicate `flower` values
- no missing/blank values in any of the 5 required columns

The current dataset passes all of these (see
`data/processed/data_quality_report.json`, regenerated every time
`build_database.py` runs). If a future dataset revision fails
validation, `build_database.py` stops and prints exactly what's wrong
rather than loading partial or invalid data.

## Dataset characteristics (measured, not hard-coded)

As of the current 30-record dataset (see `/api/analytics` for the live,
always-current version of this table):

| Category | Count |
|---|---|
| Love | 12 |
| Remembrance | 3 |
| Character | 3 |
| Hope | 2 |
| Commitment | 2 |
| Farewell | 2 |
| Negative emotion | 1 |
| Affection | 1 |
| Rejection | 1 |
| Admiration | 1 |
| Emotion | 1 |
| Friendship | 1 |

## Dataset version

Version 1 — the initial 30-record CSV supplied for this project. The
pipeline and schema make no assumption that this stays at 30 records or
12 categories (spec section 57) — `build_database.py` re-derives
everything from whatever CSV is in `data/raw/`.
