"""Retrieval evaluation: precision@k, recall@k, hit-rate@k, and MRR,
measured against a small hand-curated relevance set built directly
from the 30 supplied records (spec section 28).

Every relevance judgment is justified by the record's own
historical_meaning / human_language_meaning / communication_category
-- see the comment above each entry. Borderline cases (a record that
is thematically close but doesn't use matching documented language)
are deliberately left OUT rather than guessed in either direction --
see docs/EVALUATION.md for the specific judgment calls.
"""

from __future__ import annotations

from dataclasses import dataclass

EVAL_SET: list[tuple[str, set[int]]] = [
    ("I want to express romantic love", {1, 7, 19, 15}),
    # 1 Rose,Red: "Declaration of love" / "express romantic love" (near-exact wording)
    # 7 Tulip,Red: "Declaration of love" / "openly declaring my love"
    # 19 Chrysanthemum,Red: "I love" / "directly telling you that I love you"
    # 15 Myrtle: "Love" / "expressing love and affection"
    ("I want to express friendship", {30}),
    # 30 Acacia: "Friendship" / "value our friendship" -- the only Friendship-category record
    ("I want to say goodbye", {23, 24}),
    # 23 Sweet Pea: "Departure" / "saying goodbye or announcing my departure"
    # 24 Daisy, Michaelmas: "Farewell" / "saying goodbye"
    ("I want to remember someone", {4, 21, 22}),
    # 4 Forget Me Not: "...forget me not" / "want you to remember me"
    # 21 Pansy: "Thoughts" / "You are in my thoughts"
    # 22 Rosemary: "Remembrance" / "remember you...to be remembered"
    ("I want to show loyalty and faithfulness", {5, 13, 14, 25}),
    # 5 Violet,Blue: "Faithfulness" / "faithful and loyal"
    # 13 Heliotrope: "Devotion. Faithfulness" / "devoted and faithful"
    # 14 Ivy: "Fidelity. Marriage" / "loyalty, lasting commitment"
    # 25 Wall-flower: "Fidelity in adversity" / "remain loyal...difficult"
    ("I feel shy and embarrassed", {28}),
    # 28 Peony: "Shame. Bashfulness" / "feel shy or embarrassed" (near-exact wording)
    ("I want to send a message of hope", {29, 11}),
    # 29 Snowdrop: "Hope" / "sending you a message of hope" (near-exact wording)
    # 11 Lily of the Valley: category Hope, "Return of happiness"
    ("I want to reject someone's feelings", {18}),
    # 18 Carnation,Striped: "Refusal" / "rejecting your proposal or feelings" (near-exact wording)
]


def precision_at_k(retrieved_ids: list[int], relevant_ids: set[int], k: int) -> float:
    top_k = retrieved_ids[:k]
    return sum(1 for i in top_k if i in relevant_ids) / len(top_k) if top_k else 0.0


def recall_at_k(retrieved_ids: list[int], relevant_ids: set[int], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    return sum(1 for i in top_k if i in relevant_ids) / len(relevant_ids)


def hit_rate_at_k(retrieved_ids: list[int], relevant_ids: set[int], k: int) -> float:
    return 1.0 if any(i in relevant_ids for i in retrieved_ids[:k]) else 0.0


def reciprocal_rank(retrieved_ids: list[int], relevant_ids: set[int]) -> float:
    for rank, i in enumerate(retrieved_ids, start=1):
        if i in relevant_ids:
            return 1.0 / rank
    return 0.0


@dataclass
class EvalSummary:
    method: str
    k: int
    mean_precision: float
    mean_recall: float
    mean_hit_rate: float
    mrr: float
    per_query: list[dict]


def evaluate(search_fn, k: int = 5, method_name: str = "") -> EvalSummary:
    """search_fn(query) -> ordered list of results, each with .flower.id"""
    per_query = []
    precisions, recalls, hit_rates, rr = [], [], [], []

    for query, relevant_ids in EVAL_SET:
        results = search_fn(query)
        retrieved_ids = [r.flower.id for r in results]

        p = precision_at_k(retrieved_ids, relevant_ids, k)
        r = recall_at_k(retrieved_ids, relevant_ids, k)
        h = hit_rate_at_k(retrieved_ids, relevant_ids, k)
        m = reciprocal_rank(retrieved_ids, relevant_ids)

        precisions.append(p); recalls.append(r); hit_rates.append(h); rr.append(m)
        per_query.append({
            "query": query,
            "relevant_ids": sorted(relevant_ids),
            "retrieved_ids": retrieved_ids[:k],
            "precision": round(p, 3),
            "recall": round(r, 3),
            "hit": h == 1.0,
            "reciprocal_rank": round(m, 3),
        })

    n = len(EVAL_SET)
    return EvalSummary(
        method=method_name,
        k=k,
        mean_precision=round(sum(precisions) / n, 3),
        mean_recall=round(sum(recalls) / n, 3),
        mean_hit_rate=round(sum(hit_rates) / n, 3),
        mrr=round(sum(rr) / n, 3),
        per_query=per_query,
    )
