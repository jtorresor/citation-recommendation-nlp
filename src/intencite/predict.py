from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "models" / "tfidf_logreg_baseline_v1.joblib"

# El modelo se carga una sola vez cuando arranca la API.
_model = joblib.load(MODEL_PATH)


def predict_citation(context: str) -> dict:
    prediction = str(_model.predict([context])[0])

    probabilities = _model.predict_proba([context])[0]
    classes = _model.classes_

    probability_dict = {
        str(label): float(probability)
        for label, probability in zip(classes, probabilities)
    }

    return {
        "prediction": prediction,
        "confidence": max(probability_dict.values()),
        "probabilities": probability_dict,
    }
