from fastapi import APIRouter

from api.schemas import CitationInput, PredictionResponse
from intencite.predict import predict_citation

router = APIRouter(
    prefix="/api/v1",
    tags=["Prediction"],
)


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(input_data: CitationInput):
    return predict_citation(input_data.context)


@router.get("/models")
def available_models():
    return {
        "models": [
            {
                "id": "tfidf-logreg-baseline-v1",
                "name": "TF-IDF + Logistic Regression",
            }
        ]
    }
