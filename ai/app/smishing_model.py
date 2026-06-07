import joblib
from huggingface_hub import hf_hub_download

MODEL_REPO = "Hyeonseo/ko-smishing-detector"
MODEL_FILE = "pipeline.pkl"

pipeline = None


def load_smishing_model():
    global pipeline

    if pipeline is None:
        model_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE
        )
        pipeline = joblib.load(model_path)


def predict_smishing(text: str):
    load_smishing_model()

    proba = pipeline.predict_proba([text])[0]

    normal_score = float(proba[0])
    smishing_score = float(proba[1])

    label = "smishing" if smishing_score >= normal_score else "normal"
    confidence = max(smishing_score, normal_score)

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "smishing_score": round(smishing_score, 4),
        "normal_score": round(normal_score, 4),
        "model_name": MODEL_REPO
    }