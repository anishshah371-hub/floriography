from pydantic import BaseModel


class FlowerOut(BaseModel):
    id: int
    flower: str
    historical_meaning: str
    human_language_meaning: str
    communication_category: str


class FlowerListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[FlowerOut]
