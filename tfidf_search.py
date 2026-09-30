"""TF-IDF + cosine similarity retrieval -- the "improved" method in the
baseline-vs-improved comparison (docs/EVALUATION.md).

Term frequency (TF): how often a word appears in one record's
search_text. Inverse document frequency (IDF): words that appear in
most of the 30 records (like "i" or "love") get a LOW weight; words
that appear in only a few records (like "friendship" or "bashfulness")
get a HIGH weight. TF-IDF is TF times IDF -- so a shared word only
drives up similarity when it's actually distinctive, unlike raw
keyword overlap (keyword_search.py) where every shared word counts
equally. Cosine similarity then measures the angle between the
query's TF-IDF vector and each record's TF-IDF vector: 1.0 means
identical term-weight direction, 0.0 means no shared terms at all.

The vectorizer is fit ONCE (build_index, called at startup / via
build_artifacts.py) and reused for every query -- never refit per
request (spec section 12).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.database.models import Flower
from app.nlp.preprocessing import tokenize

# Same token definition as keyword_search.py's tokenizer, so a term
# either method reports as "matched" means the same thing in both.
# lowercase=False because search_text is already normalized upstream.
TOKEN_PATTERN = r"[a-z0-9]+"


@dataclass
class TfidfIndex:
    vectorizer: TfidfVectorizer
    matrix: "np.ndarray"  # sparse matrix, n_records x n_terms
    records: list[Flower]  # matrix row i corresponds to records[i]


@dataclass
class TfidfResult:
    flower: Flower
    score: float  # cosine similarity, in [0, 1] for non-negative TF-IDF vectors
    matched_terms: list[str]


def build_index(records: list[Flower]) -> TfidfIndex:
    texts = [r.search_text for r in records]
    vectorizer = TfidfVectorizer(lowercase=False, token_pattern=TOKEN_PATTERN)
    matrix = vectorizer.fit_transform(texts)
    return TfidfIndex(vectorizer=vectorizer, matrix=matrix, records=records)


def _matched_terms(vectorizer: TfidfVectorizer, query_vec, doc_vec) -> list[str]:
    """Terms with non-zero TF-IDF weight in BOTH the query and the
    document -- real evidence for why the score is what it is, sorted
    by how much each term actually contributed (query_w * doc_w)."""
    q = query_vec.toarray().ravel()
    d = doc_vec.toarray().ravel()
    contribution = q * d
    nonzero = np.nonzero(contribution)[0]
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(nonzero, key=lambda i: contribution[i], reverse=True)
    return [terms[i] for i in ranked]


def search(query: str, index: TfidfIndex, top_k: int = 5) -> list[TfidfResult]:
    if not tokenize(query):
        return []

    query_vec = index.vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, index.matrix).ravel()

    ranked_idx = np.argsort(similarities)[::-1]
    results = []
    for i in ranked_idx[:top_k]:
        score = float(similarities[i])
        if score <= 0:
            continue
        doc_vec = index.matrix[i]
        results.append(
            TfidfResult(
                flower=index.records[i],
                score=score,
                matched_terms=_matched_terms(index.vectorizer, query_vec, doc_vec),
            )
        )
    return results
