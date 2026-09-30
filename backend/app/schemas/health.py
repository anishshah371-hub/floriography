"""Pydantic response models for the health-check endpoint."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    message: str
