from pydantic import BaseModel


class TextLengthStats(BaseModel):
    min: int
    max: int
    mean: float


class AnalyticsResponse(BaseModel):
    total_records: int
    category_distribution: dict[str, int]
    category_count: int
    text_length_stats: dict[str, TextLengthStats]
