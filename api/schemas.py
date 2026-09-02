from typing import Literal

from pydantic import BaseModel, Field

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
        min_length=1,
        description="Citation context to classify",
    )


class ClassProbabilities(BaseModel):
    Application: float
    Background: float
    Comparison: float
    Gap: float
    Improvement: float


class PredictionResponse(BaseModel):
    prediction: CitationLabel
    probabilities: ClassProbabilities
