"""Pipeline entry point: raw CSV -> validate -> clean -> processed CSV
+ SQLite database.

Run from the backend/ directory:

    python -m app.database.build_database

Re-run any time data/raw/ changes -- it is fully reproducible and
always rebuilds data/processed/ and the database from the raw CSV
(never the other way around).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# floriography/backend/app/database/build_database.py -> floriography/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "sample_for_floriography.csv"
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "flowers_processed.csv"
QUALITY_REPORT = PROJECT_ROOT / "data" / "processed" / "data_quality_report.json"
DB_PATH = PROJECT_ROOT / "data" / "processed" / "floriography.db"

sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import connection, pipeline, repository  # noqa: E402


def main() -> None:
    print(f"Loading raw CSV: {RAW_CSV}")
    df = pipeline.load_raw(str(RAW_CSV))

    report = pipeline.validate(df)
    print(report.summary())
    if not report.is_valid:
        print("Validation failed -- stopping. Fix data/raw/ and re-run.")
        sys.exit(1)

    processed, transformation_log = pipeline.clean(df)

    PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(PROCESSED_CSV, index=False)
    print(f"Wrote processed CSV: {PROCESSED_CSV} ({len(processed)} rows)")

    quality_report = {
        "row_count": report.row_count,
        "is_valid": report.is_valid,
        "duplicate_ids": report.duplicate_ids,
        "invalid_ids": report.invalid_ids,
        "missing_values": report.missing_values,
        "duplicate_flower_name_rows": report.duplicate_flower_rows,
        "transformations_applied": transformation_log,
    }
    QUALITY_REPORT.write_text(json.dumps(quality_report, indent=2))
    print(f"Wrote data-quality report: {QUALITY_REPORT}")

    conn = connection.get_connection(str(DB_PATH))
    connection.init_schema(conn)
    inserted = repository.insert_flowers(conn, processed.to_dict(orient="records"))
    print(f"Inserted/replaced {inserted} rows into {DB_PATH}")

    count = repository.count_all(conn)
    categories = repository.get_categories(conn)
    print(f"DB now has {count} rows across {len(categories)} categories.")
    conn.close()


if __name__ == "__main__":
    main()
