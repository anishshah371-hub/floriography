"""Tests for preprocessing, keyword search, TF-IDF search, ranking,
and evaluation. Runs against the real 30-record database built by
backend/app/database/build_database.py -- run that first if
data/processed/floriography.db doesn't exist yet.

Run from the project root:

    python -m unittest tests.test_nlp -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import connection, repository  # noqa: E402
from app.nlp import evaluation, keyword_search, preprocessing, ranking, tfidf_search  # noqa: E402

DB_PATH = str(PROJECT_ROOT / "data" / "processed" / "floriography.db")


class TestPreprocessing(unittest.TestCase):
    def test_normalize_lowercases_and_collapses_whitespace(self):
        self.assertEqual(preprocessing.normalize_text("  Rose   RED "), "rose red")

    def test_normalize_preserves_punctuation(self):
        self.assertEqual(preprocessing.normalize_text("Purity. Sweetness"), "purity. sweetness")

    def test_tokenize_strips_punctuation(self):
        self.assertEqual(preprocessing.tokenize("Rose, Red"), ["rose", "red"])

    def test_tokenize_keeps_short_words(self):
        # No stopword removal by design -- "i" must survive.
        self.assertIn("i", preprocessing.tokenize("I love you"))


class TestWithRealDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conn = connection.get_connection(DB_PATH)
        cls.records = repository.get_all_search_records(conn)
        conn.close()
        cls.index = tfidf_search.build_index(cls.records)

    def test_30_records_loaded(self):
        self.assertEqual(len(self.records), 30)

    def test_keyword_search_finds_exact_phrase_match(self):
        results = keyword_search.search("I feel shy and embarrassed", self.records, top_k=5)
        self.assertTrue(results)
        self.assertEqual(results[0].flower.flower, "Peony")

    def test_keyword_search_empty_query_returns_empty(self):
        self.assertEqual(keyword_search.search("", self.records), [])

    def test_tfidf_search_beats_keyword_on_friendship_query(self):
        # The documented case where raw keyword overlap fails and
        # TF-IDF succeeds -- see docs/EVALUATION.md.
        query = "I want to express friendship"
        kw_top = keyword_search.search(query, self.records, top_k=5)
        tf_top = tfidf_search.search(query, self.index, top_k=5)

        kw_ids = [r.flower.id for r in kw_top]
        tf_ids = [r.flower.id for r in tf_top]

        self.assertNotIn(30, kw_ids)       # Acacia missing from the baseline's top 5
        self.assertEqual(tf_ids[0], 30)    # but ranked #1 by TF-IDF

    def test_tfidf_scores_are_bounded(self):
        for r in tfidf_search.search("I love you", self.index, top_k=10):
            self.assertGreaterEqual(r.score, 0.0)
            self.assertLessEqual(r.score, 1.0 + 1e-9)

    def test_tfidf_matched_terms_are_real_overlap(self):
        results = tfidf_search.search("I feel shy and embarrassed", self.index, top_k=1)
        matched = set(results[0].matched_terms)
        query_tokens = set(preprocessing.tokenize("I feel shy and embarrassed"))
        record_tokens = set(preprocessing.tokenize(results[0].flower.search_text))
        # Every reported matched term must actually be in both the
        # query and the record -- never fabricated.
        self.assertTrue(matched <= query_tokens)
        self.assertTrue(matched <= record_tokens)

    def test_ranking_explanation_reflects_matched_terms(self):
        results = tfidf_search.search("I feel shy and embarrassed", self.index, top_k=1)
        result_dict = ranking.to_result_dict(results[0], rank=1)
        for term in result_dict["matched_terms"]:
            self.assertIn(term, result_dict["explanation"])

    def test_no_strong_match_returns_empty_not_fabricated(self):
        results = tfidf_search.search("zzqxxnonsensequery asdkjaslkdj", self.index, top_k=5)
        self.assertEqual(results, [])


class TestEvaluation(unittest.TestCase):
    def test_precision_recall_hit_rate_mrr_basic_cases(self):
        self.assertEqual(evaluation.precision_at_k([1, 2, 3], {1, 3}, k=3), 2 / 3)
        self.assertEqual(evaluation.recall_at_k([1, 2, 3], {1, 3, 5}, k=3), 2 / 3)
        self.assertEqual(evaluation.hit_rate_at_k([2, 4, 6], {1, 3}, k=3), 0.0)
        self.assertEqual(evaluation.reciprocal_rank([2, 4, 6], {6}), 1 / 3)

    def test_tfidf_beats_keyword_on_real_eval_set(self):
        conn = connection.get_connection(DB_PATH)
        records = repository.get_all_search_records(conn)
        conn.close()
        index = tfidf_search.build_index(records)

        kw = evaluation.evaluate(lambda q: keyword_search.search(q, records, top_k=5), k=5, method_name="keyword")
        tf = evaluation.evaluate(lambda q: tfidf_search.search(q, index, top_k=5), k=5, method_name="tfidf")

        self.assertGreaterEqual(tf.mrr, kw.mrr)
        self.assertGreaterEqual(tf.mean_recall, kw.mean_recall)


if __name__ == "__main__":
    unittest.main()
