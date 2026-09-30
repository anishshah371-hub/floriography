# Evaluation

Reproducible by running:

```
cd backend
python -m app.nlp.run_evaluation
```

which writes `docs/evaluation_results.json` (the source of every
number in this file) and is exercised by
`tests/test_nlp.py::TestEvaluation`.

## Evaluation set

8 natural-language queries, each with a relevant-record set justified
directly from the dataset's own `historical_meaning` /
`human_language_meaning` / `communication_category` text (spec section
28 — no ground truth invented beyond what the records themselves say).
Full reasoning for every judgment lives as comments in
`backend/app/nlp/evaluation.py`; summarized:

| Query | Relevant ids | Justification |
|---|---|---|
| "I want to express romantic love" | 1, 7, 15, 19 | Each explicitly says "declaration of love" / "I love you" / "romantic" |
| "I want to express friendship" | 30 | Only Friendship-category record; says "friendship" verbatim |
| "I want to say goodbye" | 23, 24 | Both explicitly "departure" / "farewell" / "goodbye" |
| "I want to remember someone" | 4, 21, 22 | Explicitly "remember me" / "in my thoughts" / "remembrance" |
| "I want to show loyalty and faithfulness" | 5, 13, 14, 25 | Each explicitly "faithful" / "fidelity" / "loyal" |
| "I feel shy and embarrassed" | 28 | Explicitly "shame, bashfulness" / "shy or embarrassed" |
| "I want to send a message of hope" | 11, 29 | Category Hope; 29 also says "message of hope" verbatim |
| "I want to reject someone's feelings" | 18 | Explicitly "refusal" / "rejecting your proposal or feelings" |

Borderline cases were deliberately left **out** rather than guessed in
either direction — e.g. Jonquil ("I desire a return of affection") was
not marked relevant for an "express affection" query, because
*wanting affection back* and *expressing* it are different documented
intents; including it would have been a judgment the dataset doesn't
actually support.

## Metrics, k=5

| Method | Precision@5 | Recall@5 | Hit Rate@5 | MRR |
|---|---|---|---|---|
| Keyword overlap (baseline) | 0.225 | 0.490 | 0.750 | 0.667 |
| **TF-IDF + cosine (primary)** | **0.275** | **0.646** | **0.875** | **0.812** |

TF-IDF wins on every metric. The largest gap is recall (+0.156) and
MRR (+0.145) — consistent with TF-IDF's main advantage being *ranking*
relevant-but-not-exact-wording records higher, and surfacing at least
one relevant record in more queries (7/8 vs 6/8 hit rate).

## Where they disagree

**"I want to express friendship"** — the clearest case, and not
cherry-picked (it's query 2 of 8, run in the same fixed order as every
other query):

| | Retrieved top 5 (ids) | Acacia (id 30) rank | Precision | Recall | RR |
|---|---|---|---|---|---|
| Keyword | [1, 22, 16, 4, 5] | **not in top 5** | 0.0 | 0.0 | 0.0 |
| TF-IDF | [30, 1, 22, 16, 4] | **1** | 0.2 | 1.0 | 1.0 |

The keyword baseline ranks results by shared words including "i",
"to", "want" — present in nearly every record, so they contribute
nothing distinctive but still count equally in Jaccard overlap.
TF-IDF's IDF term down-weights exactly those words and rewards the one
genuinely rare, shared word: "friendship".

**"I want to reject someone's feelings"** — both methods fail (hit =
false, rank 22 not-relevant "Rosemary" leads for keyword; the relevant
Carnation-Striped record, id 18, doesn't appear in either top 5). Root
cause, confirmed by inspecting tokens directly: the query contains
"reject" and the record's text contains "rejecting" / "Refusal" /
"Rejection" — different surface word forms, and this project
deliberately does not stem or lemmatize (see
docs/SEARCH_METHODOLOGY.md's "Data cleaning philosophy"). This is a
real, measured limitation of that design choice, not a bug — see the
README's "Known limitations".

## Baseline vs. improved: is TF-IDF actually justified here?

Yes, measurably (MRR 0.667 → 0.812, a real 22% relative improvement,
achieved with a well-understood, standard-library-adjacent technique
and no added runtime dependency beyond scikit-learn, which was already
in the approved stack). Embeddings were not attempted for this
iteration — see docs/SEARCH_METHODOLOGY.md for why a 30-record,
mostly-literal-language dataset doesn't yet justify that additional
complexity, and how the architecture leaves room to add and re-evaluate
it later without restructuring anything.

## Limitations of this evaluation itself

- 8 queries is a small evaluation set — enough to demonstrate and
  measure a real difference between two methods, not enough to
  produce a statistically rigorous estimate of production-grade
  retrieval quality. This is disclosed, not hidden.
- Relevance judgments are single-annotator (this project's author),
  though every judgment is tied to an explicit quote from the record.
- Recall@5 is capped by `k=5` when a query's relevant set is smaller
  than 5 (most are) — a query with only 1 truly relevant record can
  reach recall 1.0 easily; this is normal for Recall@k with small
  relevant-sets, not an artifact of anything else.
