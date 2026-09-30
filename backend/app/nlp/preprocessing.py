"""Text normalization and tokenization shared by keyword_search.py and
tfidf_search.py.

Deliberately simple and undocumented-magic-free (spec section 55):
- lowercase + collapse whitespace, nothing more
- tokenize on word boundaries
- NO stopword removal: short common words ("i", "to", "you") can be
  part of the phrase-level meaning of a short symbolic description,
  and this dataset is small enough that removing them buys nothing.
- NO stemming/lemmatization: keeps every match traceable to an exact
  surface word, which is easier to explain and to debug than a
  stemmed match would be.
Both choices are deliberate trade-offs for a 30-record dataset, not
an oversight -- see docs/SEARCH_METHODOLOGY.md.
"""

from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_text(text: str) -> str:
    """Lowercase + collapse whitespace. Punctuation is left in place
    so it's still visible to a human reading normalized text."""
    return " ".join(str(text).lower().split())


def tokenize(text: str) -> list[str]:
    """Normalize, then split into word tokens (drops punctuation for
    matching purposes only -- normalize_text output is what's stored
    and displayed)."""
    return _TOKEN_RE.findall(normalize_text(text))
