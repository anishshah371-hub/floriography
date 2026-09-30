from pydantic import BaseModel


class SearchResultOut(BaseModel):
    rank: int
    id: int
    flower: str
    historical_meaning: str
    human_language_meaning: str
    communication_category: str
    similarity_score: float
    matched_terms: list[str]
    explanation: str


class MeaningSearchResponse(BaseModel):
    query: str
    method: str
    results: list[SearchResultOut]
    message: str | None = None
