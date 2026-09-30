"""Tests for the data pipeline and database layer. Pure stdlib
unittest + pandas/sqlite3 -- no FastAPI needed, so these run in any
environment with the backend/requirements.txt installed (or, as here,
with just pandas + scikit-learn available).

Run from the project root:

    python -m unittest tests.test_database -v
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import connection, pipeline, repository  # noqa: E402

REQUIRED_COLUMNS = pipeline.REQUIRED_COLUMNS


class TestValidation(unittest.TestCase):
    def test_real_dataset_is_valid(self):
        df = pipeline.load_raw(str(PROJECT_ROOT / "data" / "raw" / "sample_for_floriography.csv"))
        report = pipeline.validate(df)
        self.assertTrue(report.is_valid, report.summary())
        self.assertEqual(report.row_count, 30)

    def test_missing_column_is_caught(self):
        df = pd.DataFrame({"id": [1], "flower": ["Rose"]})  # missing 3 required columns
        report = pipeline.validate(df)
        self.assertFalse(report.is_valid)
        self.assertTrue(report.missing_columns)

    def test_duplicate_id_is_caught(self):
        df = pd.DataFrame({
            "id": [1, 1],
            "flower": ["Rose", "Tulip"],
            "historical_meaning": ["a", "b"],
            "human_language_meaning": ["a", "b"],
            "communication_category": ["Love", "Love"],
        })
        report = pipeline.validate(df)
        self.assertFalse(report.is_valid)
        self.assertIn(1, report.duplicate_ids)

    def test_missing_value_is_caught(self):
        df = pd.DataFrame({
            "id": [1],
            "flower": ["Rose"],
            "historical_meaning": [""],  # blank
            "human_language_meaning": ["a"],
            "communication_category": ["Love"],
        })
        report = pipeline.validate(df)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.missing_values["historical_meaning"], [1])


class TestCleaning(unittest.TestCase):
    def setUp(self):
        self.df = pipeline.load_raw(str(PROJECT_ROOT / "data" / "raw" / "sample_for_floriography.csv"))
        self.processed, self.log = pipeline.clean(self.df)

    def test_raw_display_text_is_unchanged(self):
        raw_row = self.df[self.df["id"] == 3].iloc[0]
        processed_row = self.processed[self.processed["id"] == 3].iloc[0]
        self.assertEqual(raw_row["historical_meaning"], processed_row["historical_meaning"])
        self.assertEqual(processed_row["historical_meaning"], "Decrease of love. Jealously")

    def test_spelling_correction_applied_to_normalized_only(self):
        row = self.processed[self.processed["id"] == 3].iloc[0]
        self.assertIn("jealousy", row["normalized_historical_meaning"])
        self.assertNotIn("jealously", row["normalized_historical_meaning"])

    def test_search_text_excludes_flower_name(self):
        row = self.processed[self.processed["id"] == 30].iloc[0]  # Acacia
        self.assertNotIn("acacia", row["search_text"])
        self.assertIn("friendship", row["search_text"])

    def test_meaningful_punctuation_preserved_in_display_text(self):
        row = self.processed[self.processed["id"] == 10].iloc[0]  # Lily, White
        self.assertEqual(row["historical_meaning"], "Purity. Sweetness")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmpdir.name) / "test.db")
        df = pipeline.load_raw(str(PROJECT_ROOT / "data" / "raw" / "sample_for_floriography.csv"))
        processed, _ = pipeline.clean(df)
        conn = connection.get_connection(self.db_path)
        connection.init_schema(conn)
        repository.insert_flowers(conn, processed.to_dict(orient="records"))
        conn.close()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _conn(self) -> sqlite3.Connection:
        return connection.get_connection(self.db_path)

    def test_all_30_rows_present(self):
        conn = self._conn()
        self.assertEqual(repository.count_all(conn), 30)
        conn.close()

    def test_get_by_id(self):
        conn = self._conn()
        f = repository.get_by_id(conn, 1)
        self.assertEqual(f.flower, "Rose, Red")
        self.assertIsNone(repository.get_by_id(conn, 999))
        conn.close()

    def test_search_by_name_tolerant(self):
        conn = self._conn()
        for query, expected_count in [("rose", 4), ("ROSE RED", 1), ("red rose", 1), ("Rose, Red", 1)]:
            with self.subTest(query=query):
                self.assertEqual(len(repository.search_by_name(conn, query)), expected_count)
        self.assertEqual(repository.search_by_name(conn, "nonexistentflowerxyz"), [])
        conn.close()

    def test_category_distribution_matches_known_counts(self):
        conn = self._conn()
        dist = repository.get_category_distribution(conn)
        self.assertEqual(dist["Love"], 12)
        self.assertEqual(sum(dist.values()), 30)
        self.assertEqual(len(dist), 12)
        conn.close()

    def test_category_filter(self):
        conn = self._conn()
        records, total = repository.get_all(conn, category="Friendship"), repository.count_all(conn, category="Friendship")
        self.assertEqual(total, 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].flower, "Acacia")
        conn.close()


if __name__ == "__main__":
    unittest.main()
