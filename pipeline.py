"""Raw-CSV -> validated -> cleaned data pipeline.

Pure pandas/stdlib -- no web-framework dependency, so this module can
be imported and unit-tested (and run as a script) without FastAPI
installed.

Design choices, documented here because they matter for the interview:

- The RAW csv is never modified. Cleaning produces a *separate*
  processed file with extra normalized_* / search_text columns; the
  original display text (flower, historical_meaning,
  human_language_meaning, communication_category) is carried through
  unchanged into the processed file too, so nothing about "what the
  dataset actually says" is lost or silently rewritten.
- Only ONE explicit, documented spelling fix is applied, and only to
  the normalized/search copy of the text -- see SPELLING_CORRECTIONS
  below. Nothing else is "cleaned" -- meaningful punctuation like
  "Purity. Sweetness" is preserved verbatim in both raw and processed
  display fields (see the module docstring in nlp/preprocessing.py for
  why aggressive cleaning is avoided).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.nlp.preprocessing import normalize_text

REQUIRED_COLUMNS = [
    "id",
    "flower",
    "historical_meaning",
    "human_language_meaning",
    "communication_category",
]

# Explicit, documented, single-purpose spelling corrections applied ONLY
# to the normalized/search text (never to the raw display text). Keys
# and values are lowercase because this is applied after lowercasing.
# Add to this dict (and to docs/DATA_DICTIONARY.md) if a future dataset
# revision introduces a similar issue -- do not silently "fix" things
# that aren't listed here.
SPELLING_CORRECTIONS = {
    "jealously": "jealousy",  # "Decrease of love. Jealously" (id 3) -- adjective used where the noun was intended
}


@dataclass
class ValidationReport:
    row_count: int
    missing_columns: list[str] = field(default_factory=list)
    duplicate_ids: list[int] = field(default_factory=list)
    invalid_ids: list = field(default_factory=list)
    missing_values: dict = field(default_factory=dict)  # column -> [row ids]
    duplicate_flower_rows: list[int] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (
            self.missing_columns
            or self.duplicate_ids
            or self.invalid_ids
            or any(self.missing_values.values())
        )

    def summary(self) -> str:
        if self.is_valid:
            return f"VALID -- {self.row_count} rows, no blocking issues."
        lines = [f"INVALID -- {self.row_count} rows"]
        if self.missing_columns:
            lines.append(f"  missing columns: {self.missing_columns}")
        if self.duplicate_ids:
            lines.append(f"  duplicate ids: {self.duplicate_ids}")
        if self.invalid_ids:
            lines.append(f"  invalid ids: {self.invalid_ids}")
        for col, rows in self.missing_values.items():
            if rows:
                lines.append(f"  missing '{col}' at ids: {rows}")
        return "\n".join(lines)


def load_raw(path: str) -> pd.DataFrame:
    """Read the raw CSV exactly as supplied (utf-8-sig strips the BOM)."""
    return pd.read_csv(path, encoding="utf-8-sig")


def validate(df: pd.DataFrame) -> ValidationReport:
    """Check the raw dataframe. Never raises -- returns a report the
    caller decides what to do with (build_database.py stops on
    is_valid=False rather than silently continuing, per spec section 26)."""
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        return ValidationReport(row_count=len(df), missing_columns=missing_columns)

    invalid_ids = []
    for v in df["id"]:
        try:
            if int(v) != v and not float(v).is_integer():
                invalid_ids.append(v)
        except (ValueError, TypeError):
            invalid_ids.append(v)

    duplicate_ids = df["id"][df["id"].duplicated(keep=False)].unique().tolist()

    missing_values = {}
    for col in REQUIRED_COLUMNS:
        blank = df[col].isna() | (df[col].astype(str).str.strip() == "")
        missing_values[col] = df.loc[blank, "id"].tolist()

    duplicate_flower_rows = (
        df["id"][df.duplicated(subset=["flower"], keep=False)].tolist()
    )

    return ValidationReport(
        row_count=len(df),
        duplicate_ids=duplicate_ids,
        invalid_ids=invalid_ids,
        missing_values=missing_values,
        duplicate_flower_rows=duplicate_flower_rows,
    )


def _apply_spelling_corrections(text: str) -> str:
    words = text.split(" ")
    corrected = [SPELLING_CORRECTIONS.get(w, w) for w in words]
    return " ".join(corrected)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return (processed_df, transformation_log). Raw display columns
    are carried through unchanged; normalized_* and search_text are
    added."""
    out = df.copy()
    log = []

    out["normalized_flower"] = out["flower"].map(normalize_text)
    out["normalized_historical_meaning"] = out["historical_meaning"].map(normalize_text).map(_apply_spelling_corrections)
    out["normalized_human_language_meaning"] = out["human_language_meaning"].map(normalize_text)
    out["normalized_communication_category"] = out["communication_category"].map(normalize_text)

    log.append(
        "Added normalized_flower, normalized_historical_meaning, "
        "normalized_human_language_meaning, normalized_communication_category "
        "(lowercased, whitespace-collapsed copies of the raw display columns)."
    )

    changed = out.loc[
        out["normalized_historical_meaning"]
        != out["historical_meaning"].map(normalize_text),
        "id",
    ].tolist()
    if changed:
        log.append(
            f"Applied spelling correction {SPELLING_CORRECTIONS} to "
            f"normalized_historical_meaning only (raw historical_meaning "
            f"left untouched) for id(s): {changed}."
        )

    # search_text = historical_meaning + human_language_meaning + category
    # (normalized versions), per docs/SEARCH_METHODOLOGY.md. Flower name is
    # deliberately excluded -- meaning search should match on documented
    # symbolism, not on the flower's own name.
    out["search_text"] = (
        out["normalized_historical_meaning"]
        + " "
        + out["normalized_human_language_meaning"]
        + " "
        + out["normalized_communication_category"]
    )
    log.append(
        "search_text = normalized_historical_meaning + "
        "normalized_human_language_meaning + normalized_communication_category "
        "(flower name excluded by design)."
    )

    return out, log
