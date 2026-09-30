"""Runs the baseline-vs-improved evaluation (evaluation.py) against the
real database and writes the results to docs/evaluation_results.json.

Run from backend/:

    python -m app.nlp.run_evaluation

This is what produced the numbers quoted in docs/EVALUATION.md -- if
the dataset changes, re-run this and update that doc.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = PROJECT_ROOT / "docs" / "evaluation_results.json"

sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import connection, repository  # noqa: E402
from app.nlp import evaluation, keyword_search, tfidf_search  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "processed" / "floriography.db"


def main() -> None:
    conn = connection.get_connection(str(DB_PATH))
    records = repository.get_all_search_records(conn)
    index = tfidf_search.build_index(records)
    conn.close()

    keyword_fn = lambda q: keyword_search.search(q, records, top_k=5)
    tfidf_fn = lambda q: tfidf_search.search(q, index, top_k=5)

    kw = evaluation.evaluate(keyword_fn, k=5, method_name="keyword (baseline)")
    tf = evaluation.evaluate(tfidf_fn, k=5, method_name="tfidf (improved)")

    for s in (kw, tf):
        print(f"{s.method:<22} P@5={s.mean_precision}  R@5={s.mean_recall}  HitRate@5={s.mean_hit_rate}  MRR={s.mrr}")

    OUT_PATH.write_text(json.dumps({"keyword": asdict(kw), "tfidf": asdict(tf)}, indent=2))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
