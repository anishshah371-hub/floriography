# Search Methodology

This document explains how flower search and meaning search actually
work — the level of detail meant to be defensible line-by-line in a
technical interview.

## Flower search (`GET /api/flowers/search`)

Retrieval, not ranking — the input is a flower name, and matching is
tolerant of case, punctuation, and word order (spec section 9):

1. **Normalized exact match**: lowercase + whitespace-collapse the
   query, compare to `normalized_flower`.
2. **Substring match**: `normalized_flower LIKE '%query%'` — this is
   why `"rose"` finds every Rose variant plus Rosemary.
3. **Token match** (fallback): tokenize both the query and each
   record's name (splitting on anything that isn't a letter/digit, so
   punctuation is ignored), and match if every query token appears
   among the record's tokens, in any order. This step exists because
   step 2 fails on a query like `"ROSE RED"` — there's no comma in the
   query, so it's never a literal substring of `"rose, red"`. Token
   matching finds `{rose, red} ⊆ {rose, red}` regardless of the comma
   or word order, so `"ROSE RED"` and `"red rose"` both resolve to
   `Rose, Red`. (This exact gap was caught by
   `tests/test_database.py::test_search_by_name_tolerant` during
   development — see "Known limitations" in the README for how it was
   found and fixed.)

No fabrication: if none of the three steps match anything, the
endpoint returns an empty result list, never an invented record.

## Meaning search (`GET /api/search/meaning`)

This is the project's core NLP component. Two methods are implemented
so the improvement from one to the other can actually be measured
(spec section 29), not just asserted.

### Baseline: keyword overlap (`app/nlp/keyword_search.py`)

Tokenize the query and a record's `search_text` (lowercase, split on
non-alphanumeric characters — no stemming, no stopword removal, see
"Design choices" below), then score by **Jaccard similarity**:

```
score = |query_tokens ∩ record_tokens| / |query_tokens ∪ record_tokens|
```

Every shared word counts equally. That's the baseline's weakness —
see the friendship example below.

### Primary method: TF-IDF + cosine similarity (`app/nlp/tfidf_search.py`)

- **Term Frequency (TF)**: how often a word appears within one
  record's `search_text`.
- **Inverse Document Frequency (IDF)**: `log` of (total records ÷
  records containing the word). A word in almost every record (like
  "i") gets a low IDF; a word in only one or two records (like
  "friendship") gets a high one.
- **TF-IDF** = TF × IDF, computed per word per record, giving each
  record a vector over the full vocabulary (129 terms across this
  dataset).
- **Cosine similarity** measures the angle between the query's TF-IDF
  vector and each record's vector: 1.0 = same direction (very similar
  weighted-term content), 0.0 = no shared vocabulary at all.

Implementation: `sklearn.feature_extraction.text.TfidfVectorizer`,
fit **once** over all 30 records' `search_text` (`build_index`,
triggered by `python -m app.nlp.build_artifacts`, pickled to
`artifacts/tfidf_index.pkl`), then reused for every query via
`.transform()` — never refit per request. `sklearn.metrics.pairwise.
cosine_similarity` ranks records against the fitted matrix.

`token_pattern` is set to match `app/nlp/preprocessing.py`'s own
tokenizer exactly (`[a-z0-9]+`, `lowercase=False` since the text is
already normalized), so a "matched term" means the same thing whether
it's reported by the keyword method or the TF-IDF method.

### Why TF-IDF over raw keyword overlap — a measured example

Query: **"I want to express friendship"**

| Method | Rank 1 result | Why |
|---|---|---|
| Keyword (Jaccard) | Rose, Red (0.364) | Shares "i / to / want / express" — common words, not actually about friendship |
| TF-IDF (cosine) | **Acacia (0.460)** | The only word both texts share with real weight is "friendship" itself — a rare, distinctive word in this vocabulary |

Acacia doesn't even appear in the keyword baseline's top 5. This isn't
a cherry-picked example — it's exactly why IDF weighting exists: common
words are automatically down-weighted instead of needing a hand-built
stopword list. See `docs/EVALUATION.md` for the full 8-query comparison.

### Why NOT semantic embeddings (yet)

Spec sections 10/29/30 are explicit that embeddings should only be
added if they measurably help. With 30 records and short (20-60
character) documented meanings, TF-IDF already achieves 0.812 MRR
(docs/EVALUATION.md) using a fully transparent, zero-dependency-beyond-
scikit-learn method that's straightforward to explain term-by-term. An
embedding model would add a real dependency, a real latency cost, and
a much harder-to-inspect similarity score, for a dataset this small and
this literal (most records use the word they mean — "friendship",
"hope", "shy" — rather than metaphor an embedding model would be needed
to bridge). The architecture (a swappable `method` parameter already
in `search_service.search_meaning`) supports adding an embedding-based
method later and comparing it against this baseline the same way
TF-IDF was compared against keyword overlap — but it isn't justified
yet.

### Explanations (`app/nlp/ranking.py`)

Every result's `matched_terms` is the actual set of vocabulary terms
with non-zero TF-IDF weight in **both** the query and that specific
record (sorted by how much each term contributed to the score) — never
a fabricated or generic list. `explanation` is a single templated
sentence built directly from that list: `"Matched because the
documented meaning shares these terms with your query: {terms}."` If
there are no shared terms, there is no result — see the similarity
threshold below.

### No-match handling and the similarity threshold

Results below `MIN_SIMILARITY_SCORE = 0.1` (`app/config/settings.py`)
are dropped before the API ever returns them, rather than shown as a
low-confidence "match". This threshold was chosen by inspecting the
actual score distribution across the 8-query evaluation set: scores
cluster at 0.057-0.059 for single-common-word overlaps (noise) and
jump to 0.165+ for anything with a genuinely shared content word — 0.1
sits in that gap. If every result for a query is dropped, the API
returns `"results": []` with `message: "No strong documented matches
were found for this query."` — never a fabricated recommendation.

## Data cleaning philosophy

Aggressive NLP preprocessing (stemming, lemmatization, stopword
removal) was deliberately **not** applied. Trade-off, made explicit:

- **Pro**: every match is traceable to an exact surface word; nothing
  is fabricated or inferred by a preprocessing step a reader can't see
  in the record's own text.
- **Con, measured**: query **"I want to reject someone's feelings"**
  fails to retrieve `Carnation, Striped` (id 18, "I am rejecting your
  proposal or feelings") with either method — "reject" (query) and
  "rejecting" (record) are different surface tokens with no stemming
  to unify them. See docs/EVALUATION.md and the README's "Known
  limitations" for this exact, measured failure case and what would
  fix it.

This is a real, demonstrated cost of a real, documented design choice
— not a hidden gap.
