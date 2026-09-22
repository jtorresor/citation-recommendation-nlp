from fastapi import APIRouter, HTTPException

from api.schemas import CitationInput, PredictionResponse
from intencite.predict import predict_citation
from intencite.predict_lora import predict_lora

router = APIRouter(
    prefix="/api/v1",
    tags=["Prediction"],
)


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(input_data: CitationInput):

    if input_data.model == "tfidf-logreg-baseline-v1":
        return predict_citation(input_data.context)

    if input_data.model == "qwen2.5-1.5b-lora-3ctx":
        return predict_lora(input_data.context)

    raise HTTPException(
        status_code=400,
        detail=f"Unknown model: {input_data.model}",
    )


@router.get("/models")
def available_models():
    return {
        "models": [
            {
                "id": "tfidf-logreg-baseline-v1",
                "name": "TF-IDF + Logistic Regression",
            },
            {
                "id": "qwen2.5-1.5b-lora-3ctx",
                "name": "Qwen2.5 1.5B + LoRA",
            },
        ]
    }
