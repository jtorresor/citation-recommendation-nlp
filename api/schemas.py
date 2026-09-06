from typing import Literal

from pydantic import BaseModel, Field, field_validator

CitationLabel = Literal[
    "Application",
    "Background",
    "Comparison",
    "Gap",
    "Improvement",
]


class CitationInput(BaseModel):
    context: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Citation context text to classify. Must be between 20 and 5000 characters. Minimum 3 words.",
    )

    @field_validator("context")
    @classmethod
    def validate_context(cls, value: str) -> str:
        value = value.strip()

        if len(value.split()) < 3:
            raise ValueError("Citation context must contain at least three words")

        return value


class ClassProbabilities(BaseModel):
    Application: float
    Background: float
    Comparison: float
    Gap: float
    Improvement: float


class PredictionResponse(BaseModel):
    prediction: CitationLabel
    confidence: float
    probabilities: ClassProbabilities
