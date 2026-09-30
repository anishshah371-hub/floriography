"""Plain dataclasses for a flower record.

Deliberately NOT pydantic models -- the database/service/NLP layers
should have no dependency on the web framework, so they can be
imported and unit-tested without FastAPI installed. The API layer
(backend/app/schemas/) converts between this and Pydantic response
models at the edge.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Flower:
    id: int
    flower: str
    historical_meaning: str
    human_language_meaning: str
    communication_category: str
    normalized_flower: str
    normalized_historical_meaning: str
    normalized_human_language_meaning: str
    normalized_communication_category: str
    search_text: str

    @staticmethod
    def from_row(row) -> "Flower":
        return Flower(**{k: row[k] for k in Flower.__dataclass_fields__})

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "flower": self.flower,
            "historical_meaning": self.historical_meaning,
            "human_language_meaning": self.human_language_meaning,
            "communication_category": self.communication_category,
        }
